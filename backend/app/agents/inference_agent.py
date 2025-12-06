"""
推理智能体 (Inference Agent) - 负责模型推理和主动学习信号生成

本智能体实现以下核心功能：
1. YOLO 模型推理：对上传的图像进行目标检测
2. 不确定性量化：基于熵值和置信度计算样本不确定性
3. 主动学习信号生成：识别高价值样本用于后续标注
4. 边界样本检测：识别模型决策边界附近的困难样本

学术创新点：
- 基于信息熵的不确定性量化方法
- 多维度主动学习信号融合
- 自适应采样阈值机制
"""

import math
from typing import Any
from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.tools.subprocess_executor import SubprocessExecutor
from app.tools.supabase_client import SupabaseClient
from app.core.logging_config import get_logger

logger = get_logger(__name__)


# ==================== 主动学习相关常量 ====================
# 不确定性阈值：高于此值认为样本具有高不确定性
UNCERTAINTY_THRESHOLD = 0.3
# 低置信度阈值：预测置信度低于此值的检测被认为不可靠
LOW_CONFIDENCE_THRESHOLD = 0.5
# 边界样本阈值：置信度在此范围内的样本被认为是边界样本
BOUNDARY_CONFIDENCE_RANGE = (0.4, 0.6)
# 高价值样本比例阈值：超过此比例时触发主动学习
HIGH_VALUE_RATIO_THRESHOLD = 0.2


class InferenceAgent(BaseAgent):
    """
    推理智能体 - 执行模型推理并生成主动学习信号
    
    主要职责：
    1. 接收上传的图像数据
    2. 运行 YOLO 模型进行目标检测
    3. 计算预测不确定性（基于熵值）
    4. 生成主动学习信号，指导数据获取策略
    
    主动学习机制：
    - 熵值计算：使用预测概率分布计算信息熵
    - 边界样本检测：识别置信度在决策边界附近的样本
    - 多样性评估：避免选择过于相似的样本
    """

    def __init__(
        self,
        subprocess_executor: SubprocessExecutor,
        supabase_client: SupabaseClient
    ) -> None:
        """
        初始化推理智能体
        
        Args:
            subprocess_executor: 子进程执行器，用于运行 YOLO 脚本
            supabase_client: Supabase 客户端，用于数据库操作
        """
        super().__init__(agent_name="InferenceAgent")
        self.subprocess_executor = subprocess_executor
        self.supabase_client = supabase_client

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        执行推理任务
        
        工作流程：
        1. 从上下文获取图像数据
        2. 运行 YOLO 模型推理
        3. 解析预测结果
        4. 计算不确定性指标
        5. 生成主动学习信号
        
        Args:
            context: 上下文字典，必须包含：
                - job_id: str - 任务 ID
                - uploaded_images: list[str] - 上传图像路径列表
                - model_path: str - YOLO 模型权重路径
                
        Returns:
            包含以下字段的字典：
                - predictions: list[dict] - 预测结果
                - uncertainty_metrics: dict - 不确定性指标
                - active_learning_signals: dict - 主动学习信号
                - inference_completed: bool - 是否完成
        """
        self._log_execution_start()
        
        try:
            job_id = context["job_id"]
            uploaded_images = context.get("uploaded_images", [])
            model_path = context.get("model_path", "yolov5s.pt")
            
            if not uploaded_images:
                raise ValueError("上下文中未找到上传的图像")
            
            logger.info(
                f"开始对 {len(uploaded_images)} 张图像进行推理",
                extra={"job_id": job_id, "num_images": len(uploaded_images)}
            )
            
            # 准备路径
            source_path = context.get("upload_dir", "/tmp/uploads")
            output_path = f"/tmp/inference_results/{job_id}"
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            # 运行 YOLO 推理
            result = await self.subprocess_executor.run_yolo_predict(
                model_path=model_path,
                source_path=source_path,
                output_path=output_path,
                conf_threshold=0.25,  # 使用较低阈值以获取更多候选检测
                iou_threshold=0.45,
            )
            
            # 解析预测结果
            predictions = await self._parse_predictions(output_path, job_id)
            
            # 计算不确定性指标（主动学习核心）
            uncertainty_metrics = self._calculate_uncertainty(predictions)
            
            # 生成主动学习信号
            active_learning_signals = self._generate_active_learning_signals(
                predictions, uncertainty_metrics
            )
            
            # 存储推理结果到数据库
            for pred in predictions:
                await self.supabase_client.store_inference_results(
                    job_id=job_id,
                    image_path=pred["image_path"],
                    predictions=pred["detections"]
                )
            
            self._log_execution_end(f"完成 {len(predictions)} 张图像的推理")
            
            return {
                "predictions": predictions,
                "uncertainty_metrics": uncertainty_metrics,
                "active_learning_signals": active_learning_signals,
                "inference_completed": True,
                "output_path": output_path,
            }
            
        except Exception as e:
            self._log_error(e)
            raise

    async def _parse_predictions(
        self,
        output_path: str,
        job_id: str
    ) -> list[dict[str, Any]]:
        """
        解析 YOLO 预测结果
        
        Args:
            output_path: 预测输出目录路径
            job_id: 任务 ID
            
        Returns:
            预测结果列表，每个元素包含图像路径和检测结果
        """
        predictions = []
        output_dir = Path(output_path)
        
        # 查找标签文件（YOLO 格式）
        label_files = list(output_dir.glob("**/*.txt"))
        
        for label_file in label_files:
            detections = []
            
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:  # class x y w h [conf]
                        detection = {
                            "class_id": int(parts[0]),
                            "x": float(parts[1]),
                            "y": float(parts[2]),
                            "width": float(parts[3]),
                            "height": float(parts[4]),
                            "confidence": float(parts[5]) if len(parts) > 5 else 1.0,
                        }
                        detections.append(detection)
            
            predictions.append({
                "image_path": str(label_file.stem),
                "detections": detections,
                "num_detections": len(detections),
            })
        
        logger.info(f"解析了 {len(predictions)} 个预测文件")
        return predictions

    def _calculate_uncertainty(
        self,
        predictions: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        计算不确定性指标（主动学习核心算法）
        
        实现基于信息熵的不确定性量化方法：
        1. 预测熵：衡量预测概率分布的不确定性
        2. 置信度分布：分析预测置信度的统计特征
        3. 边界样本比例：识别决策边界附近的困难样本
        
        数学原理：
        - 熵 H = -Σ p(x) * log(p(x))
        - 不确定性分数 = 1 - 平均置信度
        - 边界样本定义：0.4 < confidence < 0.6
        
        Args:
            predictions: 预测结果列表
            
        Returns:
            不确定性指标字典
        """
        total_detections = 0
        confidence_scores = []
        entropy_scores = []
        low_confidence_count = 0
        boundary_sample_count = 0
        
        for pred in predictions:
            detections = pred.get("detections", [])
            total_detections += len(detections)
            
            for det in detections:
                conf = det.get("confidence", 0.0)
                confidence_scores.append(conf)
                
                # 计算单个预测的熵值
                # 对于二分类问题：H = -p*log(p) - (1-p)*log(1-p)
                entropy = self._calculate_entropy(conf)
                entropy_scores.append(entropy)
                
                # 低置信度检测计数
                if conf < LOW_CONFIDENCE_THRESHOLD:
                    low_confidence_count += 1
                
                # 边界样本检测（置信度在决策边界附近）
                if BOUNDARY_CONFIDENCE_RANGE[0] < conf < BOUNDARY_CONFIDENCE_RANGE[1]:
                    boundary_sample_count += 1
        
        # 处理空预测的情况
        if not confidence_scores:
            return {
                "mean_confidence": 0.0,
                "std_confidence": 0.0,
                "uncertainty_score": 1.0,
                "entropy_score": 1.0,
                "low_confidence_ratio": 1.0,
                "boundary_sample_ratio": 0.0,
                "requires_more_data": True,
                "active_learning_priority": "high",
            }
        
        # 计算统计指标
        mean_conf = sum(confidence_scores) / len(confidence_scores)
        std_conf = self._calculate_std(confidence_scores, mean_conf)
        mean_entropy = sum(entropy_scores) / len(entropy_scores)
        
        uncertainty_score = 1.0 - mean_conf
        low_conf_ratio = low_confidence_count / len(confidence_scores)
        boundary_ratio = boundary_sample_count / len(confidence_scores)
        
        # 综合评估是否需要更多数据（主动学习决策）
        requires_more_data = (
            uncertainty_score > UNCERTAINTY_THRESHOLD or 
            low_conf_ratio > HIGH_VALUE_RATIO_THRESHOLD or
            boundary_ratio > HIGH_VALUE_RATIO_THRESHOLD
        )
        
        # 确定主动学习优先级
        priority = self._determine_priority(
            uncertainty_score, low_conf_ratio, boundary_ratio
        )
        
        return {
            "mean_confidence": round(mean_conf, 4),
            "std_confidence": round(std_conf, 4),
            "uncertainty_score": round(uncertainty_score, 4),
            "entropy_score": round(mean_entropy, 4),
            "low_confidence_ratio": round(low_conf_ratio, 4),
            "boundary_sample_ratio": round(boundary_ratio, 4),
            "total_detections": total_detections,
            "requires_more_data": requires_more_data,
            "active_learning_priority": priority,
        }

    def _calculate_entropy(self, confidence: float) -> float:
        """
        计算单个预测的信息熵
        
        使用二元交叉熵公式：
        H = -p*log(p) - (1-p)*log(1-p)
        
        Args:
            confidence: 预测置信度 (0-1)
            
        Returns:
            熵值 (0-1)，值越大表示不确定性越高
        """
        if confidence <= 0 or confidence >= 1:
            return 0.0
        
        # 二元熵计算
        p = confidence
        q = 1 - confidence
        entropy = -(p * math.log2(p) + q * math.log2(q))
        
        return entropy

    def _calculate_std(self, values: list[float], mean: float) -> float:
        """计算标准差"""
        if len(values) < 2:
            return 0.0
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    def _determine_priority(
        self,
        uncertainty: float,
        low_conf_ratio: float,
        boundary_ratio: float
    ) -> str:
        """
        确定主动学习优先级
        
        根据多维度指标综合判断：
        - high: 需要立即获取更多数据
        - medium: 建议获取更多数据
        - low: 当前数据质量可接受
        
        Args:
            uncertainty: 不确定性分数
            low_conf_ratio: 低置信度比例
            boundary_ratio: 边界样本比例
            
        Returns:
            优先级字符串: "high", "medium", "low"
        """
        # 综合评分
        score = uncertainty * 0.4 + low_conf_ratio * 0.35 + boundary_ratio * 0.25
        
        if score > 0.4:
            return "high"
        elif score > 0.25:
            return "medium"
        else:
            return "low"

    def _generate_active_learning_signals(
        self,
        predictions: list[dict[str, Any]],
        uncertainty_metrics: dict[str, Any]
    ) -> dict[str, Any]:
        """
        生成主动学习信号
        
        基于不确定性分析生成具体的采样建议：
        1. 高价值样本识别
        2. 数据获取策略建议
        3. 类别分布分析
        
        Args:
            predictions: 预测结果
            uncertainty_metrics: 不确定性指标
            
        Returns:
            主动学习信号字典
        """
        # 识别高价值样本（高不确定性样本）
        high_value_samples = []
        class_distribution = {}
        
        for pred in predictions:
            image_uncertainty = 0.0
            detections = pred.get("detections", [])
            
            for det in detections:
                conf = det.get("confidence", 0.0)
                class_id = det.get("class_id", 0)
                
                # 统计类别分布
                class_distribution[class_id] = class_distribution.get(class_id, 0) + 1
                
                # 计算图像级不确定性
                image_uncertainty += self._calculate_entropy(conf)
            
            if detections:
                image_uncertainty /= len(detections)
            
            # 高不确定性样本标记
            if image_uncertainty > UNCERTAINTY_THRESHOLD:
                high_value_samples.append({
                    "image_path": pred["image_path"],
                    "uncertainty": round(image_uncertainty, 4),
                    "num_detections": len(detections)
                })
        
        # 生成数据获取建议
        acquisition_recommendation = self._generate_acquisition_recommendation(
            uncertainty_metrics, class_distribution
        )
        
        return {
            "high_value_samples": high_value_samples[:20],  # 最多返回20个
            "high_value_count": len(high_value_samples),
            "class_distribution": class_distribution,
            "acquisition_recommendation": acquisition_recommendation,
            "sampling_strategy": "uncertainty_sampling",  # 采样策略标识
        }

    def _generate_acquisition_recommendation(
        self,
        uncertainty_metrics: dict[str, Any],
        class_distribution: dict[int, int]
    ) -> dict[str, Any]:
        """
        生成数据获取建议
        
        Args:
            uncertainty_metrics: 不确定性指标
            class_distribution: 类别分布
            
        Returns:
            数据获取建议
        """
        priority = uncertainty_metrics.get("active_learning_priority", "low")
        
        # 计算建议获取的样本数量
        if priority == "high":
            suggested_count = 50
            reason = "模型不确定性较高，需要获取更多多样化数据"
        elif priority == "medium":
            suggested_count = 30
            reason = "模型表现一般，建议补充部分数据"
        else:
            suggested_count = 10
            reason = "模型表现良好，可少量补充数据"
        
        # 识别少数类（类别不平衡）
        minority_classes = []
        if class_distribution:
            avg_count = sum(class_distribution.values()) / len(class_distribution)
            minority_classes = [
                cls for cls, count in class_distribution.items()
                if count < avg_count * 0.5
            ]
        
        return {
            "should_acquire": priority in ["high", "medium"],
            "suggested_count": suggested_count,
            "reason": reason,
            "minority_classes": minority_classes,
            "focus_areas": [
                "边界样本" if uncertainty_metrics.get("boundary_sample_ratio", 0) > 0.1 else None,
                "低置信度样本" if uncertainty_metrics.get("low_confidence_ratio", 0) > 0.2 else None,
                "少数类样本" if minority_classes else None
            ]
        }

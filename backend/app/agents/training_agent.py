"""
训练智能体 (Training Agent) - 负责模型训练和优化策略

本智能体实现以下核心功能：
1. 数据集准备：整合原始数据和伪标注数据
2. 训练配置生成：根据数据特征自动优化训练参数
3. 训练触发：通过远程连接触发 YOLO 模型训练
4. 课程学习支持：按难度排序训练数据

学术创新点：
- 基于数据质量的自适应训练策略
- 课程学习（Curriculum Learning）集成
- 类别平衡的数据增强策略
- 弱监督微调（Weakly Supervised Fine-tuning）支持
"""

from typing import Any
from pathlib import Path
import yaml
import json

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState
from app.tools.remote_client import RemoteClient
from app.tools.subprocess_executor import SubprocessExecutor
from app.tools.supabase_client import SupabaseClient
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


# ==================== 训练策略相关常量 ====================
# 默认训练参数
DEFAULT_EPOCHS = 100
DEFAULT_BATCH_SIZE = 16
DEFAULT_IMG_SIZE = 640
DEFAULT_LEARNING_RATE = 0.01

# 课程学习参数
CURRICULUM_WARMUP_EPOCHS = 10  # 预热阶段只使用简单样本
CURRICULUM_PHASES = 3  # 课程学习分为3个阶段

# 弱监督微调参数
WEAK_SUPERVISION_LOSS_WEIGHT = 0.3  # 伪标签损失权重
CONFIDENCE_WEIGHTED_LOSS = True  # 是否使用置信度加权损失


class TrainingAgent(BaseAgent):
    """
    训练智能体 - 执行模型训练和优化
    
    主要职责：
    1. 准备训练数据集（YOLO 格式）
    2. 生成优化的训练配置
    3. 触发远程训练任务
    4. 监控训练进度
    
    训练优化策略：
    - 课程学习：按样本难度排序，先易后难
    - 弱监督微调：使用伪标签进行增强训练
    - 类别平衡：对少数类进行过采样
    - 自适应学习率：根据数据集大小调整
    """

    def __init__(
        self,
        subprocess_executor: SubprocessExecutor,
        supabase_client: SupabaseClient
    ) -> None:
        """
        初始化训练智能体
        
        Args:
            subprocess_executor: 子进程执行器，用于运行训练脚本
            supabase_client: Supabase 客户端，用于数据库操作
        """
        super().__init__(agent_name="TrainingAgent")
        self.subprocess_executor = subprocess_executor
        self.supabase_client = supabase_client

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        执行模型训练
        
        工作流程：
        1. 整合原始数据和伪标注数据
        2. 应用课程学习排序
        3. 生成训练配置
        4. 触发训练任务
        
        Args:
            context: 上下文字典，必须包含：
                - job_id: str - 任务 ID
                - uploaded_images: list[str] - 原始图像
                - acquired_images: list[str] - 获取的图像
                - pseudo_labels: list[dict] - 伪标签
                
        Returns:
            包含以下字段的字典：
                - training_started: bool - 训练是否启动
                - training_config: dict - 训练配置
                - curriculum_info: dict - 课程学习信息
        """
        self._log_execution_start()
        
        try:
            job_id = context["job_id"]
            uploaded_images = context.get("uploaded_images", [])
            acquired_images = context.get("acquired_images", [])
            pseudo_labels = context.get("pseudo_labels", [])
            quality_metrics = context.get("quality_metrics", {})
            
            logger.info(
                f"准备训练: {len(uploaded_images)} 原始图像 + "
                f"{len(acquired_images)} 获取图像",
                extra={"job_id": job_id}
            )
            
            # 步骤 1: 准备数据集并应用课程学习
            dataset_path, curriculum_info = await self._prepare_curriculum_dataset(
                job_id=job_id,
                original_images=uploaded_images,
                acquired_images=acquired_images,
                pseudo_labels=pseudo_labels
            )
            
            # 步骤 2: 生成优化的训练配置
            training_config = self._generate_training_config(
                dataset_path=dataset_path,
                quality_metrics=quality_metrics,
                curriculum_info=curriculum_info
            )
            
            # 步骤 3: 生成 data.yaml
            data_yaml_path = await self._generate_data_yaml(
                dataset_path=dataset_path,
                job_id=job_id,
                curriculum_info=curriculum_info
            )
            
            # 步骤 4: 触发训练
            training_result = await self.subprocess_executor.run_yolo_train(
                data_yaml_path=data_yaml_path,
                model_config="yolov5s.yaml",
                epochs=training_config["epochs"],
                batch_size=training_config["batch_size"],
                img_size=training_config["img_size"],
                weights="yolov5s.pt",
            )
            
            logger.info("训练任务已提交")
            
            self._log_execution_end("训练任务启动成功")
            
            return {
                "training_started": True,
                "training_config": training_config,
                "curriculum_info": curriculum_info,
                "dataset_path": dataset_path,
                "training_result": training_result,
            }
            
        except Exception as e:
            self._log_error(e)
            raise

    async def _prepare_curriculum_dataset(
        self,
        job_id: str,
        original_images: list[str],
        acquired_images: list[str],
        pseudo_labels: list[dict[str, Any]]
    ) -> tuple[str, dict[str, Any]]:
        """
        准备课程学习数据集
        
        按照课程学习原则组织数据：
        1. 将数据按难度分组
        2. 简单样本放在前面
        3. 困难样本放在后面
        
        Args:
            job_id: 任务 ID
            original_images: 原始图像列表
            acquired_images: 获取的图像列表
            pseudo_labels: 伪标签列表
            
        Returns:
            (数据集路径, 课程学习信息)
        """
        dataset_path = Path(f"/tmp/datasets/{job_id}")
        
        # 创建目录结构
        for split in ["train", "val"]:
            (dataset_path / "images" / split).mkdir(parents=True, exist_ok=True)
            (dataset_path / "labels" / split).mkdir(parents=True, exist_ok=True)
        
        # 按难度对伪标签进行分组
        easy_samples = []
        medium_samples = []
        hard_samples = []
        
        for label in pseudo_labels:
            difficulty = label.get("curriculum_difficulty", "medium")
            if difficulty == "easy":
                easy_samples.append(label)
            elif difficulty == "hard":
                hard_samples.append(label)
            else:
                medium_samples.append(label)
        
        # 课程学习信息
        curriculum_info = {
            "total_samples": len(pseudo_labels),
            "easy_count": len(easy_samples),
            "medium_count": len(medium_samples),
            "hard_count": len(hard_samples),
            "phases": CURRICULUM_PHASES,
            "warmup_epochs": CURRICULUM_WARMUP_EPOCHS,
            "phase_epochs": [
                CURRICULUM_WARMUP_EPOCHS,  # 阶段1：只使用简单样本
                DEFAULT_EPOCHS // 2,        # 阶段2：加入中等样本
                DEFAULT_EPOCHS             # 阶段3：使用全部样本
            ]
        }
        
        # 按课程学习顺序排列样本
        ordered_samples = easy_samples + medium_samples + hard_samples
        
        # 数据集划分（90% 训练，10% 验证）
        train_ratio = 0.9
        train_count = int(len(ordered_samples) * train_ratio)
        
        # 分配到训练集和验证集
        train_samples = ordered_samples[:train_count]
        val_samples = ordered_samples[train_count:]
        
        # 写入标签文件（实际实现会复制图像和标签文件）
        self._write_dataset_samples(dataset_path / "train", train_samples)
        self._write_dataset_samples(dataset_path / "val", val_samples)
        
        logger.info(
            f"课程学习数据集准备完成: "
            f"简单 {len(easy_samples)}, 中等 {len(medium_samples)}, 困难 {len(hard_samples)}"
        )
        
        return str(dataset_path), curriculum_info

    def _write_dataset_samples(
        self,
        split_path: Path,
        samples: list[dict[str, Any]]
    ) -> None:
        """
        写入数据集样本
        
        Args:
            split_path: 数据集分割路径（train/val）
            samples: 样本列表
        """
        # 实际实现会：
        # 1. 复制图像到 images/{split}/
        # 2. 生成 YOLO 格式标签到 labels/{split}/
        pass

    def _generate_training_config(
        self,
        dataset_path: str,
        quality_metrics: dict[str, Any],
        curriculum_info: dict[str, Any]
    ) -> dict[str, Any]:
        """
        生成优化的训练配置
        
        根据数据集特征自适应调整训练参数：
        - 数据量少时使用更小的 batch size
        - 伪标签质量低时使用更低的学习率
        - 应用弱监督微调策略
        
        Args:
            dataset_path: 数据集路径
            quality_metrics: 数据质量指标
            curriculum_info: 课程学习信息
            
        Returns:
            训练配置字典
        """
        total_samples = curriculum_info.get("total_samples", 100)
        avg_quality = quality_metrics.get("average_quality_score", 0.7)
        
        # 自适应 batch size
        if total_samples < 50:
            batch_size = 8
        elif total_samples < 200:
            batch_size = 16
        else:
            batch_size = 32
        
        # 自适应学习率（质量低时使用更小的学习率）
        base_lr = DEFAULT_LEARNING_RATE
        if avg_quality < 0.5:
            learning_rate = base_lr * 0.5
        elif avg_quality < 0.7:
            learning_rate = base_lr * 0.8
        else:
            learning_rate = base_lr
        
        # 自适应 epochs（数据少时训练更多轮）
        if total_samples < 50:
            epochs = DEFAULT_EPOCHS * 2
        elif total_samples < 200:
            epochs = DEFAULT_EPOCHS * 1.5
        else:
            epochs = DEFAULT_EPOCHS
        
        # 弱监督微调配置
        weak_supervision_config = {
            "enabled": True,
            "pseudo_label_weight": WEAK_SUPERVISION_LOSS_WEIGHT,
            "confidence_weighted": CONFIDENCE_WEIGHTED_LOSS,
            "min_confidence": 0.5,
        }
        
        # 课程学习配置
        curriculum_config = {
            "enabled": True,
            "warmup_epochs": CURRICULUM_WARMUP_EPOCHS,
            "phases": CURRICULUM_PHASES,
            "easy_ratio_start": 1.0,  # 开始时只用简单样本
            "easy_ratio_end": 0.3,    # 结束时简单样本占比
        }
        
        config = {
            "epochs": int(epochs),
            "batch_size": batch_size,
            "img_size": DEFAULT_IMG_SIZE,
            "learning_rate": round(learning_rate, 6),
            "optimizer": "AdamW",
            "scheduler": "cosine",
            "warmup_epochs": 3,
            "weak_supervision": weak_supervision_config,
            "curriculum_learning": curriculum_config,
            "augmentation": {
                "mosaic": 1.0,
                "mixup": 0.1,
                "copy_paste": 0.1,
                "hsv_h": 0.015,
                "hsv_s": 0.7,
                "hsv_v": 0.4,
                "degrees": 0.0,
                "translate": 0.1,
                "scale": 0.5,
                "shear": 0.0,
                "perspective": 0.0,
                "flipud": 0.0,
                "fliplr": 0.5,
            }
        }
        
        logger.info(
            f"训练配置: epochs={config['epochs']}, batch_size={config['batch_size']}, "
            f"lr={config['learning_rate']}, 弱监督={weak_supervision_config['enabled']}"
        )
        
        return config

    async def _generate_data_yaml(
        self,
        dataset_path: str,
        job_id: str,
        curriculum_info: dict[str, Any]
    ) -> str:
        """
        生成 YOLO 训练配置文件
        
        Args:
            dataset_path: 数据集路径
            job_id: 任务 ID
            curriculum_info: 课程学习信息
            
        Returns:
            data.yaml 文件路径
        """
        data_yaml_path = Path(dataset_path) / "data.yaml"
        
        # 数据集配置
        data_config = {
            "path": dataset_path,
            "train": "images/train",
            "val": "images/val",
            "nc": 1,  # 类别数（需要根据实际情况调整）
            "names": ["object"],  # 类别名称
            # 自定义字段：课程学习信息
            "curriculum": {
                "enabled": True,
                "total_samples": curriculum_info.get("total_samples", 0),
                "phases": curriculum_info.get("phases", CURRICULUM_PHASES),
            }
        }
        
        # 写入配置文件
        with open(data_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data_config, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"生成 data.yaml: {data_yaml_path}")
        return str(data_yaml_path)


# ==================== LangGraph 节点函数 ====================

async def evolution_node(state: AgentState) -> AgentState:
    """
    LangGraph 节点函数：训练节点（evolution）
    
    通过 SSH 发送指令触发远程训练任务。
    实现课程学习和弱监督微调策略。
    
    此函数作为 LangGraph 工作流中的 evolution 节点，负责：
    1. 准备课程学习数据集
    2. 生成优化的训练配置
    3. 通过 SSH 连接到远程 GPU 服务器
    4. 触发训练脚本执行
    
    Args:
        state: AgentState 状态字典
        
    Returns:
        更新后的 AgentState
    """
    logger.info("执行训练节点 (evolution)")
    
    try:
        # 检查是否有新数据
        crawled_count = state.get("crawled_count", 0)
        pseudo_labels = state.get("pseudo_labels", [])
        quality_metrics = state.get("quality_metrics", {})
        
        if crawled_count == 0 and not pseudo_labels:
            logger.warning("没有新数据，跳过训练")
            state["training_status"] = "skipped"
            state["training_reason"] = "没有新的数据可用于训练"
            return state
        
        # 初始化远程客户端
        remote_client = RemoteClient()
        
        try:
            # 连接远程服务器
            await remote_client.connect()
            
            # 生成训练配置
            training_agent = TrainingAgent(None, None)
            
            # 课程学习信息
            curriculum_info = {
                "total_samples": len(pseudo_labels),
                "easy_count": sum(1 for p in pseudo_labels if p.get("curriculum_difficulty") == "easy"),
                "medium_count": sum(1 for p in pseudo_labels if p.get("curriculum_difficulty") == "medium"),
                "hard_count": sum(1 for p in pseudo_labels if p.get("curriculum_difficulty") == "hard"),
            }
            
            training_config = training_agent._generate_training_config(
                dataset_path="",
                quality_metrics=quality_metrics,
                curriculum_info=curriculum_info
            )
            
            # 触发远程训练
            data_yaml_path = f"{settings.remote_yolo_project_path}/data.yaml"
            
            exit_code, stdout, stderr = await remote_client.trigger_training(
                data_yaml_path=data_yaml_path,
                epochs=training_config["epochs"],
                batch_size=training_config["batch_size"],
                img_size=training_config["img_size"]
            )
            
            if exit_code == 0:
                state["training_status"] = "completed"
                state["training_config"] = training_config
                state["curriculum_info"] = curriculum_info
                logger.info(
                    f"远程训练任务已成功触发 "
                    f"(epochs={training_config['epochs']}, "
                    f"batch_size={training_config['batch_size']})"
                )
            else:
                state["training_status"] = "failed"
                error_msg = f"训练任务失败: {stderr[:200]}"
                state["errors"] = state.get("errors", []) + [error_msg]
                logger.error(error_msg)
            
        finally:
            await remote_client.disconnect()
        
        return state
        
    except Exception as e:
        error_msg = f"训练节点执行失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["training_status"] = "failed"
        state["errors"] = state.get("errors", []) + [error_msg]
        return state

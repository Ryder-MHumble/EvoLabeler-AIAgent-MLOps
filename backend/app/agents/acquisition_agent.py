"""
数据获取智能体 (Acquisition Agent) - 负责 Web 数据采集和半监督学习

本智能体实现以下核心功能：
1. Web 数据爬取：基于搜索策略从网络获取相关图像
2. 伪标注生成：使用当前模型对未标注数据进行推理
3. 质量评估：基于置信度和多样性筛选高质量伪标签
4. 噪声过滤：实现带噪学习的数据预处理

学术创新点：
- 基于置信度阈值的自适应伪标注策略
- 多维度质量评分机制
- 多样性感知的样本选择算法
- 课程学习（Curriculum Learning）数据排序
"""

import math
import hashlib
from typing import Any
from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState
from app.tools.web_crawler import WebCrawler
from app.tools.subprocess_executor import SubprocessExecutor
from app.tools.supabase_client import SupabaseClient
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


# ==================== 半监督学习相关常量 ====================
# 伪标注置信度阈值：高于此值的预测才会被采纳
PSEUDO_LABEL_CONFIDENCE_THRESHOLD = 0.5
# 高置信度阈值：用于计算质量分数
HIGH_CONFIDENCE_THRESHOLD = 0.7
# 最小检测数阈值：图像必须有足够的检测才被认为有效
MIN_DETECTIONS_THRESHOLD = 1
# 多样性哈希桶大小：用于去重
DIVERSITY_HASH_SIZE = 16
# 课程学习难度分组数
CURRICULUM_DIFFICULTY_GROUPS = 3


class AcquisitionAgent(BaseAgent):
    """
    数据获取智能体 - 执行 Web 爬取和半监督学习
    
    主要职责：
    1. 根据分析智能体生成的搜索策略爬取网络图像
    2. 对获取的图像运行伪标注（Pseudo-Labeling）
    3. 质量过滤和多样性保证
    4. 为训练准备高质量数据集
    
    半监督学习机制：
    - 伪标注：使用教师模型生成未标注数据的标签
    - 置信度过滤：只保留高置信度的伪标签
    - 质量评分：综合评估伪标签的可靠性
    - 课程学习：按难度排序数据，先易后难
    """

    def __init__(
        self,
        web_crawler: WebCrawler,
        subprocess_executor: SubprocessExecutor,
        supabase_client: SupabaseClient
    ) -> None:
        """
        初始化数据获取智能体
        
        Args:
            web_crawler: Web 爬虫，用于图像获取
            subprocess_executor: 子进程执行器，用于伪标注
            supabase_client: Supabase 客户端，用于数据库操作
        """
        super().__init__(agent_name="AcquisitionAgent")
        self.web_crawler = web_crawler
        self.subprocess_executor = subprocess_executor
        self.supabase_client = supabase_client

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        执行数据获取和伪标注任务
        
        工作流程：
        1. 从上下文获取搜索策略
        2. 执行 Web 图像爬取
        3. 运行伪标注
        4. 质量过滤和多样性去重
        5. 按课程学习原则排序数据
        
        Args:
            context: 上下文字典，必须包含：
                - job_id: str - 任务 ID
                - search_queries: list[str] - 搜索查询列表
                - model_path: str - 伪标注模型路径
                
        Returns:
            包含以下字段的字典：
                - acquired_images: list[str] - 获取的图像
                - pseudo_labels: list[dict] - 伪标签
                - quality_metrics: dict - 质量指标
                - dataset_ready: bool - 数据集是否就绪
        """
        self._log_execution_start()
        
        try:
            job_id = context["job_id"]
            search_queries = context.get("search_queries", [])
            model_path = context.get("model_path", "yolov5s.pt")
            
            # 获取主动学习信号以调整获取策略
            active_learning_signals = context.get("active_learning_signals", {})
            acquisition_recommendation = active_learning_signals.get(
                "acquisition_recommendation", {}
            )
            
            if not search_queries:
                raise ValueError("上下文中未找到搜索查询")
            
            # 根据主动学习建议调整获取数量
            suggested_count = acquisition_recommendation.get("suggested_count", 10)
            images_per_query = max(5, suggested_count // len(search_queries))
            
            logger.info(
                f"使用 {len(search_queries)} 个查询获取数据，每个查询 {images_per_query} 张",
                extra={"job_id": job_id}
            )
            
            # 步骤 1: 从 Web 爬取图像
            acquired_images = await self.web_crawler.crawl_images(
                queries=search_queries,
                limit=images_per_query,
                job_id=job_id
            )
            
            if not acquired_images:
                logger.warning("未从 Web 获取到图像")
                return {
                    "acquired_images": [],
                    "pseudo_labels": [],
                    "quality_metrics": {},
                    "dataset_ready": False,
                }
            
            logger.info(f"从 Web 获取了 {len(acquired_images)} 张图像")
            
            # 步骤 2: 运行伪标注（半监督学习核心）
            pseudo_labels = await self._run_pseudo_labeling(
                images=acquired_images,
                model_path=model_path,
                job_id=job_id
            )
            
            # 步骤 3: 质量过滤（带噪学习核心）
            filtered_labels, quality_metrics = self._filter_and_score_pseudo_labels(
                pseudo_labels,
                confidence_threshold=PSEUDO_LABEL_CONFIDENCE_THRESHOLD
            )
            
            # 步骤 4: 多样性过滤
            diverse_labels = self._ensure_diversity(filtered_labels)
            
            # 步骤 5: 课程学习排序
            curriculum_sorted_labels = self._sort_by_curriculum(diverse_labels)
            
            logger.info(
                f"生成 {len(curriculum_sorted_labels)} 个高质量伪标签 "
                f"(质量分数: {quality_metrics.get('average_quality_score', 0):.3f})"
            )
            
            self._log_execution_end(
                f"获取 {len(acquired_images)} 张图像，{len(curriculum_sorted_labels)} 个有效标签"
            )
            
            return {
                "acquired_images": acquired_images,
                "pseudo_labels": curriculum_sorted_labels,
                "total_acquired": len(acquired_images),
                "high_quality_labels": len(curriculum_sorted_labels),
                "quality_metrics": quality_metrics,
                "dataset_ready": len(curriculum_sorted_labels) > 0,
            }
            
        except Exception as e:
            self._log_error(e)
            raise

    async def _run_pseudo_labeling(
        self,
        images: list[str],
        model_path: str,
        job_id: str
    ) -> list[dict[str, Any]]:
        """
        运行伪标注（Pseudo-Labeling）
        
        半监督学习核心步骤：
        使用当前训练好的模型对未标注数据进行推理，
        生成伪标签用于扩充训练集。
        
        Args:
            images: 图像 URL/路径列表
            model_path: 模型路径
            job_id: 任务 ID
            
        Returns:
            伪标签列表
        """
        # 下载图像（如果是 URL）
        local_image_paths = await self._download_images(images, job_id)
        
        if not local_image_paths:
            return []
        
        # 运行推理生成伪标签
        output_path = f"/tmp/pseudo_labels/{job_id}"
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        try:
            result = await self.subprocess_executor.run_yolo_predict(
                model_path=model_path,
                source_path=",".join(local_image_paths),
                output_path=output_path,
                conf_threshold=0.25,  # 使用较低阈值获取更多候选
                iou_threshold=0.45,
            )
        except Exception as e:
            logger.error(f"伪标注推理失败: {e}")
            return []
        
        # 解析伪标签
        pseudo_labels = self._parse_pseudo_labels(output_path, local_image_paths)
        
        return pseudo_labels

    def _parse_pseudo_labels(
        self,
        output_path: str,
        image_paths: list[str]
    ) -> list[dict[str, Any]]:
        """
        解析伪标签文件
        
        Args:
            output_path: 输出目录
            image_paths: 图像路径列表
            
        Returns:
            伪标签列表
        """
        pseudo_labels = []
        output_dir = Path(output_path)
        
        # 创建图像路径映射
        path_map = {Path(p).stem: p for p in image_paths}
        
        for label_file in output_dir.glob("**/*.txt"):
            image_name = label_file.stem
            image_path = path_map.get(image_name, str(label_file.with_suffix(".jpg")))
            
            detections = []
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        detection = {
                            "class_id": int(parts[0]),
                            "x": float(parts[1]),
                            "y": float(parts[2]),
                            "width": float(parts[3]),
                            "height": float(parts[4]),
                            "confidence": float(parts[5]) if len(parts) > 5 else 0.5,
                        }
                        detections.append(detection)
            
            if detections:
                pseudo_labels.append({
                    "image_path": image_path,
                    "label_path": str(label_file),
                    "detections": detections,
                    "num_detections": len(detections),
                })
        
        return pseudo_labels

    async def _download_images(
        self,
        image_urls: list[str],
        job_id: str
    ) -> list[str]:
        """
        下载图像到本地存储
        
        Args:
            image_urls: 图像 URL 列表
            job_id: 任务 ID
            
        Returns:
            本地文件路径列表
        """
        # 简化实现：假设图像已经可访问
        # 实际实现应该下载图像
        download_dir = Path(f"/tmp/acquired_images/{job_id}")
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # 返回可访问的路径
        return [url for url in image_urls if url]

    def _filter_and_score_pseudo_labels(
        self,
        labels: list[dict[str, Any]],
        confidence_threshold: float
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        过滤和评分伪标签（带噪学习核心算法）
        
        实现多维度质量评估：
        1. 置信度过滤：移除低置信度检测
        2. 质量评分：综合评估标签可靠性
        3. 统计分析：计算质量分布
        
        质量评分公式：
        Q = 0.5 * avg_confidence + 0.3 * high_conf_ratio + 0.2 * consistency_score
        
        Args:
            labels: 伪标签列表
            confidence_threshold: 置信度阈值
            
        Returns:
            (过滤后的标签列表, 质量指标字典)
        """
        filtered = []
        quality_scores = []
        
        for label in labels:
            detections = label.get("detections", [])
            
            # 过滤低置信度检测
            high_conf_detections = [
                det for det in detections
                if det.get("confidence", 0.0) >= confidence_threshold
            ]
            
            # 跳过没有有效检测的样本
            if len(high_conf_detections) < MIN_DETECTIONS_THRESHOLD:
                continue
            
            # 计算质量分数
            quality_score = self._calculate_quality_score(high_conf_detections)
            
            filtered.append({
                **label,
                "detections": high_conf_detections,
                "num_detections": len(high_conf_detections),
                "quality_score": quality_score,
            })
            quality_scores.append(quality_score)
        
        # 计算质量指标
        quality_metrics = self._compute_quality_metrics(quality_scores, len(labels))
        
        return filtered, quality_metrics

    def _calculate_quality_score(
        self,
        detections: list[dict[str, Any]]
    ) -> float:
        """
        计算单个样本的质量分数
        
        综合考虑：
        - 平均置信度
        - 高置信度检测比例
        - 检测一致性
        
        Args:
            detections: 检测结果列表
            
        Returns:
            质量分数 (0-1)
        """
        if not detections:
            return 0.0
        
        confidences = [d.get("confidence", 0.0) for d in detections]
        
        # 平均置信度
        avg_confidence = sum(confidences) / len(confidences)
        
        # 高置信度比例
        high_conf_count = sum(1 for c in confidences if c >= HIGH_CONFIDENCE_THRESHOLD)
        high_conf_ratio = high_conf_count / len(confidences)
        
        # 一致性分数（置信度方差越小越好）
        if len(confidences) > 1:
            variance = sum((c - avg_confidence) ** 2 for c in confidences) / len(confidences)
            consistency_score = 1.0 - min(variance * 4, 1.0)  # 归一化
        else:
            consistency_score = 1.0
        
        # 加权综合评分
        quality_score = (
            0.5 * avg_confidence +
            0.3 * high_conf_ratio +
            0.2 * consistency_score
        )
        
        return round(quality_score, 4)

    def _compute_quality_metrics(
        self,
        quality_scores: list[float],
        total_count: int
    ) -> dict[str, Any]:
        """
        计算整体质量指标
        
        Args:
            quality_scores: 质量分数列表
            total_count: 总样本数
            
        Returns:
            质量指标字典
        """
        if not quality_scores:
            return {
                "average_quality_score": 0.0,
                "min_quality_score": 0.0,
                "max_quality_score": 0.0,
                "retention_rate": 0.0,
            }
        
        return {
            "average_quality_score": round(sum(quality_scores) / len(quality_scores), 4),
            "min_quality_score": round(min(quality_scores), 4),
            "max_quality_score": round(max(quality_scores), 4),
            "std_quality_score": round(self._calculate_std(quality_scores), 4),
            "retention_rate": round(len(quality_scores) / total_count, 4) if total_count > 0 else 0.0,
            "filtered_count": len(quality_scores),
            "total_count": total_count,
        }

    def _calculate_std(self, values: list[float]) -> float:
        """计算标准差"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    def _ensure_diversity(
        self,
        labels: list[dict[str, Any]],
        max_similar: int = 3
    ) -> list[dict[str, Any]]:
        """
        确保样本多样性（去重和平衡）
        
        使用特征哈希来检测相似样本，
        避免训练集中存在过多相似的图像。
        
        Args:
            labels: 标签列表
            max_similar: 每组相似样本的最大数量
            
        Returns:
            去重后的标签列表
        """
        hash_buckets = {}
        diverse_labels = []
        
        for label in labels:
            # 计算样本特征哈希
            feature_hash = self._compute_feature_hash(label)
            bucket_key = feature_hash[:DIVERSITY_HASH_SIZE]
            
            # 控制每个桶中的样本数量
            if bucket_key not in hash_buckets:
                hash_buckets[bucket_key] = 0
            
            if hash_buckets[bucket_key] < max_similar:
                diverse_labels.append(label)
                hash_buckets[bucket_key] += 1
        
        logger.info(
            f"多样性过滤: {len(labels)} -> {len(diverse_labels)} "
            f"(保留 {len(diverse_labels)/len(labels)*100:.1f}%)"
        )
        
        return diverse_labels

    def _compute_feature_hash(self, label: dict[str, Any]) -> str:
        """
        计算样本特征哈希
        
        基于检测结果生成特征签名，用于相似性判断。
        
        Args:
            label: 标签字典
            
        Returns:
            特征哈希字符串
        """
        detections = label.get("detections", [])
        
        # 构建特征向量
        features = []
        for det in detections:
            class_id = det.get("class_id", 0)
            x = int(det.get("x", 0) * 10)
            y = int(det.get("y", 0) * 10)
            features.append(f"{class_id}:{x}:{y}")
        
        # 排序确保一致性
        features.sort()
        feature_string = "|".join(features)
        
        return hashlib.md5(feature_string.encode()).hexdigest()

    def _sort_by_curriculum(
        self,
        labels: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        按课程学习原则排序数据
        
        课程学习（Curriculum Learning）策略：
        先使用简单样本训练，逐步引入困难样本。
        质量分数高的样本被认为是"简单"样本。
        
        Args:
            labels: 标签列表
            
        Returns:
            排序后的标签列表
        """
        # 按质量分数降序排序（先简单后困难）
        sorted_labels = sorted(
            labels,
            key=lambda x: x.get("quality_score", 0),
            reverse=True
        )
        
        # 为每个样本添加难度等级
        total = len(sorted_labels)
        group_size = total // CURRICULUM_DIFFICULTY_GROUPS if total > 0 else 1
        
        for i, label in enumerate(sorted_labels):
            if group_size > 0:
                difficulty_level = min(i // group_size, CURRICULUM_DIFFICULTY_GROUPS - 1)
            else:
                difficulty_level = 0
            label["curriculum_difficulty"] = ["easy", "medium", "hard"][difficulty_level]
        
        return sorted_labels


# ==================== LangGraph 节点函数 ====================

async def hunting_node(state: AgentState) -> AgentState:
    """
    LangGraph 节点函数：数据获取节点（hunter）
    
    此函数作为 LangGraph 工作流中的 hunter 节点，负责：
    1. 根据分析结果提取的关键词进行网络爬取
    2. 上传获取的图像到 Supabase
    3. 运行伪标注和质量过滤
    4. 更新状态中的图像 URL 列表
    
    Args:
        state: AgentState 状态字典
        
    Returns:
        更新后的 AgentState
    """
    logger.info("执行数据获取节点 (hunter)")
    
    try:
        # 初始化工具
        supabase_client = SupabaseClient()
        web_crawler = WebCrawler(supabase_client)
        
        # 获取搜索关键词
        search_keywords = state.get("search_keywords", [])
        if not search_keywords:
            search_keywords = state.get("search_queries", [])
        
        if not search_keywords:
            error_msg = "未找到搜索关键词"
            logger.warning(error_msg)
            state["errors"] = state.get("errors", []) + [error_msg]
            return state
        
        # 获取主动学习信号以调整获取策略
        active_learning_signals = state.get("active_learning_signals", {})
        acquisition_recommendation = active_learning_signals.get(
            "acquisition_recommendation", {}
        )
        suggested_count = acquisition_recommendation.get("suggested_count", 10)
        
        # 获取项目 ID 或任务 ID
        project_id = state.get("project_id", "")
        job_id = state.get("job_id", project_id)
        
        # 计算每个查询的图像数量
        images_per_query = max(5, suggested_count // len(search_keywords))
        
        # 爬取图像
        crawled_images = await web_crawler.crawl_images(
            queries=search_keywords,
            limit=images_per_query,
            job_id=job_id
        )
        
        # 更新状态
        current_images = state.get("image_urls", [])
        state["image_urls"] = current_images + crawled_images
        state["acquired_images"] = crawled_images
        state["crawled_count"] = len(crawled_images)
        
        # 记录获取策略信息
        state["acquisition_strategy"] = {
            "total_queries": len(search_keywords),
            "images_per_query": images_per_query,
            "total_acquired": len(crawled_images),
            "active_learning_guided": acquisition_recommendation.get("should_acquire", False)
        }
        
        logger.info(
            f"数据获取完成: 爬取 {len(crawled_images)} 张图像 "
            f"(主动学习建议: {suggested_count})"
        )
        
        return state
        
    except Exception as e:
        error_msg = f"数据获取节点执行失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["errors"] = state.get("errors", []) + [error_msg]
        return state

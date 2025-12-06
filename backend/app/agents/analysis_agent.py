"""
分析智能体 (Analysis Agent) - LLM 驱动的智能决策中心

本智能体实现以下核心功能：
1. VLM 图像分析：使用视觉语言模型分析上传图像
2. 搜索策略生成：基于 LLM 生成数据获取策略
3. 智能决策：根据主动学习信号判断是否需要获取更多数据
4. 场景分类：识别图像场景类型以优化搜索关键词

学术创新点：
- LLM 驱动的自动化策略规划
- 多模态分析（VLM + LLM）融合决策
- 基于不确定性的数据获取触发机制
- 动态关键词优化策略
"""

from typing import Any
from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState
from app.agents.prompts import AgentPrompts
from app.tools.qwen_api_wrapper import QwenAPIWrapper
from app.core.logging_config import get_logger

logger = get_logger(__name__)


# ==================== 智能决策相关常量 ====================
# 主动学习触发阈值
ACTIVE_LEARNING_TRIGGER_UNCERTAINTY = 0.3
ACTIVE_LEARNING_TRIGGER_LOW_CONF_RATIO = 0.2
# 最大搜索查询数
MAX_SEARCH_QUERIES = 10
# 最小样本分析数
MIN_SAMPLE_ANALYSIS = 3
MAX_SAMPLE_ANALYSIS = 8


class AnalysisAgent(BaseAgent):
    """
    分析智能体 - LLM 驱动的策略规划器
    
    主要职责：
    1. 使用 VLM 分析上传的图像
    2. 生成语义描述和场景分类
    3. 制定数据获取策略
    4. 根据主动学习信号决定是否触发数据获取
    
    智能决策机制：
    - 综合评估模型不确定性指标
    - 使用 LLM 生成优化的搜索关键词
    - 动态调整数据获取策略
    """

    def __init__(self, qwen_api: QwenAPIWrapper) -> None:
        """
        初始化分析智能体
        
        Args:
            qwen_api: Qwen API 封装器，用于 LLM/VLM 交互
        """
        super().__init__(agent_name="AnalysisAgent")
        self.qwen_api = qwen_api

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        执行分析和策略生成
        
        工作流程：
        1. 分析上传的图像
        2. 评估不确定性指标
        3. 决定是否需要获取更多数据
        4. 生成搜索策略
        
        Args:
            context: 上下文字典，必须包含：
                - job_id: str - 任务 ID
                - uploaded_images: list[str] - 上传图像路径
                - uncertainty_metrics: dict - 不确定性指标（来自推理智能体）
                
        Returns:
            包含以下字段的字典：
                - image_descriptions: list[str] - 图像描述
                - search_strategy: dict - 搜索策略
                - should_acquire_data: bool - 是否需要获取数据
                - analysis_completed: bool - 分析是否完成
        """
        self._log_execution_start()
        
        try:
            job_id = context["job_id"]
            uploaded_images = context.get("uploaded_images", [])
            uncertainty_metrics = context.get("uncertainty_metrics", {})
            active_learning_signals = context.get("active_learning_signals", {})
            
            logger.info(
                f"分析 {len(uploaded_images)} 张图像",
                extra={"job_id": job_id}
            )
            
            # 步骤 1: 使用 VLM 分析图像
            descriptions = await self._analyze_images(uploaded_images)
            
            # 步骤 2: 智能决策 - 是否需要获取更多数据
            acquisition_decision = self._make_acquisition_decision(
                uncertainty_metrics,
                active_learning_signals
            )
            
            # 步骤 3: 根据决策生成搜索策略
            if acquisition_decision["should_acquire"]:
                search_strategy = await self._generate_search_strategy(
                    descriptions,
                    uncertainty_metrics,
                    active_learning_signals
                )
            else:
                search_strategy = {
                    "queries": [],
                    "scene_type": "unknown",
                    "key_features": [],
                    "reason": "模型表现良好，无需获取更多数据"
                }
            
            logger.info(
                f"生成 {len(search_strategy.get('queries', []))} 个搜索查询 "
                f"(是否获取: {acquisition_decision['should_acquire']})",
                extra={
                    "job_id": job_id,
                    "scene_type": search_strategy.get("scene_type", "unknown")
                }
            )
            
            self._log_execution_end(
                f"分析完成，场景类型: {search_strategy.get('scene_type', 'unknown')}"
            )
            
            return {
                "image_descriptions": descriptions,
                "search_strategy": search_strategy,
                "search_queries": search_strategy.get("queries", []),
                "scene_type": search_strategy.get("scene_type", ""),
                "key_features": search_strategy.get("key_features", []),
                "should_acquire_data": acquisition_decision["should_acquire"],
                "acquisition_decision": acquisition_decision,
                "analysis_completed": True,
            }
            
        except Exception as e:
            self._log_error(e)
            raise

    async def _analyze_images(self, image_paths: list[str]) -> list[str]:
        """
        使用视觉语言模型分析图像
        
        Args:
            image_paths: 图像路径列表
            
        Returns:
            图像描述列表
        """
        descriptions = []
        
        # 选择代表性样本进行分析
        sample_count = min(MAX_SAMPLE_ANALYSIS, max(MIN_SAMPLE_ANALYSIS, len(image_paths)))
        sample_images = image_paths[:sample_count]
        
        for img_path in sample_images:
            try:
                description = await self.qwen_api.get_image_description(
                    image_path=img_path
                )
                descriptions.append(description)
                logger.info(f"分析图像: {Path(img_path).name}")
                
            except Exception as e:
                logger.warning(f"分析图像失败 {img_path}: {e}")
                continue
        
        if not descriptions:
            # 回退：提供通用描述
            descriptions.append(
                "遥感影像包含地理和地物信息，需要获取更多相似数据进行训练。"
            )
        
        return descriptions

    def _make_acquisition_decision(
        self,
        uncertainty_metrics: dict[str, Any],
        active_learning_signals: dict[str, Any]
    ) -> dict[str, Any]:
        """
        智能决策：是否需要获取更多数据
        
        基于主动学习信号进行综合判断：
        1. 不确定性分数是否超过阈值
        2. 低置信度检测比例是否过高
        3. 主动学习优先级评估
        
        Args:
            uncertainty_metrics: 不确定性指标
            active_learning_signals: 主动学习信号
            
        Returns:
            决策结果字典
        """
        # 提取关键指标
        uncertainty_score = uncertainty_metrics.get("uncertainty_score", 0.5)
        low_conf_ratio = uncertainty_metrics.get("low_confidence_ratio", 0.3)
        boundary_ratio = uncertainty_metrics.get("boundary_sample_ratio", 0.1)
        priority = uncertainty_metrics.get("active_learning_priority", "medium")
        
        # 获取主动学习建议
        acquisition_recommendation = active_learning_signals.get(
            "acquisition_recommendation", {}
        )
        high_value_count = active_learning_signals.get("high_value_count", 0)
        
        # 综合评分
        decision_score = (
            uncertainty_score * 0.35 +
            low_conf_ratio * 0.30 +
            boundary_ratio * 0.20 +
            (0.15 if priority == "high" else 0.08 if priority == "medium" else 0.0)
        )
        
        # 决策逻辑
        should_acquire = (
            decision_score > 0.25 or  # 综合分数阈值
            uncertainty_score > ACTIVE_LEARNING_TRIGGER_UNCERTAINTY or
            low_conf_ratio > ACTIVE_LEARNING_TRIGGER_LOW_CONF_RATIO or
            priority == "high"
        )
        
        # 确定原因
        reasons = []
        if uncertainty_score > ACTIVE_LEARNING_TRIGGER_UNCERTAINTY:
            reasons.append(f"模型不确定性较高 ({uncertainty_score:.2f})")
        if low_conf_ratio > ACTIVE_LEARNING_TRIGGER_LOW_CONF_RATIO:
            reasons.append(f"低置信度检测比例过高 ({low_conf_ratio:.2f})")
        if boundary_ratio > 0.15:
            reasons.append(f"边界样本比例较高 ({boundary_ratio:.2f})")
        if high_value_count > 10:
            reasons.append(f"存在 {high_value_count} 个高价值待标注样本")
        
        return {
            "should_acquire": should_acquire,
            "decision_score": round(decision_score, 4),
            "reasons": reasons if reasons else ["模型表现良好"],
            "priority": priority,
            "metrics_summary": {
                "uncertainty_score": uncertainty_score,
                "low_conf_ratio": low_conf_ratio,
                "boundary_ratio": boundary_ratio,
            }
        }

    async def _generate_search_strategy(
        self,
        descriptions: list[str],
        uncertainty_metrics: dict[str, Any],
        active_learning_signals: dict[str, Any]
    ) -> dict[str, Any]:
        """
        生成搜索策略
        
        使用 LLM 基于图像描述和不确定性分析生成优化的搜索策略。
        
        Args:
            descriptions: 图像描述列表
            uncertainty_metrics: 不确定性指标
            active_learning_signals: 主动学习信号
            
        Returns:
            搜索策略字典
        """
        # 构建上下文信息
        context_info = self._build_strategy_context(
            uncertainty_metrics, active_learning_signals
        )
        
        # 使用专业化的 System Prompt
        system_prompt = AgentPrompts.get_system_prompt("analysis")
        
        # 构建用户提示
        user_prompt = self._build_strategy_prompt(descriptions, context_info)
        
        try:
            search_strategy = await self.qwen_api.generate_search_strategy(
                descriptions=descriptions,
                num_queries=min(MAX_SEARCH_QUERIES, 5 + len(descriptions)),
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
        except Exception as e:
            logger.warning(f"LLM 策略生成失败，使用回退策略: {e}")
            search_strategy = self._fallback_strategy(descriptions)
        
        # 后处理：根据主动学习信号调整策略
        search_strategy = self._post_process_strategy(
            search_strategy, active_learning_signals
        )
        
        return search_strategy

    def _build_strategy_context(
        self,
        uncertainty_metrics: dict[str, Any],
        active_learning_signals: dict[str, Any]
    ) -> dict[str, Any]:
        """
        构建策略生成的上下文信息
        
        Args:
            uncertainty_metrics: 不确定性指标
            active_learning_signals: 主动学习信号
            
        Returns:
            上下文信息字典
        """
        # 获取少数类信息
        acquisition_recommendation = active_learning_signals.get(
            "acquisition_recommendation", {}
        )
        minority_classes = acquisition_recommendation.get("minority_classes", [])
        focus_areas = [a for a in acquisition_recommendation.get("focus_areas", []) if a]
        
        return {
            "uncertainty_level": uncertainty_metrics.get("active_learning_priority", "medium"),
            "boundary_sample_ratio": uncertainty_metrics.get("boundary_sample_ratio", 0),
            "minority_classes": minority_classes,
            "focus_areas": focus_areas,
            "suggested_count": acquisition_recommendation.get("suggested_count", 20),
        }

    def _build_strategy_prompt(
        self,
        descriptions: list[str],
        context_info: dict[str, Any]
    ) -> str:
        """
        构建策略生成的用户提示
        
        Args:
            descriptions: 图像描述列表
            context_info: 上下文信息
            
        Returns:
            用户提示字符串
        """
        desc_text = "\n".join([f"- {d}" for d in descriptions])
        
        focus_text = ""
        if context_info.get("focus_areas"):
            focus_text = f"\n重点关注: {', '.join(context_info['focus_areas'])}"
        
        minority_text = ""
        if context_info.get("minority_classes"):
            minority_text = f"\n需要补充的类别: {context_info['minority_classes']}"
        
        return f"""
请根据以下图像描述生成搜索策略：

图像描述：
{desc_text}

当前模型状态：
- 不确定性等级: {context_info.get('uncertainty_level', 'medium')}
- 边界样本比例: {context_info.get('boundary_sample_ratio', 0):.2%}
- 建议获取样本数: {context_info.get('suggested_count', 20)}
{focus_text}
{minority_text}

请生成优化的搜索关键词，确保：
1. 关键词与图像场景相关
2. 覆盖当前数据集的薄弱环节
3. 增加数据多样性
"""

    def _fallback_strategy(self, descriptions: list[str]) -> dict[str, Any]:
        """
        回退策略：当 LLM 调用失败时使用
        
        Args:
            descriptions: 图像描述列表
            
        Returns:
            基础搜索策略
        """
        # 从描述中提取关键词
        keywords = []
        for desc in descriptions:
            # 简单的关键词提取
            words = desc.replace("，", " ").replace("。", " ").split()
            keywords.extend([w for w in words if len(w) > 2])
        
        # 去重并限制数量
        unique_keywords = list(set(keywords))[:5]
        
        return {
            "queries": unique_keywords if unique_keywords else ["遥感影像", "目标检测"],
            "scene_type": "unknown",
            "key_features": [],
            "reason": "使用回退策略生成基础搜索词"
        }

    def _post_process_strategy(
        self,
        strategy: dict[str, Any],
        active_learning_signals: dict[str, Any]
    ) -> dict[str, Any]:
        """
        后处理搜索策略
        
        根据主动学习信号调整和优化策略。
        
        Args:
            strategy: 原始搜索策略
            active_learning_signals: 主动学习信号
            
        Returns:
            优化后的搜索策略
        """
        # 获取类别分布
        class_distribution = active_learning_signals.get("class_distribution", {})
        
        # 如果存在类别不平衡，添加相关搜索词
        if class_distribution:
            # 找出少数类
            avg_count = sum(class_distribution.values()) / len(class_distribution) if class_distribution else 0
            minority_classes = [
                cls for cls, count in class_distribution.items()
                if count < avg_count * 0.5
            ]
            
            if minority_classes:
                strategy["minority_focus"] = True
                strategy["minority_classes"] = minority_classes
        
        return strategy


# ==================== LangGraph 节点函数 ====================

async def analysis_node(state: AgentState) -> AgentState:
    """
    LangGraph 节点函数：分析图像并生成搜索策略
    
    此函数作为 LangGraph 工作流中的 perception 节点，负责：
    1. 使用 Qwen VLM 分析图像
    2. 提取关键词和场景特征
    3. 基于主动学习信号决定是否获取数据
    4. 生成优化的搜索策略
    
    Args:
        state: AgentState 状态字典
        
    Returns:
        更新后的 AgentState
    """
    logger.info("执行分析节点 (perception)")
    
    try:
        # 初始化工具
        qwen_api = QwenAPIWrapper()
        
        # 获取图像 URL 列表
        image_urls = state.get("image_urls", [])
        if not image_urls:
            image_urls = state.get("uploaded_images", [])
        
        if not image_urls:
            error_msg = "未找到图像 URL"
            logger.error(error_msg)
            state["errors"] = state.get("errors", []) + [error_msg]
            return state
        
        # 获取不确定性指标和主动学习信号
        uncertainty_metrics = state.get("uncertainty_metrics", {})
        active_learning_signals = state.get("active_learning_signals", {})
        
        # 调用 Qwen API 分析图像
        analysis_result = await qwen_api.analyze_image(image_urls)
        
        # 创建分析智能体实例进行决策
        analysis_agent = AnalysisAgent(qwen_api)
        
        # 智能决策：是否需要获取数据
        acquisition_decision = analysis_agent._make_acquisition_decision(
            uncertainty_metrics,
            active_learning_signals
        )
        
        # 根据决策生成搜索策略
        if acquisition_decision["should_acquire"]:
            search_strategy = await qwen_api.generate_search_strategy(
                descriptions=analysis_result.get("descriptions", []),
                num_queries=5
            )
        else:
            search_strategy = {
                "queries": [],
                "scene_type": "unknown",
                "reason": "模型表现良好，跳过数据获取"
            }
        
        # 更新状态
        state["analysis_result"] = analysis_result
        state["search_keywords"] = search_strategy.get("queries", [])
        state["search_queries"] = search_strategy.get("queries", [])
        state["scene_type"] = search_strategy.get("scene_type", "未知")
        state["should_acquire_data"] = acquisition_decision["should_acquire"]
        state["acquisition_decision"] = acquisition_decision
        
        logger.info(
            f"分析完成: 生成 {len(state['search_keywords'])} 个搜索关键词 "
            f"(是否获取数据: {acquisition_decision['should_acquire']})"
        )
        
        return state
        
    except Exception as e:
        error_msg = f"分析节点执行失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["errors"] = state.get("errors", []) + [error_msg]
        return state

"""
Analysis Agent for generating data acquisition strategy.

This agent acts as the "strategy planner" using LLM to analyze
inference results and generate intelligent search strategies.
"""

from typing import Any
from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState
from app.agents.prompts import AgentPrompts
from app.tools.qwen_api_wrapper import QwenAPIWrapper
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AnalysisAgent(BaseAgent):
    """
    Agent for strategy analysis and planning.
    
    This agent leverages LLM (Qwen) to:
    1. Analyze uploaded images using VLM
    2. Generate semantic descriptions
    3. Create search strategies for data acquisition
    4. Determine optimal search queries
    """

    def __init__(self, qwen_api: QwenAPIWrapper) -> None:
        """
        Initialize the Analysis Agent.
        
        Args:
            qwen_api: Qwen API wrapper for LLM/VLM interactions
        """
        super().__init__(agent_name="AnalysisAgent")
        self.qwen_api = qwen_api

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute analysis and generate acquisition strategy.
        
        Args:
            context: Must contain:
                - job_id: str
                - uploaded_images: list[str]
                - uncertainty_metrics: dict
                
        Returns:
            Dictionary containing:
                - image_descriptions: list[str]
                - search_strategy: dict
                - analysis_completed: bool
        """
        self._log_execution_start()
        
        try:
            job_id = context["job_id"]
            uploaded_images = context.get("uploaded_images", [])
            uncertainty_metrics = context.get("uncertainty_metrics", {})
            
            logger.info(
                f"Analyzing {len(uploaded_images)} images",
                extra={"job_id": job_id}
            )
            
            # Step 1: Analyze images with VLM
            descriptions = await self._analyze_images(uploaded_images)
            
            # Step 2: Generate search strategy based on descriptions
            # 使用专业化的 System Prompt
            system_prompt = AgentPrompts.get_system_prompt("analysis")
            user_prompt = AgentPrompts.build_analysis_prompt(
                image_descriptions=descriptions,
                num_queries=5
            )
            
            search_strategy = await self.qwen_api.generate_search_strategy(
                descriptions=descriptions,
                num_queries=5,
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            logger.info(
                f"Generated {len(search_strategy.get('queries', []))} search queries",
                extra={
                    "job_id": job_id,
                    "scene_type": search_strategy.get("scene_type", "unknown")
                }
            )
            
            self._log_execution_end(
                f"Generated strategy for {search_strategy.get('scene_type', 'unknown')} scene"
            )
            
            return {
                "image_descriptions": descriptions,
                "search_strategy": search_strategy,
                "search_queries": search_strategy.get("queries", []),
                "scene_type": search_strategy.get("scene_type", ""),
                "key_features": search_strategy.get("key_features", []),
                "analysis_completed": True,
            }
            
        except Exception as e:
            self._log_error(e)
            raise

    async def _analyze_images(self, image_paths: list[str]) -> list[str]:
        """
        Analyze images using Vision-Language Model.
        
        Args:
            image_paths: List of paths to images
            
        Returns:
            List of image descriptions
        """
        descriptions = []
        
        # Analyze up to 5 representative images
        sample_images = image_paths[:5]
        
        for img_path in sample_images:
            try:
                description = await self.qwen_api.get_image_description(
                    image_path=img_path
                )
                descriptions.append(description)
                logger.info(f"Analyzed image: {Path(img_path).name}")
                
            except Exception as e:
                logger.warning(f"Failed to analyze image {img_path}: {e}")
                continue
        
        if not descriptions:
            # Fallback: provide a generic description
            descriptions.append(
                "遥感影像包含地理和地物信息，需要获取更多相似数据进行训练。"
            )
        
        return descriptions


# ==================== LangGraph Node Functions ====================

async def analysis_node(state: AgentState) -> AgentState:
    """
    LangGraph 节点函数：分析图像并生成搜索策略。
    
    此函数作为 LangGraph 工作流中的 perception 节点，负责：
    1. 使用 Qwen VLM 分析图像
    2. 提取关键词和场景特征
    3. 生成搜索策略
    
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
            # 尝试从其他字段获取
            image_urls = state.get("uploaded_images", [])
        
        if not image_urls:
            error_msg = "未找到图像 URL"
            logger.error(error_msg)
            state["errors"] = state.get("errors", []) + [error_msg]
            return state
        
        # 调用 Qwen API 分析图像
        analysis_result = await qwen_api.analyze_image(image_urls)
        
        # 从分析结果提取搜索关键词
        # 使用 LLM 生成搜索策略
        search_strategy = await qwen_api.generate_search_strategy(
            descriptions=analysis_result.get("descriptions", []),
            num_queries=5
        )
        
        # 更新状态
        state["analysis_result"] = analysis_result
        state["search_keywords"] = search_strategy.get("queries", [])
        state["search_queries"] = search_strategy.get("queries", [])
        state["scene_type"] = search_strategy.get("scene_type", "未知")
        
        logger.info(
            f"分析完成: 生成 {len(state['search_keywords'])} 个搜索关键词"
        )
        
        return state
        
    except Exception as e:
        error_msg = f"分析节点执行失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["errors"] = state.get("errors", []) + [error_msg]
        return state



"""
Analysis Agent for generating data acquisition strategy.

This agent acts as the "strategy planner" using LLM to analyze
inference results and generate intelligent search strategies.
"""

from typing import Any
from pathlib import Path

from app.agents.base_agent import BaseAgent
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
            search_strategy = await self.qwen_api.generate_search_strategy(
                descriptions=descriptions,
                num_queries=5
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



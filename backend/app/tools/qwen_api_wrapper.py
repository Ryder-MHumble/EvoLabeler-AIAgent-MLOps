"""
Qwen API wrapper for LLM and VLM interactions.

This module provides a QwenAPIWrapper class that encapsulates
interactions with the Qwen API (硅基流动 API).
"""

import base64
from typing import Any, Optional
import httpx

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class QwenAPIWrapper:
    """
    Wrapper class for Qwen API interactions.
    
    This class provides methods for:
    - Vision-Language Model (VLM) for image analysis
    - Text-only LLM for strategy generation
    """

    def __init__(self) -> None:
        """Initialize the Qwen API wrapper."""
        self.api_key = settings.qwen_api_key
        self.base_url = settings.qwen_api_base_url
        self.vl_model = settings.qwen_vl_model
        self.text_model = settings.qwen_text_model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        logger.info("QwenAPIWrapper initialized")

    async def get_image_description(
        self, 
        image_path: str,
        prompt: str = "请详细描述这张遥感影像中的内容，包括地形、地物、建筑等特征。"
    ) -> str:
        """
        Get description of an image using Vision-Language Model.
        
        Args:
            image_path: Path to the image file or base64 encoded image
            prompt: Custom prompt for image analysis
            
        Returns:
            Image description text
        """
        try:
            # If image_path is a file path, read and encode it
            if not image_path.startswith("data:image"):
                with open(image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
                    image_url = f"data:image/jpeg;base64,{image_data}"
            else:
                image_url = image_path

            payload = {
                "model": self.vl_model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": image_url}},
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7,
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

            description = result["choices"][0]["message"]["content"]
            logger.info("Generated image description", extra={"image": image_path})
            return description

        except Exception as e:
            logger.error(f"Failed to get image description: {e}", exc_info=True)
            raise

    async def generate_search_strategy(
        self, 
        descriptions: list[str],
        num_queries: int = 5,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Generate search strategy based on image descriptions.
        
        This method uses the LLM to analyze image descriptions and
        generate effective search queries for data acquisition.
        
        Args:
            descriptions: List of image descriptions
            num_queries: Number of search queries to generate
            system_prompt: Custom system prompt (uses default if not provided)
            user_prompt: Custom user prompt (uses default if not provided)
            
        Returns:
            Dictionary containing search queries and strategy
        """
        try:
            # 使用自定义 Prompt 或默认 Prompt
            if user_prompt is None:
                combined_descriptions = "\n\n".join(
                    [f"图像 {i+1}: {desc}" for i, desc in enumerate(descriptions)]
                )

                user_prompt = f"""
作为一个遥感影像分析专家，请根据以下图像描述，生成用于网络搜索的关键词策略。

图像描述：
{combined_descriptions}

请生成 {num_queries} 个高质量的搜索关键词或短语，用于在搜索引擎中查找相似的遥感影像。
这些关键词应该：
1. 涵盖主要的地物类型和场景特征
2. 包含专业的遥感术语
3. 具有良好的搜索效果
4. 多样化，覆盖不同角度

请以 JSON 格式返回结果：
{{
    "queries": ["关键词1", "关键词2", ...],
    "strategy": "简要说明搜索策略",
    "scene_type": "场景类型",
    "key_features": ["特征1", "特征2", ...]
}}
"""
            
            if system_prompt is None:
                system_prompt = "你是一个专业的遥感影像分析专家。"

            payload = {
                "model": self.text_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "max_tokens": 2000,
                "temperature": 0.8,
                "response_format": {"type": "json_object"},
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

            import json
            strategy = json.loads(result["choices"][0]["message"]["content"])
            logger.info("Generated search strategy", extra={"num_queries": num_queries})
            return strategy

        except Exception as e:
            logger.error(f"Failed to generate search strategy: {e}", exc_info=True)
            raise

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generic chat completion method.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name (defaults to text_model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Model response text
        """
        try:
            payload = {
                "model": model or self.text_model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

            return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Failed to complete chat: {e}", exc_info=True)
            raise



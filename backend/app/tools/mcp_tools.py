"""
MCP (Model Context Protocol) 工具集成模块。

本模块提供符合 MCP 标准的工具接口，使 LLM 能够：
1. 调用外部工具和服务
2. 访问结构化知识
3. 执行复杂操作

MCP 工具专为遥感影像分析和 MLOps 场景设计。
"""

from typing import Any, Dict, List, Optional, Callable
import json
from enum import Enum
from pydantic import BaseModel, Field

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class MCPToolType(str, Enum):
    """MCP 工具类型枚举。"""
    IMAGE_ANALYSIS = "image_analysis"
    DATA_RETRIEVAL = "data_retrieval"
    MODEL_INFERENCE = "model_inference"
    QUALITY_CONTROL = "quality_control"
    METADATA_EXTRACTION = "metadata_extraction"


class MCPToolDefinition(BaseModel):
    """MCP 工具定义。"""
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    tool_type: MCPToolType = Field(..., description="工具类型")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="参数schema")
    required_params: List[str] = Field(default_factory=list, description="必需参数")


class MCPToolRegistry:
    """
    MCP 工具注册表。
    
    管理所有可用的 MCP 工具，提供工具发现和调用能力。
    """
    
    def __init__(self) -> None:
        """初始化工具注册表。"""
        self.tools: Dict[str, MCPToolDefinition] = {}
        self.handlers: Dict[str, Callable] = {}
        self._register_builtin_tools()
        logger.info("MCP 工具注册表已初始化")
    
    def _register_builtin_tools(self) -> None:
        """注册内置工具。"""
        # 1. 场景分类工具
        self.register_tool(
            MCPToolDefinition(
                name="classify_scene",
                description="对遥感影像进行场景分类（城市、农村、工业区等）",
                tool_type=MCPToolType.IMAGE_ANALYSIS,
                parameters={
                    "image_description": {"type": "string", "description": "图像描述"},
                    "features": {"type": "array", "description": "视觉特征列表"}
                },
                required_params=["image_description"]
            ),
            self._classify_scene_handler
        )
        
        # 2. 关键词优化工具
        self.register_tool(
            MCPToolDefinition(
                name="optimize_search_keywords",
                description="优化搜索关键词以提高数据检索质量",
                tool_type=MCPToolType.DATA_RETRIEVAL,
                parameters={
                    "initial_keywords": {"type": "array", "description": "初始关键词"},
                    "scene_type": {"type": "string", "description": "场景类型"},
                    "language": {"type": "string", "description": "目标语言"}
                },
                required_params=["initial_keywords"]
            ),
            self._optimize_keywords_handler
        )
        
        # 3. 数据质量评估工具
        self.register_tool(
            MCPToolDefinition(
                name="assess_data_quality",
                description="评估获取数据的质量和可用性",
                tool_type=MCPToolType.QUALITY_CONTROL,
                parameters={
                    "image_url": {"type": "string", "description": "图像URL"},
                    "predictions": {"type": "object", "description": "预测结果"},
                    "confidence_threshold": {"type": "number", "description": "置信度阈值"}
                },
                required_params=["predictions"]
            ),
            self._assess_quality_handler
        )
        
        # 4. 不确定性量化工具
        self.register_tool(
            MCPToolDefinition(
                name="quantify_uncertainty",
                description="量化模型预测的不确定性（熵、方差等）",
                tool_type=MCPToolType.MODEL_INFERENCE,
                parameters={
                    "predictions": {"type": "array", "description": "预测结果列表"},
                    "method": {"type": "string", "description": "量化方法"}
                },
                required_params=["predictions"]
            ),
            self._quantify_uncertainty_handler
        )
        
        # 5. 元数据提取工具
        self.register_tool(
            MCPToolDefinition(
                name="extract_image_metadata",
                description="从遥感影像中提取元数据（分辨率、坐标等）",
                tool_type=MCPToolType.METADATA_EXTRACTION,
                parameters={
                    "image_path": {"type": "string", "description": "图像路径"}
                },
                required_params=["image_path"]
            ),
            self._extract_metadata_handler
        )
    
    def register_tool(
        self,
        definition: MCPToolDefinition,
        handler: Callable
    ) -> None:
        """
        注册新工具。
        
        Args:
            definition: 工具定义
            handler: 工具处理函数
        """
        self.tools[definition.name] = definition
        self.handlers[definition.name] = handler
        logger.info(f"已注册 MCP 工具: {definition.name}")
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        获取所有工具定义（OpenAI Functions 格式）。
        
        Returns:
            工具定义列表
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": tool.parameters,
                    "required": tool.required_params
                }
            }
            for tool in self.tools.values()
        ]
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行工具。
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            执行结果
        """
        if tool_name not in self.handlers:
            raise ValueError(f"未知工具: {tool_name}")
        
        logger.info(f"执行 MCP 工具: {tool_name}", extra={"parameters": parameters})
        
        try:
            handler = self.handlers[tool_name]
            result = await handler(parameters)
            logger.info(f"工具执行成功: {tool_name}")
            return result
        except Exception as e:
            logger.error(f"工具执行失败: {tool_name} - {e}", exc_info=True)
            return {"error": str(e), "tool": tool_name}
    
    # ==================== 工具处理函数 ====================
    
    async def _classify_scene_handler(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """场景分类处理函数。"""
        description = params.get("image_description", "")
        features = params.get("features", [])
        
        # 简单的基于规则的分类
        scene_types = {
            "城市": ["建筑", "道路", "街道", "building", "urban", "city"],
            "农村": ["田地", "农田", "村庄", "farm", "rural", "field"],
            "工业区": ["工厂", "仓库", "港口", "industrial", "factory"],
            "自然": ["森林", "山地", "水体", "forest", "mountain", "water"]
        }
        
        scores = {}
        text = description.lower() + " ".join(map(str, features)).lower()
        
        for scene, keywords in scene_types.items():
            score = sum(1 for kw in keywords if kw in text)
            scores[scene] = score
        
        predicted_scene = max(scores, key=scores.get) if scores else "未知"
        confidence = scores[predicted_scene] / (sum(scores.values()) + 1e-6)
        
        return {
            "scene_type": predicted_scene,
            "confidence": round(confidence, 2),
            "scores": scores,
            "reasoning": f"基于关键词匹配，识别为 {predicted_scene} 场景"
        }
    
    async def _optimize_keywords_handler(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """关键词优化处理函数。"""
        initial = params.get("initial_keywords", [])
        scene_type = params.get("scene_type", "")
        language = params.get("language", "zh")
        
        # 关键词扩展策略
        expansions = {
            "城市": ["urban", "city", "metropolitan", "downtown"],
            "农村": ["rural", "countryside", "agricultural"],
            "工业区": ["industrial", "factory", "manufacturing"],
            "自然": ["natural", "landscape", "wilderness"]
        }
        
        optimized = list(initial)
        
        # 添加场景相关词
        if scene_type in expansions:
            optimized.extend(expansions[scene_type])
        
        # 添加技术术语
        technical_terms = [
            "遥感影像" if language == "zh" else "remote sensing",
            "卫星图像" if language == "zh" else "satellite imagery",
            "高分辨率" if language == "zh" else "high resolution"
        ]
        optimized.extend(technical_terms)
        
        # 去重
        optimized = list(dict.fromkeys(optimized))
        
        return {
            "optimized_keywords": optimized,
            "original_count": len(initial),
            "optimized_count": len(optimized),
            "added_terms": [k for k in optimized if k not in initial]
        }
    
    async def _assess_quality_handler(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """数据质量评估处理函数。"""
        predictions = params.get("predictions", {})
        threshold = params.get("confidence_threshold", 0.5)
        
        detections = predictions.get("detections", [])
        
        # 质量指标计算
        if not detections:
            return {
                "quality_score": 0.0,
                "is_high_quality": False,
                "reason": "无检测结果"
            }
        
        confidences = [d.get("confidence", 0) for d in detections]
        avg_conf = sum(confidences) / len(confidences)
        high_conf_count = sum(1 for c in confidences if c >= threshold)
        
        quality_score = (high_conf_count / len(detections)) * avg_conf
        is_high_quality = quality_score >= 0.6
        
        return {
            "quality_score": round(quality_score, 2),
            "is_high_quality": is_high_quality,
            "average_confidence": round(avg_conf, 2),
            "high_confidence_ratio": round(high_conf_count / len(detections), 2),
            "total_detections": len(detections),
            "recommendation": "适合训练" if is_high_quality else "建议过滤"
        }
    
    async def _quantify_uncertainty_handler(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """不确定性量化处理函数。"""
        predictions = params.get("predictions", [])
        method = params.get("method", "entropy")
        
        if not predictions:
            return {"uncertainty": 1.0, "confidence": 0.0}
        
        # 收集置信度
        all_confidences = []
        for pred in predictions:
            detections = pred.get("detections", [])
            all_confidences.extend([d.get("confidence", 0) for d in detections])
        
        if not all_confidences:
            return {"uncertainty": 1.0, "confidence": 0.0}
        
        # 计算不确定性
        import numpy as np
        
        confidences = np.array(all_confidences)
        mean_conf = float(np.mean(confidences))
        std_conf = float(np.std(confidences))
        
        if method == "entropy":
            # 简化的熵计算
            uncertainty = 1.0 - mean_conf
        elif method == "variance":
            uncertainty = std_conf
        else:
            uncertainty = 1.0 - mean_conf
        
        return {
            "uncertainty": round(uncertainty, 3),
            "mean_confidence": round(mean_conf, 3),
            "std_confidence": round(std_conf, 3),
            "method": method,
            "interpretation": "高" if uncertainty > 0.5 else "中" if uncertainty > 0.3 else "低"
        }
    
    async def _extract_metadata_handler(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """元数据提取处理函数。"""
        image_path = params.get("image_path", "")
        
        try:
            from PIL import Image
            import os
            
            if not os.path.exists(image_path):
                return {"error": "文件不存在"}
            
            with Image.open(image_path) as img:
                metadata = {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "size_bytes": os.path.getsize(image_path),
                    "aspect_ratio": round(img.width / img.height, 2)
                }
                
                # 提取 EXIF 数据（如果有）
                exif = img.getexif()
                if exif:
                    metadata["has_exif"] = True
                else:
                    metadata["has_exif"] = False
                
                return metadata
                
        except Exception as e:
            return {"error": str(e)}


# 全局工具注册表实例
mcp_registry = MCPToolRegistry()


def get_mcp_tools() -> MCPToolRegistry:
    """获取全局 MCP 工具注册表。"""
    return mcp_registry


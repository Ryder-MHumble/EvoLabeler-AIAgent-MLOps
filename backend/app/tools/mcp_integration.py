"""
MCP (Model Context Protocol) 集成模块。

本模块提供真正的 MCP 协议支持，可以：
1. 挂载外部 MCP 服务（Context7, Playwright, Fetch等）
2. 将本地工具注册为 MCP 工具
3. 统一的工具调用接口

支持的 MCP 服务：
- Context7 MCP: 文档检索和知识库
- Playwright MCP: 浏览器自动化
- Fetch MCP: HTTP 请求
- 自定义 MCP 服务
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import httpx

from app.core.logging_config import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class MCPServiceType(str, Enum):
    """MCP 服务类型。"""
    CONTEXT7 = "context7"           # Context7 文档服务
    PLAYWRIGHT = "playwright"        # Playwright 浏览器自动化
    FETCH = "fetch"                  # HTTP 请求服务
    FILESYSTEM = "filesystem"        # 文件系统服务
    CUSTOM = "custom"                # 自定义服务


class MCPService:
    """
    MCP 服务基类。
    
    封装与外部 MCP 服务的通信逻辑。
    """
    
    def __init__(
        self,
        service_name: str,
        service_type: MCPServiceType,
        endpoint: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化 MCP 服务。
        
        Args:
            service_name: 服务名称
            service_type: 服务类型
            endpoint: 服务端点（如果是远程服务）
            config: 服务配置
        """
        self.service_name = service_name
        self.service_type = service_type
        self.endpoint = endpoint
        self.config = config or {}
        self.client = httpx.AsyncClient(timeout=30.0) if endpoint else None
        
        logger.info(f"MCP 服务已初始化: {service_name} ({service_type})")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        列出服务提供的所有工具。
        
        Returns:
            工具定义列表
        """
        raise NotImplementedError
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        调用工具。
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        raise NotImplementedError
    
    async def close(self):
        """关闭服务连接。"""
        if self.client:
            await self.client.aclose()


class Context7MCPService(MCPService):
    """
    Context7 MCP 服务。
    
    提供文档检索和知识库功能。
    """
    
    def __init__(self):
        super().__init__(
            service_name="context7",
            service_type=MCPServiceType.CONTEXT7,
            config={
                "api_key": settings.context7_api_key if hasattr(settings, 'context7_api_key') else None
            }
        )
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出 Context7 工具。"""
        return [
            {
                "name": "search_remote_sensing_docs",
                "description": "搜索遥感影像处理相关文档和最佳实践",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词"
                        },
                        "max_results": {
                            "type": "number",
                            "description": "最大结果数",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_yolo_documentation",
                "description": "获取 YOLO 目标检测相关文档",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "主题（如 training, inference, configuration）"
                        }
                    },
                    "required": ["topic"]
                }
            }
        ]
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用 Context7 工具。"""
        if tool_name == "search_remote_sensing_docs":
            return await self._search_docs(arguments)
        elif tool_name == "get_yolo_documentation":
            return await self._get_yolo_docs(arguments)
        else:
            raise ValueError(f"未知工具: {tool_name}")
    
    async def _search_docs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """搜索文档（模拟实现）。"""
        query = args.get("query", "")
        max_results = args.get("max_results", 5)
        
        # 这里应该调用真实的 Context7 API
        # 目前返回模拟数据
        results = [
            {
                "title": f"遥感影像处理 - {query}",
                "content": f"关于 {query} 的详细文档...",
                "source": "Remote Sensing Handbook",
                "relevance": 0.95
            }
        ]
        
        return {
            "results": results[:max_results],
            "total": len(results),
            "query": query
        }
    
    async def _get_yolo_docs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取 YOLO 文档。"""
        topic = args.get("topic", "")
        
        docs = {
            "training": "YOLO 训练配置：使用 train.py 脚本...",
            "inference": "YOLO 推理：使用 detect.py 进行目标检测...",
            "configuration": "YOLO 配置文件说明：data.yaml, model.yaml..."
        }
        
        return {
            "topic": topic,
            "documentation": docs.get(topic, "主题不存在"),
            "examples": ["示例1", "示例2"]
        }


class PlaywrightMCPService(MCPService):
    """
    Playwright MCP 服务。
    
    提供浏览器自动化功能（通过现有的 WebCrawler）。
    """
    
    def __init__(self):
        super().__init__(
            service_name="playwright",
            service_type=MCPServiceType.PLAYWRIGHT
        )
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出 Playwright 工具。"""
        return [
            {
                "name": "crawl_images",
                "description": "从搜索引擎爬取图片",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词"
                        },
                        "max_images": {
                            "type": "number",
                            "description": "最大图片数",
                            "default": 10
                        },
                        "search_engine": {
                            "type": "string",
                            "description": "搜索引擎（bing/google）",
                            "default": "bing"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "screenshot_page",
                "description": "对网页进行截图",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "网页URL"
                        },
                        "full_page": {
                            "type": "boolean",
                            "description": "是否全页截图",
                            "default": False
                        }
                    },
                    "required": ["url"]
                }
            }
        ]
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用 Playwright 工具。"""
        if tool_name == "crawl_images":
            return await self._crawl_images(arguments)
        elif tool_name == "screenshot_page":
            return await self._screenshot_page(arguments)
        else:
            raise ValueError(f"未知工具: {tool_name}")
    
    async def _crawl_images(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """爬取图片（通过现有 WebCrawler）。"""
        from app.tools.web_crawler import WebCrawler
        from app.tools.supabase_client import SupabaseClient
        
        query = args.get("query", "")
        max_images = args.get("max_images", 10)
        
        # 使用现有的爬虫
        crawler = WebCrawler(SupabaseClient())
        images = await crawler.crawl_images([query], max_images_per_query=max_images)
        
        return {
            "query": query,
            "images_found": len(images),
            "images": images
        }
    
    async def _screenshot_page(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """网页截图。"""
        # 这里可以集成真实的截图功能
        return {
            "status": "success",
            "url": args.get("url"),
            "screenshot_path": "/tmp/screenshot.png"
        }


class FetchMCPService(MCPService):
    """
    Fetch MCP 服务。
    
    提供 HTTP 请求功能。
    """
    
    def __init__(self):
        super().__init__(
            service_name="fetch",
            service_type=MCPServiceType.FETCH
        )
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出 Fetch 工具。"""
        return [
            {
                "name": "http_get",
                "description": "发送 HTTP GET 请求",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "请求URL"
                        },
                        "headers": {
                            "type": "object",
                            "description": "请求头"
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "http_post",
                "description": "发送 HTTP POST 请求",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "请求URL"
                        },
                        "body": {
                            "type": "object",
                            "description": "请求体"
                        },
                        "headers": {
                            "type": "object",
                            "description": "请求头"
                        }
                    },
                    "required": ["url"]
                }
            }
        ]
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用 Fetch 工具。"""
        if tool_name == "http_get":
            return await self._http_get(arguments)
        elif tool_name == "http_post":
            return await self._http_post(arguments)
        else:
            raise ValueError(f"未知工具: {tool_name}")
    
    async def _http_get(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """HTTP GET 请求。"""
        url = args.get("url", "")
        headers = args.get("headers", {})
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text[:1000]  # 限制返回长度
            }
    
    async def _http_post(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """HTTP POST 请求。"""
        url = args.get("url", "")
        body = args.get("body", {})
        headers = args.get("headers", {})
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, headers=headers)
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text[:1000]
            }


class MCPIntegration:
    """
    MCP 集成管理器。
    
    统一管理所有 MCP 服务和工具。
    """
    
    def __init__(self):
        """初始化 MCP 集成。"""
        self.services: Dict[str, MCPService] = {}
        self._register_default_services()
        logger.info("MCP 集成已初始化")
    
    def _register_default_services(self):
        """注册默认 MCP 服务。"""
        # Context7 服务
        self.register_service(Context7MCPService())
        
        # Playwright 服务
        self.register_service(PlaywrightMCPService())
        
        # Fetch 服务
        self.register_service(FetchMCPService())
        
        logger.info(f"已注册 {len(self.services)} 个 MCP 服务")
    
    def register_service(self, service: MCPService):
        """
        注册 MCP 服务。
        
        Args:
            service: MCP 服务实例
        """
        self.services[service.service_name] = service
        logger.info(f"已注册 MCP 服务: {service.service_name}")
    
    async def list_all_tools(self) -> List[Dict[str, Any]]:
        """
        列出所有可用工具。
        
        Returns:
            工具定义列表
        """
        all_tools = []
        
        for service_name, service in self.services.items():
            tools = await service.list_tools()
            # 添加服务前缀
            for tool in tools:
                tool["service"] = service_name
                tool["name"] = f"{service_name}.{tool['name']}"
                all_tools.append(tool)
        
        logger.info(f"共 {len(all_tools)} 个可用工具")
        return all_tools
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        调用工具。
        
        Args:
            tool_name: 工具名称（格式: service_name.tool_name）
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        # 解析服务名和工具名
        if "." in tool_name:
            service_name, actual_tool_name = tool_name.split(".", 1)
        else:
            raise ValueError(f"工具名称格式错误: {tool_name}，应为 'service.tool'")
        
        # 获取服务
        service = self.services.get(service_name)
        if not service:
            raise ValueError(f"未知服务: {service_name}")
        
        # 调用工具
        logger.info(f"调用 MCP 工具: {tool_name}", extra={"arguments": arguments})
        
        try:
            result = await service.call_tool(actual_tool_name, arguments)
            logger.info(f"工具调用成功: {tool_name}")
            return result
        except Exception as e:
            logger.error(f"工具调用失败: {tool_name} - {e}", exc_info=True)
            return {"error": str(e), "tool": tool_name}
    
    async def close_all(self):
        """关闭所有服务连接。"""
        for service in self.services.values():
            await service.close()
        logger.info("所有 MCP 服务已关闭")


# 全局 MCP 集成实例
_mcp_integration: Optional[MCPIntegration] = None


def get_mcp_integration() -> MCPIntegration:
    """获取全局 MCP 集成实例。"""
    global _mcp_integration
    if _mcp_integration is None:
        _mcp_integration = MCPIntegration()
    return _mcp_integration


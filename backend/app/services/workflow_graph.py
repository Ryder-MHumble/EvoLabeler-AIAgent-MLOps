"""
LangGraph 工作流图定义模块。

此模块定义了基于 LangGraph StateGraph 的多智能体工作流。
实现了从图像分析到数据获取再到模型训练的完整自动化流程。
"""

from typing import Literal, Any
from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.analysis_agent import analysis_node
from app.agents.acquisition_agent import hunting_node
from app.agents.training_agent import evolution_node
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def should_continue_to_hunter(state: AgentState) -> Literal["hunter", "end"]:
    """
    条件边函数：判断是否继续到 hunter 节点。
    
    如果分析结果中包含关键词，则继续到 hunter 节点进行数据获取。
    否则结束工作流。
    
    Args:
        state: AgentState 状态字典
        
    Returns:
        "hunter" 或 "end"
    """
    search_keywords = state.get("search_keywords", [])
    if search_keywords and len(search_keywords) > 0:
        logger.info(f"找到 {len(search_keywords)} 个搜索关键词，继续到 hunter 节点")
        return "hunter"
    else:
        logger.warning("未找到搜索关键词，结束工作流")
        return "end"


def should_continue_to_evolution(state: AgentState) -> Literal["evolution", "end"]:
    """
    条件边函数：判断是否继续到 evolution 节点。
    
    如果获取了新的数据（crawled_count > 0），则继续到 evolution 节点进行训练。
    否则结束工作流。
    
    Args:
        state: AgentState 状态字典
        
    Returns:
        "evolution" 或 "end"
    """
    crawled_count = state.get("crawled_count", 0)
    if crawled_count > 0:
        logger.info(f"获取了 {crawled_count} 张新图像，继续到 evolution 节点")
        return "evolution"
    else:
        logger.warning("未获取新数据，结束工作流")
        return "end"


def build_workflow_graph() -> Any:
    """
    构建 LangGraph 工作流图。
    
    工作流结构：
    START -> perception (分析) -> [条件判断] -> hunter (获取) -> [条件判断] -> evolution (训练) -> END
    
    节点说明：
    - perception: 使用 Qwen VLM 分析图像，生成搜索策略
    - hunter: 根据关键词爬取网络图像
    - evolution: 触发远程 GPU 服务器上的训练任务
    
    Returns:
        编译后的 LangGraph Runnable
    """
    # 创建状态图
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("perception", analysis_node)
    workflow.add_node("hunter", hunting_node)
    workflow.add_node("evolution", evolution_node)
    
    # 设置入口点
    workflow.set_entry_point("perception")
    
    # 添加边
    # perception -> hunter (如果找到关键词)
    workflow.add_conditional_edges(
        "perception",
        should_continue_to_hunter,
        {
            "hunter": "hunter",
            "end": END
        }
    )
    
    # hunter -> evolution (如果获取了新数据)
    workflow.add_conditional_edges(
        "hunter",
        should_continue_to_evolution,
        {
            "evolution": "evolution",
            "end": END
        }
    )
    
    # evolution -> END
    workflow.add_edge("evolution", END)
    
    # 编译图
    app = workflow.compile()
    
    logger.info("LangGraph 工作流图构建完成")
    return app


# 全局工作流实例（延迟初始化）
_workflow_app: Any = None


def get_workflow_app() -> Any:
    """
    获取工作流应用实例（单例模式）。
    
    Returns:
        编译后的 LangGraph Runnable
    """
    global _workflow_app
    if _workflow_app is None:
        _workflow_app = build_workflow_graph()
    return _workflow_app


async def run_workflow(initial_state: AgentState) -> AgentState:
    """
    运行完整工作流。
    
    这是一个便捷函数，用于执行从初始状态到最终状态的完整工作流。
    
    Args:
        initial_state: 初始 AgentState 状态字典
        
    Returns:
        最终 AgentState 状态字典
    """
    app = get_workflow_app()
    
    logger.info(f"开始执行工作流，项目ID: {initial_state.get('project_id', 'unknown')}")
    
    # 执行工作流
    final_state = None
    async for state in app.astream(initial_state):
        # 记录中间状态
        logger.debug(f"工作流状态更新: {list(state.keys())}")
        # 获取最后一个节点的输出
        for node_name, node_state in state.items():
            final_state = node_state
    
    if final_state is None:
        final_state = initial_state
    
    logger.info("工作流执行完成")
    return final_state


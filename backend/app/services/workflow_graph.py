"""
LangGraph 工作流图定义模块 - EvoLoop 迭代版本

此模块定义了基于 LangGraph StateGraph 的多智能体工作流。
支持多轮迭代的自进化循环：
  分析 → 数据获取 → 训练 → 评估 → 决策续停

关键特性：
- 多轮迭代支持（最大轮次可配置，默认 5）
- 条件分支：根据分析结果决定是否获取新数据
- 评估门禁：训练后评估模型质量
- 自动续停：根据评估结果决定是否继续迭代
"""

from typing import Literal, Any
from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.analysis_agent import analysis_node
from app.agents.acquisition_agent import hunting_node
from app.agents.training_agent import evolution_node
from app.agents.evaluation_agent import evaluation_node
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# EvoLoop 配置常量
DEFAULT_MAX_ROUNDS = 5


def initialize_round_node(state: AgentState) -> AgentState:
    """
    初始化/递增迭代轮次。

    在第一轮时设置初始值。
    在后续轮次递增 round_number。
    """
    round_number = state.get("round_number")

    if round_number is None:
        # First round
        state["round_number"] = 1
        state["max_rounds"] = state.get("max_rounds") or DEFAULT_MAX_ROUNDS
        state["rounds_without_improvement"] = 0
        state["best_metrics"] = {}
        state["best_model_path"] = ""
        logger.info(
            f"EvoLoop 初始化: max_rounds={state['max_rounds']}, "
            f"project_id={state.get('project_id', 'unknown')}"
        )
    else:
        state["round_number"] = round_number + 1
        # Clear per-round state for fresh iteration
        state["acquired_images"] = []
        state["pseudo_labels"] = []
        state["crawled_count"] = 0
        state["search_keywords"] = []
        state["evaluation_metrics"] = {}
        state["continuation_decision"] = {}
        logger.info(f"EvoLoop 轮次递增: round {state['round_number']}")

    logger.info(
        f"=== EvoLoop Round {state['round_number']}/{state.get('max_rounds', DEFAULT_MAX_ROUNDS)} ==="
    )

    return state


def finalize_node(state: AgentState) -> AgentState:
    """
    最终化节点：汇总 EvoLoop 结果。
    """
    round_number = state.get("round_number", 1)
    best_metrics = state.get("best_metrics", {})
    decision = state.get("continuation_decision", {})

    logger.info(
        f"EvoLoop 完成: 共执行 {round_number} 轮, "
        f"最佳 mAP50={best_metrics.get('mAP50', 'N/A')}, "
        f"最终决策={decision.get('reason', 'completed')}"
    )

    state["training_status"] = "completed"
    return state


def should_continue_to_hunter(state: AgentState) -> Literal["hunter", "finalize"]:
    """
    条件边：判断是否需要获取新数据。

    如果分析结果中包含搜索关键词，则继续到 hunter 节点。
    否则跳到最终化。
    """
    search_keywords = state.get("search_keywords", [])
    if search_keywords and len(search_keywords) > 0:
        logger.info(f"Round {state.get('round_number', 1)}: 找到 {len(search_keywords)} 个搜索关键词，继续获取数据")
        return "hunter"
    else:
        logger.warning(f"Round {state.get('round_number', 1)}: 未找到搜索关键词，结束迭代")
        return "finalize"


def should_continue_to_evolution(state: AgentState) -> Literal["evolution", "finalize"]:
    """
    条件边：判断是否有足够的新数据进行训练。
    """
    crawled_count = state.get("crawled_count", 0)
    if crawled_count > 0:
        logger.info(f"Round {state.get('round_number', 1)}: 获取了 {crawled_count} 张新图像，继续训练")
        return "evolution"
    else:
        logger.warning(f"Round {state.get('round_number', 1)}: 未获取新数据，结束迭代")
        return "finalize"


def should_continue_loop(state: AgentState) -> Literal["next_round", "finalize"]:
    """
    条件边：评估后决定是否继续迭代。

    检查:
    1. continuation_decision 是否指示继续
    2. 是否未超过最大轮次限制
    3. 是否需要回滚（回滚后应停止）
    """
    decision = state.get("continuation_decision", {})
    round_number = state.get("round_number", 1)
    max_rounds = state.get("max_rounds", DEFAULT_MAX_ROUNDS)

    # Check rollback (stop immediately)
    if decision.get("should_rollback"):
        logger.warning(
            f"Round {round_number}: 模型退化，执行回滚: {decision.get('reason', '')}"
        )
        return "finalize"

    # Check if we should continue
    if not decision.get("should_continue", False):
        logger.info(
            f"Round {round_number}: 停止迭代: {decision.get('reason', 'no reason given')}"
        )
        return "finalize"

    # Check max rounds
    if round_number >= max_rounds:
        logger.info(
            f"Round {round_number}: 达到最大轮次限制 ({max_rounds})，停止迭代"
        )
        return "finalize"

    # Continue to next round
    logger.info(
        f"Round {round_number}: 继续迭代 -> Round {round_number + 1}"
    )
    return "next_round"


def build_workflow_graph() -> Any:
    """
    构建 EvoLoop 工作流图。

    工作流结构:
    START -> initialize_round -> perception -> [条件] -> hunter -> [条件] -> evolution
         -> evaluation -> [条件: 续停决策]
              -> YES: 回到 initialize_round (递增轮次)
              -> NO: finalize -> END

    Returns:
        编译后的 LangGraph Runnable
    """
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("initialize_round", initialize_round_node)
    workflow.add_node("perception", analysis_node)
    workflow.add_node("hunter", hunting_node)
    workflow.add_node("evolution", evolution_node)
    workflow.add_node("evaluation", evaluation_node)
    workflow.add_node("finalize", finalize_node)

    # 设置入口点
    workflow.set_entry_point("initialize_round")

    # initialize_round -> perception
    workflow.add_edge("initialize_round", "perception")

    # perception -> hunter (条件: 有搜索关键词) 或 finalize
    workflow.add_conditional_edges(
        "perception",
        should_continue_to_hunter,
        {
            "hunter": "hunter",
            "finalize": "finalize"
        }
    )

    # hunter -> evolution (条件: 有新数据) 或 finalize
    workflow.add_conditional_edges(
        "hunter",
        should_continue_to_evolution,
        {
            "evolution": "evolution",
            "finalize": "finalize"
        }
    )

    # evolution -> evaluation
    workflow.add_edge("evolution", "evaluation")

    # evaluation -> 续停决策
    workflow.add_conditional_edges(
        "evaluation",
        should_continue_loop,
        {
            "next_round": "initialize_round",  # Loop back!
            "finalize": "finalize"
        }
    )

    # finalize -> END
    workflow.add_edge("finalize", END)

    # 编译图
    app = workflow.compile()

    logger.info("EvoLoop 工作流图构建完成 (支持多轮迭代)")
    return app


# 全局工作流实例（延迟初始化）
_workflow_app: Any = None


def get_workflow_app() -> Any:
    """
    获取工作流应用实例（单例模式）。
    """
    global _workflow_app
    if _workflow_app is None:
        _workflow_app = build_workflow_graph()
    return _workflow_app


async def run_workflow(initial_state: AgentState) -> AgentState:
    """
    运行 EvoLoop 工作流。

    Args:
        initial_state: 初始 AgentState，必须包含 project_id 和 image_urls

    Returns:
        最终 AgentState（包含所有轮次的累积结果）
    """
    app = get_workflow_app()

    logger.info(
        f"开始 EvoLoop 工作流，项目ID: {initial_state.get('project_id', 'unknown')}"
    )

    # Reset global singleton to ensure fresh graph (in case of config changes)
    global _workflow_app
    _workflow_app = None
    app = get_workflow_app()

    final_state = None
    async for state in app.astream(initial_state):
        for node_name, node_state in state.items():
            logger.debug(f"工作流节点完成: {node_name}")
            final_state = node_state

    if final_state is None:
        final_state = initial_state

    total_rounds = final_state.get("round_number", 1)
    best_map = final_state.get("best_metrics", {}).get("mAP50", "N/A")
    logger.info(
        f"EvoLoop 工作流执行完成: {total_rounds} 轮, 最佳 mAP50={best_map}"
    )

    return final_state

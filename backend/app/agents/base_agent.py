"""
多智能体系统的基础 Agent 类。

此模块提供了 BaseAgent 抽象类，所有专用 Agent 都继承自该类。
这是 IDEATE 框架中智能体层的基础组件。
"""

from abc import ABC, abstractmethod
from typing import Any

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    IDEATE 框架中所有 Agent 的抽象基类。
    
    每个 Agent 负责工作流中的特定任务：
    - InferenceAgent: 对上传的图像运行模型推理
    - AnalysisAgent: 分析结果并生成数据获取策略
    - AcquisitionAgent: 从网络获取新数据
    - TrainingAgent: 触发模型训练
    """

    def __init__(self, agent_name: str) -> None:
        """
        初始化基础 Agent。
        
        Args:
            agent_name: Agent 名称，用于日志记录
        """
        self.agent_name = agent_name
        logger.info(f"{self.agent_name} 已初始化")

    @abstractmethod
    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        执行 Agent 的任务。
        
        这是 Agent 的主要入口点。Orchestrator 调用此方法并传递当前的执行上下文。
        
        Args:
            context: 包含前序 Agent 数据的执行上下文
            
        Returns:
            包含 Agent 输出结果的字典
        """
        pass

    def _log_execution_start(self) -> None:
        """记录 Agent 执行开始。"""
        logger.info(f"{self.agent_name} 开始执行")

    def _log_execution_end(self, result_summary: str = "") -> None:
        """
        记录 Agent 执行结束。
        
        Args:
            result_summary: 可选的执行结果摘要
        """
        msg = f"{self.agent_name} 执行完成"
        if result_summary:
            msg += f": {result_summary}"
        logger.info(msg)

    def _log_error(self, error: Exception) -> None:
        """
        记录 Agent 执行过程中的错误。
        
        Args:
            error: 发生的异常
        """
        logger.error(
            f"{self.agent_name} 执行失败: {error}",
            exc_info=True,
            extra={"agent": self.agent_name}
        )


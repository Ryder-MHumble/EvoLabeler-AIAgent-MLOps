"""
任务编排器，用于协调多智能体工作流。

这是 IDEATE 框架的核心，负责按正确顺序编排所有 Agent 的执行。
实现了从数据上传到模型训练的完整自动化流程。
"""

from typing import Any, Optional
from datetime import datetime

from app.agents.inference_agent import InferenceAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.acquisition_agent import AcquisitionAgent
from app.agents.training_agent import TrainingAgent
from app.tools.supabase_client import SupabaseClient
from app.tools.qwen_api_wrapper import QwenAPIWrapper
from app.tools.web_crawler import WebCrawler
from app.tools.subprocess_executor import SubprocessExecutor
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class JobOrchestrator:
    """
    管理完整 IDEATE 工作流的编排器。
    
    工作流阶段：
    UPLOAD -> INFERENCE -> ANALYSIS -> ACQUISITION -> PSEUDO_LABELING -> TRAINING -> COMPLETE
    
    编排器职责：
    1. 初始化所有必需的 Agent 和工具
    2. 管理工作流状态转换
    3. 在 Agent 之间传递上下文
    4. 处理错误并更新任务状态
    """

    def __init__(self, job_id: str) -> None:
        """
        初始化任务编排器。
        
        Args:
            job_id: 唯一任务标识符
        """
        self.job_id = job_id
        self.context: dict[str, Any] = {"job_id": job_id}
        
        # 初始化工具层
        self.supabase_client = SupabaseClient()
        self.qwen_api = QwenAPIWrapper()
        self.web_crawler = WebCrawler(self.supabase_client)
        self.subprocess_executor = SubprocessExecutor()
        
        # 使用依赖注入初始化 Agent
        self.inference_agent = InferenceAgent(
            subprocess_executor=self.subprocess_executor,
            supabase_client=self.supabase_client
        )
        self.analysis_agent = AnalysisAgent(
            qwen_api=self.qwen_api
        )
        self.acquisition_agent = AcquisitionAgent(
            web_crawler=self.web_crawler,
            subprocess_executor=self.subprocess_executor,
            supabase_client=self.supabase_client
        )
        self.training_agent = TrainingAgent(
            subprocess_executor=self.subprocess_executor,
            supabase_client=self.supabase_client
        )
        
        logger.info(f"任务编排器已初始化，任务ID: {job_id}")

    async def run(self) -> dict[str, Any]:
        """
        执行完整的 IDEATE 工作流。
        
        此方法按顺序编排所有 Agent，在每个阶段更新任务状态，
        并优雅地处理错误。
        
        Returns:
            包含最终工作流结果的字典
        """
        logger.info(f"开始执行工作流，任务ID: {self.job_id}")
        start_time = datetime.utcnow()
        
        try:
            # 阶段 1: 推理
            await self._update_status("INFERENCE", "正在对上传的图像运行推理")
            inference_result = await self.inference_agent.execute(self.context)
            self.context.update(inference_result)
            
            # 阶段 2: 分析
            await self._update_status("ANALYSIS", "正在分析图像并生成搜索策略")
            analysis_result = await self.analysis_agent.execute(self.context)
            self.context.update(analysis_result)
            
            # 阶段 3: 数据获取（包含伪标注）
            await self._update_status("ACQUISITION", "正在从网络获取数据")
            acquisition_result = await self.acquisition_agent.execute(self.context)
            self.context.update(acquisition_result)
            
            # 检查是否获取了足够的数据
            if not acquisition_result.get("dataset_ready", False):
                logger.warning("获取的数据不足，跳过训练")
                await self._update_status(
                    "COMPLETE",
                    "工作流已完成（数据不足，未进行训练）"
                )
                return self._build_final_result(start_time, training_skipped=True)
            
            # 阶段 4: 训练
            await self._update_status("TRAINING", "正在使用获取的数据训练模型")
            training_result = await self.training_agent.execute(self.context)
            self.context.update(training_result)
            
            # 阶段 5: 完成
            await self._update_status("COMPLETE", "工作流成功完成")
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(
                f"工作流已完成，任务ID: {self.job_id}",
                extra={"job_id": self.job_id, "duration_seconds": duration}
            )
            
            return self._build_final_result(start_time)
            
        except Exception as e:
            logger.error(
                f"工作流执行失败，任务ID: {self.job_id}",
                exc_info=True,
                extra={"job_id": self.job_id}
            )
            await self._update_status("FAILED", f"工作流失败: {str(e)}")
            raise

    async def _update_status(
        self,
        status: str,
        message: str,
        metadata_update: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Update job status in database.
        
        Args:
            status: New job status
            message: Progress message
            metadata_update: Optional metadata to update
        """
        try:
            await self.supabase_client.update_job_status(
                job_id=self.job_id,
                status=status,
                progress_message=message,
                metadata_update=metadata_update
            )
            logger.info(
                f"Job status updated: {status}",
                extra={"job_id": self.job_id, "status": status}
            )
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
            # Don't raise - status update failure shouldn't stop workflow

    def _build_final_result(
        self,
        start_time: datetime,
        training_skipped: bool = False
    ) -> dict[str, Any]:
        """
        Build final result summary.
        
        Args:
            start_time: Workflow start time
            training_skipped: Whether training was skipped
            
        Returns:
            Dictionary with workflow summary
        """
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        return {
            "job_id": self.job_id,
            "status": "COMPLETE",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "training_skipped": training_skipped,
            "summary": {
                "images_processed": len(self.context.get("uploaded_images", [])),
                "images_acquired": len(self.context.get("acquired_images", [])),
                "pseudo_labels_generated": len(self.context.get("pseudo_labels", [])),
                "scene_type": self.context.get("scene_type", "unknown"),
                "search_queries_used": len(self.context.get("search_queries", [])),
            }
        }



"""
高级任务编排器 - 支持残差连接和并行执行。

本模块实现了更复杂的编排架构：
1. **残差连接 (Residual Connections)**: Agent 输出保留原始输入
2. **并行执行 (Parallel Execution)**: 独立 Agent 并发运行
3. **条件分支 (Conditional Branching)**: 基于结果的动态路由
4. **反馈循环 (Feedback Loops)**: Agent 输出影响前序步骤
"""

import asyncio
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum

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


class ExecutionMode(str, Enum):
    """执行模式枚举。"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"      # 并行执行
    CONDITIONAL = "conditional"  # 条件执行


class AgentNode:
    """
    Agent 执行节点。
    
    封装单个 Agent 的执行逻辑，支持残差连接。
    """
    
    def __init__(
        self,
        agent: Any,
        name: str,
        enable_residual: bool = True,
        timeout: Optional[int] = None
    ):
        """
        初始化 Agent 节点。
        
        Args:
            agent: Agent 实例
            name: 节点名称
            enable_residual: 是否启用残差连接
            timeout: 超时时间（秒）
        """
        self.agent = agent
        self.name = name
        self.enable_residual = enable_residual
        self.timeout = timeout
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行 Agent 并应用残差连接。
        
        Args:
            context: 输入上下文
            
        Returns:
            输出上下文（包含残差）
        """
        logger.info(f"执行节点: {self.name}")
        start_time = datetime.utcnow()
        
        try:
            # 执行 Agent
            if self.timeout:
                result = await asyncio.wait_for(
                    self.agent.execute(context),
                    timeout=self.timeout
                )
            else:
                result = await self.agent.execute(context)
            
            # 应用残差连接：保留原始上下文
            if self.enable_residual:
                output = {**context, **result}  # 合并，新结果覆盖旧值
                output[f"{self.name}_residual"] = True
            else:
                output = result
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            output[f"{self.name}_duration"] = duration
            
            logger.info(f"节点 {self.name} 执行成功，耗时 {duration:.2f}s")
            return output
            
        except asyncio.TimeoutError:
            logger.error(f"节点 {self.name} 执行超时")
            raise
        except Exception as e:
            logger.error(f"节点 {self.name} 执行失败: {e}", exc_info=True)
            raise


class ParallelGroup:
    """
    并行执行组。
    
    管理一组可并行执行的 Agent 节点。
    """
    
    def __init__(self, nodes: List[AgentNode], name: str = "parallel_group"):
        """
        初始化并行组。
        
        Args:
            nodes: Agent 节点列表
            name: 组名称
        """
        self.nodes = nodes
        self.name = name
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        并行执行所有节点。
        
        Args:
            context: 输入上下文
            
        Returns:
            合并后的输出上下文
        """
        logger.info(f"开始并行执行组: {self.name}, 节点数: {len(self.nodes)}")
        start_time = datetime.utcnow()
        
        # 并发执行所有节点
        tasks = [node.execute(context.copy()) for node in self.nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        merged_context = context.copy()
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"节点 {self.nodes[i].name} 执行失败: {result}")
                errors.append({
                    "node": self.nodes[i].name,
                    "error": str(result)
                })
            else:
                # 合并成功的结果
                merged_context.update(result)
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        merged_context[f"{self.name}_duration"] = duration
        merged_context[f"{self.name}_errors"] = errors
        
        logger.info(f"并行组 {self.name} 执行完成，耗时 {duration:.2f}s")
        
        if errors and len(errors) == len(self.nodes):
            raise RuntimeError(f"并行组 {self.name} 所有节点都失败了")
        
        return merged_context


class AdvancedJobOrchestrator:
    """
    高级任务编排器。
    
    特性：
    - 残差连接：保留中间结果
    - 并行执行：加速独立任务
    - 条件分支：智能决策
    - 反馈循环：质量迭代
    """
    
    def __init__(self, job_id: str) -> None:
        """
        初始化高级编排器。
        
        Args:
            job_id: 任务标识符
        """
        self.job_id = job_id
        self.context: Dict[str, Any] = {"job_id": job_id}
        
        # 初始化工具层
        self.supabase_client = SupabaseClient()
        self.qwen_api = QwenAPIWrapper()
        self.web_crawler = WebCrawler(self.supabase_client)
        self.subprocess_executor = SubprocessExecutor()
        
        # 初始化 Agent
        self._init_agents()
        
        # 初始化执行图
        self._build_execution_graph()
        
        logger.info(f"高级编排器已初始化，任务ID: {job_id}")
    
    def _init_agents(self) -> None:
        """初始化所有 Agent。"""
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
    
    def _build_execution_graph(self) -> None:
        """
        构建执行图。
        
        执行架构：
        
        [上传] 
           ↓
        [推理] (残差连接)
           ↓
        ┌────────────┐
        │ 并行分支   │
        │ ├─ 分析A  │ (场景分析)
        │ └─ 分析B  │ (质量评估)
        └────────────┘
           ↓
        [策略融合] (残差连接)
           ↓
        [数据获取] (条件执行)
           ↓
        [训练] (残差连接 + 反馈)
           ↓
        [完成]
        """
        # 节点定义
        self.node_inference = AgentNode(
            agent=self.inference_agent,
            name="inference",
            enable_residual=True,
            timeout=600
        )
        
        self.node_analysis = AgentNode(
            agent=self.analysis_agent,
            name="analysis",
            enable_residual=True,
            timeout=300
        )
        
        self.node_acquisition = AgentNode(
            agent=self.acquisition_agent,
            name="acquisition",
            enable_residual=True,
            timeout=1800
        )
        
        self.node_training = AgentNode(
            agent=self.training_agent,
            name="training",
            enable_residual=True,
            timeout=7200
        )
        
        logger.info("执行图构建完成")
    
    async def run(self) -> Dict[str, Any]:
        """
        执行高级工作流。
        
        Returns:
            工作流结果
        """
        logger.info(f"开始高级工作流执行，任务ID: {self.job_id}")
        start_time = datetime.utcnow()
        
        try:
            # ========== 阶段 1: 推理 ==========
            await self._update_status("INFERENCE", "正在运行模型推理")
            self.context = await self.node_inference.execute(self.context)
            
            # ========== 阶段 2: 并行分析 ==========
            await self._update_status("ANALYSIS", "正在并行分析图像")
            self.context = await self._parallel_analysis()
            
            # ========== 阶段 3: 条件数据获取 ==========
            should_acquire = self._should_acquire_data()
            
            if should_acquire:
                await self._update_status("ACQUISITION", "正在获取新数据")
                self.context = await self.node_acquisition.execute(self.context)
                
                # 数据质量检查（反馈循环）
                quality_check = self._check_data_quality()
                self.context["quality_check"] = quality_check
                
                if not quality_check["passed"]:
                    logger.warning("数据质量检查未通过，跳过训练")
                    await self._update_status(
                        "COMPLETE",
                        f"工作流完成（数据质量不足: {quality_check['reason']}）"
                    )
                    return self._build_final_result(start_time, training_skipped=True)
            else:
                logger.info("不确定性低，跳过数据获取")
                self.context["acquisition_skipped"] = True
            
            # ========== 阶段 4: 训练（含残差） ==========
            if self.context.get("dataset_ready", False):
                await self._update_status("TRAINING", "正在训练模型")
                self.context = await self.node_training.execute(self.context)
            else:
                logger.info("数据集未就绪，跳过训练")
            
            # ========== 阶段 5: 完成 ==========
            await self._update_status("COMPLETE", "工作流成功完成")
            
            return self._build_final_result(start_time)
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}", exc_info=True)
            await self._update_status("FAILED", f"工作流失败: {str(e)}")
            raise
    
    async def _parallel_analysis(self) -> Dict[str, Any]:
        """
        并行分析阶段。
        
        同时进行多个分析任务，提高效率。
        """
        # 主分析任务
        analysis_result = await self.node_analysis.execute(self.context)
        
        # 可以添加更多并行分析任务
        # 例如：质量评估、元数据提取等
        
        # 这里演示简化版本，实际可以使用 ParallelGroup
        return {**self.context, **analysis_result}
    
    def _should_acquire_data(self) -> bool:
        """
        决策：是否需要获取新数据。
        
        基于不确定性指标和现有数据质量。
        """
        uncertainty_metrics = self.context.get("uncertainty_metrics", {})
        uncertainty_score = uncertainty_metrics.get("uncertainty_score", 0)
        low_conf_ratio = uncertainty_metrics.get("low_confidence_ratio", 0)
        
        # 决策逻辑
        should_acquire = (
            uncertainty_score > 0.3 or  # 高不确定性
            low_conf_ratio > 0.2        # 低置信度样本多
        )
        
        logger.info(
            f"数据获取决策: {should_acquire}",
            extra={
                "uncertainty": uncertainty_score,
                "low_conf_ratio": low_conf_ratio
            }
        )
        
        return should_acquire
    
    def _check_data_quality(self) -> Dict[str, Any]:
        """
        检查获取数据的质量。
        
        实现反馈循环机制。
        """
        acquired_images = self.context.get("acquired_images", [])
        pseudo_labels = self.context.get("pseudo_labels", [])
        
        if len(acquired_images) < 5:
            return {
                "passed": False,
                "reason": "获取图像数量不足 (<5)"
            }
        
        if len(pseudo_labels) < 3:
            return {
                "passed": False,
                "reason": "高质量伪标签不足 (<3)"
            }
        
        # 计算平均质量分数
        if pseudo_labels:
            quality_scores = []
            for label in pseudo_labels:
                detections = label.get("detections", [])
                if detections:
                    avg_conf = sum(d.get("confidence", 0) for d in detections) / len(detections)
                    quality_scores.append(avg_conf)
            
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                if avg_quality < 0.5:
                    return {
                        "passed": False,
                        "reason": f"平均质量分数过低 ({avg_quality:.2f})"
                    }
        
        return {
            "passed": True,
            "quality_score": avg_quality if quality_scores else 0,
            "samples_count": len(acquired_images)
        }
    
    async def _update_status(
        self,
        status: str,
        message: str,
        metadata_update: Optional[Dict[str, Any]] = None
    ) -> None:
        """更新任务状态。"""
        try:
            await self.supabase_client.update_job_status(
                job_id=self.job_id,
                status=status,
                progress_message=message,
                metadata_update=metadata_update
            )
        except Exception as e:
            logger.error(f"状态更新失败: {e}")
    
    def _build_final_result(
        self,
        start_time: datetime,
        training_skipped: bool = False
    ) -> Dict[str, Any]:
        """构建最终结果。"""
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # 收集各阶段耗时
        stage_durations = {
            "inference": self.context.get("inference_duration", 0),
            "analysis": self.context.get("analysis_duration", 0),
            "acquisition": self.context.get("acquisition_duration", 0),
            "training": self.context.get("training_duration", 0),
        }
        
        return {
            "job_id": self.job_id,
            "status": "COMPLETE",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_duration_seconds": duration,
            "stage_durations": stage_durations,
            "training_skipped": training_skipped,
            "architecture": "residual_parallel",  # 标记使用的架构
            "summary": {
                "images_processed": len(self.context.get("uploaded_images", [])),
                "images_acquired": len(self.context.get("acquired_images", [])),
                "pseudo_labels_generated": len(self.context.get("pseudo_labels", [])),
                "scene_type": self.context.get("scene_type", "unknown"),
                "uncertainty_score": self.context.get("uncertainty_metrics", {}).get("uncertainty_score", 0),
                "quality_check": self.context.get("quality_check", {}),
            }
        }


"""
LangGraph AgentState 定义模块。

此模块定义了多智能体系统使用的共享状态结构。
所有 Agent 节点通过 AgentState 进行数据传递和状态管理。
"""

from typing import TypedDict, Optional


class AgentState(TypedDict):
    """
    多智能体系统的共享状态定义。
    
    所有 LangGraph 节点函数接收和返回此类型的状态字典。
    使用 TypedDict 确保类型安全和 IDE 支持。
    """
    
    # 项目标识
    project_id: str
    
    # 图像数据
    image_urls: list[str]  # 当前批次的图像 URL 列表
    
    # 分析结果
    analysis_result: dict  # Qwen VLM 分析输出
    
    # 搜索策略
    search_keywords: list[str]  # 从分析结果提取的搜索关键词
    
    # 数据获取统计
    crawled_count: int  # 已爬取的图像数量
    
    # 训练状态
    training_status: str  # 训练状态（pending/running/completed/failed）
    
    # 错误处理
    errors: list[str]  # 错误信息列表
    
    # 可选字段（用于扩展）
    job_id: Optional[str]  # 任务 ID
    uploaded_images: Optional[list[str]]  # 上传的原始图像
    acquired_images: Optional[list[str]]  # 获取的新图像
    pseudo_labels: Optional[list[dict]]  # 伪标签数据
    uncertainty_metrics: Optional[dict]  # 不确定性指标
    search_queries: Optional[list[str]]  # 搜索查询列表
    scene_type: Optional[str]  # 场景类型
    model_path: Optional[str]  # 模型路径

    # ==================== EvoLoop 迭代控制 ====================
    # 当前迭代轮次（从 1 开始）
    round_number: Optional[int]
    # 最大允许迭代轮次
    max_rounds: Optional[int]

    # ==================== 模型版本管理 ====================
    # 历史最佳模型路径
    best_model_path: Optional[str]
    # 历史最佳模型指标
    best_metrics: Optional[dict]
    # 当前模型版本 UUID
    model_version_id: Optional[str]

    # ==================== 评估结果 ====================
    # 当前轮次评估指标
    evaluation_metrics: Optional[dict]
    # 与最佳模型的对比结果
    model_comparison: Optional[dict]
    # 校准指标 (ECE, MCE)
    calibration_metrics: Optional[dict]
    # 续停决策
    continuation_decision: Optional[dict]

    # ==================== 验证集管理 ====================
    # 固定 holdout 验证集路径
    holdout_validation_set: Optional[list[str]]
    # 验证集哈希（确保跨轮次一致性）
    validation_set_hash: Optional[str]

    # ==================== 防退化追踪 ====================
    # 连续未改善轮次数
    rounds_without_improvement: Optional[int]
    # 数据质量门禁结果
    data_quality_gate_result: Optional[dict]
    # 模型健康报告
    model_health_report: Optional[dict]

    # ==================== 训练扩展 ====================
    # 训练配置（当前轮次）
    training_config: Optional[dict]
    # 课程学习信息
    curriculum_info: Optional[dict]
    # 数据质量指标
    quality_metrics: Optional[dict]


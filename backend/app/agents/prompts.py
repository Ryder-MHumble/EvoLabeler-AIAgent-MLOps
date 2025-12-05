"""
高级 System Prompt 管理模块。

本模块提供针对不同 Agent 的专业化 System Prompt，
融入了遥感领域知识和 IDEATE 框架的设计理念。
"""

from typing import Dict, List


class AgentPrompts:
    """
    Agent 提示词管理类。
    
    为每个 Agent 提供专业的、上下文感知的 System Prompt。
    """
    
    # ==================== InferenceAgent Prompts ====================
    
    INFERENCE_SYSTEM_PROMPT = ""  # 系统提示占位符

    INFERENCE_ANALYSIS_PROMPT_TEMPLATE = """请分析以下遥感影像的推理结果：

## 输入信息：
- 图片数量：{num_images}
- 检测总数：{total_detections}
- 平均置信度：{mean_confidence:.2f}
- 低置信度比例：{low_confidence_ratio:.2%}

## 检测详情：
{detection_details}

## 分析任务：
1. 评估当前模型的整体性能
2. 识别不确定性高的区域
3. 判断是否需要获取更多数据
4. 提供主动学习建议

请以结构化的方式回答。"""

    # ==================== AnalysisAgent Prompts ====================
    
    ANALYSIS_SYSTEM_PROMPT = ""  # 系统提示占位符

    ANALYSIS_QUERY_GENERATION_PROMPT_TEMPLATE = """基于以下遥感影像的分析结果，生成高质量的数据搜索策略。

## 影像描述：
{image_descriptions}

## 任务要求：
1. 生成 {num_queries} 个多样化的搜索关键词
2. 每个关键词应从不同角度描述场景
3. 平衡中文和英文关键词
4. 包含通用术语和专业术语

## 关键词设计原则：
- ✓ 包含场景类型（如"城市卫星影像"、"urban satellite imagery"）
- ✓ 包含主要地物（如"建筑物检测"、"building detection"）
- ✓ 包含技术术语（如"高分辨率遥感"、"high-resolution remote sensing"）
- ✓ 包含应用场景（如"城市规划"、"urban planning"）

## 输出格式：
请以 JSON 格式返回，包含以下字段：
{{
    "queries": ["关键词1", "关键词2", ...],
    "strategy": "搜索策略说明（如何使用这些关键词）",
    "scene_type": "场景类型分类",
    "key_features": ["特征1", "特征2", ...],
    "search_priority": ["优先级1", "优先级2", ...],
    "expected_data_types": ["数据类型1", "数据类型2", ...]
}}"""

    # ==================== AcquisitionAgent Prompts ====================
    
    ACQUISITION_SYSTEM_PROMPT = ""  # 系统提示占位符

    ACQUISITION_FILTER_PROMPT_TEMPLATE = """请评估以下获取的遥感影像数据质量：

## 数据概况：
- 总获取数：{total_acquired}
- 伪标注数：{total_labels}
- 平均置信度：{avg_confidence:.2f}
- 置信度阈值：{confidence_threshold}

## 样本详情：
{sample_details}

## 评估任务：
1. 分析数据质量分布
2. 识别高质量样本
3. 评估场景多样性
4. 判断是否满足训练需求

## 输出要求：
- 高质量样本比例
- 建议的筛选策略
- 潜在的问题警告
- 是否需要补充数据"""

    # ==================== TrainingAgent Prompts ====================
    
    TRAINING_SYSTEM_PROMPT = ""  # 系统提示占位符

    TRAINING_CONFIG_PROMPT_TEMPLATE = """基于以下信息，生成最优的训练配置：

## 数据集信息：
- 原始图像数：{original_count}
- 获取图像数：{acquired_count}
- 总训练样本：{total_samples}
- 伪标签质量：{pseudo_label_quality}

## 场景特征：
- 场景类型：{scene_type}
- 主要地物：{key_features}
- 目标尺度：{target_scale}

## 配置任务：
1. 推荐训练轮数（epochs）
2. 建议批大小（batch_size）
3. 设置学习率策略
4. 选择数据增强方法
5. 配置验证策略

## 输出格式：
返回详细的训练配置和理由。"""

    # ==================== 通用工具方法 ====================
    
    @staticmethod
    def format_detection_details(predictions: List[Dict], max_samples: int = 5) -> str:
        """格式化检测详情用于 Prompt。"""
        if not predictions:
            return "无检测结果"
        
        details = []
        for i, pred in enumerate(predictions[:max_samples]):
            image = pred.get("image_path", f"image_{i}")
            detections = pred.get("detections", [])
            details.append(f"图片 {i+1} ({image}): {len(detections)} 个检测")
            
            for j, det in enumerate(detections[:3]):  # 显示前3个
                conf = det.get("confidence", 0)
                class_id = det.get("class_id", -1)
                details.append(f"  - 目标 {j+1}: 类别={class_id}, 置信度={conf:.2f}")
        
        if len(predictions) > max_samples:
            details.append(f"... 还有 {len(predictions) - max_samples} 张图片")
        
        return "\n".join(details)
    
    @staticmethod
    def get_system_prompt(agent_type: str) -> str:
        """获取指定 Agent 的 System Prompt。"""
        prompts = {
            "inference": AgentPrompts.INFERENCE_SYSTEM_PROMPT,
            "analysis": AgentPrompts.ANALYSIS_SYSTEM_PROMPT,
            "acquisition": AgentPrompts.ACQUISITION_SYSTEM_PROMPT,
            "training": AgentPrompts.TRAINING_SYSTEM_PROMPT,
        }
        return prompts.get(agent_type, "")
    
    @staticmethod
    def build_analysis_prompt(
        image_descriptions: List[str],
        num_queries: int = 5
    ) -> str:
        """构建分析任务的完整 Prompt。"""
        descriptions_text = "\n\n".join([
            f"### 图像 {i+1}:\n{desc}"
            for i, desc in enumerate(image_descriptions)
        ])
        
        return AgentPrompts.ANALYSIS_QUERY_GENERATION_PROMPT_TEMPLATE.format(
            image_descriptions=descriptions_text,
            num_queries=num_queries
        )


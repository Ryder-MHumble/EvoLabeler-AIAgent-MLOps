# EvoLabeler - AI Agent Driven MLOps Engine

<div align="center">

<img src="docs/images/logo.png" alt="EvoLabeler Logo" width="200"/>

**🚀 基于多智能体的自进化遥感影像目标检测 MLOps 引擎**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.13+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.4-brightgreen)](https://vuejs.org/)
[![Electron](https://img.shields.io/badge/Electron-28-blue)](https://www.electronjs.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[English](README_EN.md) | [中文文档](README.md)

</div>

---

## 📖 项目简介

**EvoLabeler** 是基于 **IDEATE (Iterative Data Engine via Agentic Task Execution)** 框架的创新型 MLOps 系统，通过多智能体协作实现遥感影像目标检测的完全自动化闭环。

### 🎯 核心特性

- **🤖 Multi-Agent 架构**: 4个专业化Agent协同工作
- **🔄 自动化闭环**: 从数据上传到模型训练全自动
- **🧠 LLM驱动决策**: 智能分析和策略规划
- **🌐 主动学习**: 基于不确定性的智能数据获取
- **📊 半监督学习**: 高质量伪标注生成与课程学习
- **🔗 残差架构**: 信息保留和并行执行
- **📁 协同工作区**: 智能标注和 Agent 监控
- **🖼️ 智能标注**: 真实缩放支持（0.25x-5x）、图像上传、YOLO/JSON导出、多工具编辑
- **📊 项目特定数据**: 每个项目独立的训练指标和配置
- **📸 智能封面**: 自动使用第一张上传图片作为项目封面

---

## 🔬 核心算法与学术创新

### 主动学习 (Active Learning)

基于信息熵的不确定性量化方法，实现智能样本选择：

```python
# 熵值计算：H = -Σ p(x) * log(p(x))
def calculate_entropy(confidence: float) -> float:
    if confidence <= 0 or confidence >= 1:
        return 0.0
    p, q = confidence, 1 - confidence
    return -(p * math.log2(p) + q * math.log2(q))

# 主动学习决策
requires_more_data = (
    uncertainty_score > 0.3 or       # 不确定性阈值
    low_confidence_ratio > 0.2 or    # 低置信度比例
    boundary_sample_ratio > 0.2      # 边界样本比例
)
```

**创新点**：
- 多维度不确定性评估（熵值 + 置信度 + 边界样本）
- 自适应采样阈值机制
- 高价值样本自动识别

### 半监督学习 (Semi-Supervised Learning)

伪标注 + 质量评估 + 课程学习的完整管线：

```python
# 质量评分公式
quality_score = (
    0.5 * avg_confidence +           # 平均置信度
    0.3 * high_confidence_ratio +    # 高置信度比例
    0.2 * consistency_score          # 一致性分数
)

# 课程学习排序（先易后难）
sorted_samples = sort_by_quality(pseudo_labels, descending=True)
```

**创新点**：
- 基于置信度的自适应伪标注策略
- 多维度质量评分机制
- 多样性感知的样本选择
- 课程学习（Curriculum Learning）集成

### 弱监督微调 (Weakly Supervised Fine-tuning)

针对伪标签的优化训练策略：

```python
# 弱监督配置
weak_supervision_config = {
    "pseudo_label_weight": 0.3,      # 伪标签损失权重
    "confidence_weighted": True,      # 置信度加权损失
    "min_confidence": 0.5,           # 最小置信度阈值
}
```

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (Electron Desktop)                │
│       Vue3 + TypeScript + GSAP + Element Plus               │
│         项目仪表盘 | 工作区监控 | 协同工作区 | Agent可视化        │
│      数据流管理 | 智能画布(缩放/上传/导出) | Agent分析面板       │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │          AdvancedJobOrchestrator (编排层)                │ │
│ │  - 残差连接  - 并行执行  - 条件分支  - 反馈循环              │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌────────┬──────────┬──────────────┬────────────┐          │
│ │Inference│Analysis │Acquisition   │Training    │  Agents  │
│ │Agent   │Agent    │Agent         │Agent        │          │
│ │主动学习 │智能决策   │半监督学习      │课程学习      │          │
│ └────────┴──────────┴──────────────┴────────────┘          │
│ ┌────────┬──────────┬──────────────┬────────────┐          │
│ │Supabase│QwenAPI   │WebCrawler    │Subprocess  │  Tools    │
│ │Client  │Wrapper   │(Playwright)  │Executor    │           │
│ └────────┴──────────┴──────────────┴────────────┘          │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                    MCP Tool Registry                    │ │
│ │        场景分类 | 关键词优化 | 质量评估 | 不确定性量化        │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              External Services / Storage                    │
│  Supabase DB  |  硅基流动API  |  YOLO Scripts  |  Storage    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔬 工作流程

### 完整流程图

```
用户上传 ZIP
    ↓
[UPLOAD] 解压验证
    ↓
[INFERENCE] 模型推理 (残差连接)
    ├─ 检测结果
    ├─ 不确定性评估 (熵值计算)
    └─ 主动学习信号 (高价值样本识别)
    ↓
[ANALYSIS] VLM+LLM分析 (残差+并行)
    ├─ 场景分类 (MCP工具)
    ├─ 语义提取
    ├─ 搜索策略生成
    └─ 智能决策 (是否需要更多数据)
    ↓
[条件分支] 基于主动学习信号判断
    ├─ 是 → [ACQUISITION]
    │         ├─ Web爬取 (Playwright)
    │         ├─ 伪标注 (半监督学习)
    │         ├─ 质量评估 (多维度评分)
    │         └─ 多样性过滤
    │         ↓
    │      [质量检查] (反馈循环)
    │         ├─ 通过 → 继续
    │         └─ 不通过 → 补充/结束
    │
    └─ 否 → 跳过获取
    ↓
[TRAINING] 模型训练 (残差连接)
    ├─ 课程学习排序 (先易后难)
    ├─ 弱监督微调配置
    ├─ 自适应训练参数
    └─ 训练监控
    ↓
[COMPLETE] 完成
```

### 关键学术概念实现

| 概念 | 实现位置 | 核心算法 |
|------|---------|---------|
| **主动学习** | InferenceAgent | 熵值不确定性、边界样本检测 |
| **半监督学习** | AcquisitionAgent | 伪标注生成、质量评分 |
| **课程学习** | TrainingAgent | 按难度排序、分阶段训练 |
| **弱监督微调** | TrainingAgent | 置信度加权损失、自适应参数 |
| **LLM决策** | AnalysisAgent | 智能数据获取判断 |
| **残差连接** | AdvancedOrchestrator | 信息保留和梯度流动 |

---

## 📁 项目结构

```
EvoLabeler/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── agents/            # 智能体层 (核心算法)
│   │   │   ├── inference_agent.py   # 主动学习实现
│   │   │   ├── analysis_agent.py    # LLM决策实现
│   │   │   ├── acquisition_agent.py # 半监督学习实现
│   │   │   ├── training_agent.py    # 课程学习实现
│   │   │   └── prompts.py           # System Prompt
│   │   ├── services/          # 服务层
│   │   │   └── advanced_orchestrator.py  # 残差+并行编排
│   │   ├── tools/             # 工具层
│   │   │   ├── mcp_tools.py         # MCP工具集成
│   │   │   └── web_crawler.py       # 数据爬取
│   │   └── api/               # API层
│   └── docs/                  # 文档
├── evolauncher-frontend/      # 前端 Electron 应用
│   ├── src/
│   │   ├── views/            # 视图组件
│   │   │   ├── DashboardView.vue      # 仪表盘
│   │   │   ├── WorkspaceView.vue      # 工作区
│   │   │   └── CoPilotWorkspaceView.vue # 协同工作区
│   │   ├── components/       # UI 组件
│   │   │   ├── dashboard/    # 仪表盘模块
│   │   │   ├── workspace/    # 工作区模块
│   │   │   └── copilot/      # 协同工作区模块
│   │   └── store/            # 状态管理
│   └── README.md             # 前端文档
├── docs/                      # 项目文档
│   └── images/               # 图片资源
└── README.md                  # 本文件
```

---

## 🚀 快速开始

### 环境要求

- Python 3.13+
- Poetry (包管理)
- Supabase 账号
- 硅基流动 API Key

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/Ryder-MHumble/EvoLabeler-AIAgent-MLOps.git
cd EvoLabeler-AIAgent-MLOps

# 2. 安装后端依赖
cd backend
poetry install
poetry run playwright install

# 3. 配置环境
cp .env.example .env
# 编辑 .env 填入你的API密钥

# 4. 初始化数据库
poetry run python scripts/setup_database.py

# 5. 启动后端服务
poetry run python run.py
```

### 启动前端

```bash
# 开发模式
cd evolauncher-frontend
npm install
npm run electron:dev

# 构建生产版本
npm run build:mac
```

### 访问服务

- **后端 API文档**: http://localhost:8000/docs
- **前端应用**: Electron 桌面窗口自动打开

---

## 📸 应用截图

<table>
  <tr>
    <td align="center"><b>仪表盘 - 项目管理</b></td>
    <td align="center"><b>工作区监控 - 训练详情</b></td>
    <td align="center"><b>协同工作区 - 智能标注</b></td>
  </tr>
  <tr>
    <td><img src="docs/images/home.png" alt="仪表盘" /></td>
    <td><img src="docs/images/ProjectDetails.png" alt="工作区" /></td>
    <td><img src="docs/images/SmartCanvas.png" alt="智能画布" /></td>
  </tr>
  <tr>
    <td align="center"><i>项目卡片展示、系统指标统计、GSAP动画效果</i></td>
    <td align="center"><i>进化任务监视器、YOLO训练指标、损失曲线、Agent遥测</i></td>
    <td align="center"><i>数据流管理、智能画布、标注工具、Agent分析、实时终端</i></td>
  </tr>
</table>

---

### 数据库初始化

```bash
# 创建项目表 (在 Supabase SQL Editor 中执行)
# 运行: backend/app/db/migrations/002_create_projects_table.sql

# 插入测试数据
cd backend
poetry run python scripts/insert_test_projects.py
```

---

## 📖 详细文档

### 后端文档
- [后端 API 文档](backend/docs/API.md) - 包含项目和任务管理接口
- [架构设计](backend/docs/ARCHITECTURE.md)
- [数据库设计](backend/app/db/DATABASE_DESIGN.md)
- [项目表迁移 SQL](backend/app/db/migrations/002_create_projects_table.sql)

### 前端文档
- [前端 README](evolauncher-frontend/README.md)
- [快速开始](evolauncher-frontend/QUICKSTART.md)
- [协同工作区功能](evolauncher-frontend/CO_PILOT_FEATURES.md)

### 核心功能亮点

**智能画布标注系统：**
- ✅ 真实缩放支持，标注框自动随图像缩放（0.25x - 5x）
- ✅ 支持拖拽或点击上传本地图像
- ✅ 标注导出支持 YOLO 格式（txt + classes.txt）和 JSON 格式
- ✅ 多工具编辑：选择工具(V)、绘制工具(B)、平移工具(H)
- ✅ 完整快捷键支持：V/B/H切换工具、+/-缩放、0重置、空格确认、Del删除
- ✅ 精确编辑：8个调整手柄、拖拽移动、标签选择

**项目特定数据管理：**
- ✅ 每个项目独立的训练数据和指标
- ✅ 可配置的模型架构（YOLO v5-11、TDA-YOLO）
- ✅ 独立的训练参数配置（批量大小、学习率、输入尺寸）
- ✅ 实时硬件资源监控（GPU显存、利用率）
- ✅ 动态训练进度和指标趋势
- ✅ 可配置的损失曲线收敛特性

**项目创建向导：**
- ✅ 四步向导式创建流程
- ✅ 批量图片上传支持
- ✅ 自动封面生成（使用第一张上传图片）
- ✅ 多种YOLO模型选择（YOLOv5-11、TDA-YOLO）
- ✅ 灵活的模型规模配置（Nano - XLarge）
- ✅ 可选的自定义预训练权重上传

---

## 🛠️ 技术栈

### 后端

- **框架**: FastAPI 0.115
- **数据库**: Supabase (PostgreSQL)
- **LLM/VLM**: 硅基流动 API (Qwen)
- **爬虫**: Playwright
- **验证**: Pydantic V2

### 前端

- **桌面框架**: Electron 28
- **前端框架**: Vue 3.4 (Composition API)
- **构建工具**: Vite 5.0
- **UI 库**: Element Plus 2.5
- **动画**: GSAP 3.12
- **状态管理**: Pinia 2.1
- **路由**: Vue Router 4.2
- **国际化**: Vue I18n 9.9

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

- FastAPI 团队
- Supabase 社区
- 硅基流动API
- Playwright 项目
- 所有开源贡献者

---

## ⭐ Star History

如果这个项目对你有帮助，请给个 Star ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=Ryder-MHumble/EvoLabeler-AIAgent-MLOps&type=Date)](https://star-history.com/#Ryder-MHumble/EvoLabeler-AIAgent-MLOps&Date)

---

<div align="center">

**Made with ❤️ by Ryder Sun**

</div>

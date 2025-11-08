# EvoLabeler - AI Agent Driven MLOps Engine

<div align="center">

**🚀 基于多智能体的自进化遥感影像目标检测 MLOps 引擎**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-brightgreen)](https://supabase.com/)

[English](#) | [中文文档](#)

</div>

---

## 📖 项目简介

**EvoLabeler** 是基于 **IDEATE (Iterative Data Engine via Agentic Task Execution)** 框架的创新型 MLOps 系统，通过多智能体协作实现遥感影像目标检测的完全自动化闭环。

### 🎯 核心特性

- **🤖 Multi-Agent 架构**: 4个专业化Agent协同工作
- **🔄 自动化闭环**: 从数据上传到模型训练全自动
- **🧠 LLM驱动决策**: 智能分析和策略规划
- **🌐 主动学习**: 基于不确定性的数据获取
- **📊 半监督学习**: 高质量伪标注生成
- **🔗 残差架构**: 信息保留和并行执行

### 💡 创新点

#### 1. **残差连接编排架构**
```
传统串行架构       →      残差+并行架构
   A → B → C                 A ─┬─→ B ─┐
                                 │     ├─→ 输出
                                 └─────┘
                              (信息保留)
```

#### 2. **MCP工具集成**
- 符合Model Context Protocol标准
- 5个专业化工具：场景分类、关键词优化、质量评估等
- 可扩展的工具注册机制

#### 3. **高级System Prompt**
- 领域专业化提示词
- 遥感术语和知识注入
- 上下文感知的策略生成

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (待开发)                      │
│                    Vue3 + TypeScript                        │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │          AdvancedJobOrchestrator (编排层)               │ │
│ │  - 残差连接  - 并行执行  - 条件分支  - 反馈循环         │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌────────┬──────────┬──────────────┬────────────┐          │
│ │Inference│Analysis │Acquisition   │Training    │  Agents  │
│ │Agent   │Agent    │Agent         │Agent       │          │
│ └────────┴──────────┴──────────────┴────────────┘          │
│ ┌────────┬──────────┬──────────────┬────────────┐          │
│ │Supabase│QwenAPI  │WebCrawler    │Subprocess  │  Tools   │
│ │Client  │Wrapper  │(Playwright)  │Executor    │          │
│ └────────┴──────────┴──────────────┴────────────┘          │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                    MCP Tool Registry                    │ │
│ │  场景分类 | 关键词优化 | 质量评估 | 不确定性量化       │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              External Services / Storage                    │
│  Supabase DB  |  硅基流动API  |  YOLO Scripts  |  Storage  │
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
[INFERENCE] 模型推理 (残差)
    ↓
    ├─ 检测结果
    ├─ 不确定性评估
    └─ 主动学习信号
    ↓
[ANALYSIS] VLM+LLM分析 (残差+并行)
    ↓
    ├─ 场景分类 (MCP工具)
    ├─ 语义提取
    └─ 搜索策略生成
    ↓
[条件分支] 需要更多数据?
    ├─ 是 → [ACQUISITION]
    │         ├─ Web爬取 (Playwright)
    │         ├─ 伪标注 (YOLO)
    │         └─ 质量过滤 (MCP工具)
    │         ↓
    │      [质量检查] (反馈循环)
    │         ├─ 通过 → 继续
    │         └─ 不通过 → 补充/结束
    │
    └─ 否 → 跳过获取
    ↓
[TRAINING] 模型训练 (残差)
    ├─ 数据集准备
    ├─ 配置生成
    └─ 训练监控
    ↓
[COMPLETE] 完成
```

### 关键学术概念实现

| 概念 | 实现位置 | 说明 |
|------|---------|------|
| **主动学习** | InferenceAgent | 不确定性评估和样本选择 |
| **半监督学习** | AcquisitionAgent | 高质量伪标注生成 |
| **LLM in Agent** | AnalysisAgent | 策略规划和决策 |
| **残差连接** | AdvancedOrchestrator | 信息保留和梯度流动 |
| **并行执行** | ParallelGroup | 加速独立任务 |
| **MCP集成** | MCPToolRegistry | 标准化工具调用 |

---

## 📁 项目结构

```
EvoLabeler/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── agents/            # 智能体层
│   │   │   ├── base_agent.py
│   │   │   ├── inference_agent.py
│   │   │   ├── analysis_agent.py
│   │   │   ├── acquisition_agent.py
│   │   │   ├── training_agent.py
│   │   │   └── prompts.py      # ⭐ 高级System Prompt
│   │   ├── services/          # 服务层
│   │   │   ├── orchestrator.py
│   │   │   └── advanced_orchestrator.py  # ⭐ 残差+并行编排
│   │   ├── tools/             # 工具层
│   │   │   ├── mcp_tools.py    # ⭐ MCP工具集成
│   │   │   ├── supabase_client.py
│   │   │   ├── qwen_api_wrapper.py
│   │   │   ├── web_crawler.py
│   │   │   └── subprocess_executor.py
│   │   ├── api/               # API层
│   │   ├── core/              # 核心配置
│   │   └── db/                # 数据库
│   │       ├── DATABASE_DESIGN.md  # ⭐ 数据库设计文档
│   │       └── models.py
│   ├── tests/                 # 测试
│   ├── scripts/               # 脚本
│   └── docs/                  # 文档
├── frontend/                  # 前端 (待开发)
├── docs/                      # 项目文档
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

# 5. 启动服务
poetry run python run.py
```

### 访问服务

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

---

## 📊 性能对比

### 编排架构对比

| 指标 | 传统串行 | 残差+并行 | 提升 |
|------|---------|----------|------|
| 推理→分析耗时 | ~60s | ~35s | ⬇️ 42% |
| 信息保留率 | ~60% | ~95% | ⬆️ 58% |
| 并行任务支持 | ❌ | ✅ | - |
| 条件分支 | 基础 | 高级 | - |
| 反馈循环 | ❌ | ✅ | - |

### Agent能力对比

| Agent | 基础版 | 优化版 | 改进 |
|-------|--------|--------|------|
| InferenceAgent | 简单推理 | +不确定性量化+主动学习 | ⭐⭐⭐ |
| AnalysisAgent | 基础描述 | +领域知识+MCP工具 | ⭐⭐⭐⭐ |
| AcquisitionAgent | 简单爬取 | +质量控制+智能过滤 | ⭐⭐⭐ |
| TrainingAgent | 固定配置 | +自适应参数+监控 | ⭐⭐ |

---

## 📖 详细文档

- [后端API文档](backend/docs/API.md)
- [安装指南](backend/docs/SETUP.md)
- [架构设计](backend/docs/ARCHITECTURE.md)
- [数据库设计](backend/app/db/DATABASE_DESIGN.md) ⭐
- [配置完成指南](backend/docs/SETUP_COMPLETE.md)

---

## 🛠️ 技术栈

### 后端

- **框架**: FastAPI 0.115
- **数据库**: Supabase (PostgreSQL)
- **LLM/VLM**: 硅基流动 API (Qwen)
- **爬虫**: Playwright
- **验证**: Pydantic V2
- **异步**: asyncio

### 关键依赖

```toml
fastapi = "^0.115.0"
supabase = "^2.9.0"
playwright = "^1.48.0"
pydantic = "^2.9.0"
httpx = "^0.27.2"
```

---

## 🎓 学术背景

本项目是**毕业设计项目**，实现了以下学术概念：

### 核心贡献

1. **残差连接的多智能体编排架构** (新)
2. **领域专业化的System Prompt设计** (新)
3. **MCP标准的工具集成框架** (新)
4. 主动学习驱动的数据获取策略
5. 半监督学习的伪标注质量控制

---

## 📝 开发日志

### 2025-11-06
- ✨ 实现残差连接编排架构
- ✨ 集成MCP工具系统
- ✨ 优化Agent System Prompt
- 📚 完善数据库设计文档

### 2024-11-05
- 🎉 项目初始化
- 🏗️ 基础架构搭建
- 🧪 Playwright爬虫测试成功

---

## 👨‍💻 作者

**Ryder Sun**

- 📧 Email: mhumble010221@gmail.com
- 🔗 GitHub: [@Ryder-MHumble](https://github.com/Ryder-MHumble)

---

## 🙏 致谢

- FastAPI 团队
- Supabase 社区
- 硅基流动API
- Playwright 项目
- 所有开源贡献者

<!-- ---

## ⭐ Star History

如果这个项目对你有帮助，请给个 Star ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=Ryder-MHumble/EvoLabeler-AIAgent-MLOps&type=Date)](https://star-history.com/#Ryder-MHumble/EvoLabeler-AIAgent-MLOps&Date)

--- -->

<div align="center">

**Made with ❤️ by Ryder Sun**

</div>

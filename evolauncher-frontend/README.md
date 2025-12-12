# EvoLabeler Frontend - Electron Desktop Application

<div align="center">

**🎨 AI Agent 驱动的遥感影像标注系统 - 桌面端**

[![Electron](https://img.shields.io/badge/Electron-28.2-blue)](https://www.electronjs.org/)
[![Vue](https://img.shields.io/badge/Vue-3.4-brightgreen)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[English](#) | [中文文档](#)

</div>

---

## 📖 项目简介

**EvoLabeler Frontend** 是 [EvoLabeler](../README.md) 系统的**桌面客户端**，基于 Electron + Vue 3 + TypeScript 构建，为用户提供流畅、现代化的 MLOps 工作流可视化体验。

### 🎯 核心特性

- **🖥️ 原生桌面体验**: Electron 无边框窗口 + 自定义标题栏
- **🎨 Premium UI/UX**: GSAP 驱动的专业级动画系统
- **🌓 双主题系统**: 精心设计的明暗主题，平滑切换
- **🌐 国际化**: 完整的中英文支持
- **📊 实时监控**: 多 Agent 协同工作流可视化
- **🔧 MCP 工具集成**: Model Context Protocol 工具注册表展示
- **⚡ 高性能**: 硬件加速动画，60fps 流畅运行

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────┐
│                  Electron Main Process              │
│                 (main.ts + preload.ts)              │
└────────────────────┬────────────────────────────────┘
                     │ IPC
┌────────────────────▼────────────────────────────────┐
│              Vue 3 Renderer Process                 │
│ ┌─────────────────────────────────────────────────┐ │
│ │          Router (Vue Router 4)                  │ │
│ │  /dashboard  |  /workspace                      │ │
│ └─────────────────────────────────────────────────┘ │
│ ┌───────────┬──────────────┬─────────────────────┐ │
│ │ Pinia     │ Vue I18n     │ Element Plus        │ │
│ │ (State)   │ (i18n)       │ (UI Components)     │ │
│ └───────────┴──────────────┴─────────────────────┘ │
│ ┌─────────────────────────────────────────────────┐ │
│ │        GSAP Animation Engine                    │ │
│ │   Stagger Effects | Smooth Transitions          │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────┐
│              Backend FastAPI Server                 │
│         (See ../backend/README.md)                  │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求

- **Node.js**: 18+ 或 20+
- **包管理器**: npm / yarn / pnpm
- **操作系统**: macOS / Windows / Linux

### 安装步骤

```bash
# 1. 进入前端目录
cd evolauncher-frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

### Electron 开发模式

```bash
# 同时启动 Vite + Electron
npm run electron:dev
```

**开发模式特性:**
- ✅ 热模块替换 (HMR)
- ✅ DevTools 自动打开
- ✅ 代码变更实时重载

### 生产构建

```bash
# 构建 Web 资源
npm run build

# 构建 Electron 安装包
npm run electron:build
```

构建产物将输出到 `release/` 目录。

---

## 📁 项目结构

```
evolauncher-frontend/
├── electron/                        # Electron 主进程
│   ├── main.ts                      # 主进程入口
│   └── preload.ts                   # 预渲染Bridge
│
├── src/                             # 主要源码目录
│   ├── api/
│   │   ├── types.ts                 # API/Mock通用类型定义
│   │   ├── projects.ts              # 项目API客户端
│   │   └── mocks/                   # 前端 User Story Mock 数据
│   │       ├── mock_missions.ts     # 任务Mock数据
│   │       ├── mock_stream.ts       # 图像数据流Mock
│   │       └── mock_logs.ts         # Agent日志Mock
│   │
│   ├── components/
│   │   ├── layout/                  # 布局组件
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppSidebar.vue
│   │   │   └── AppErrorBoundary.vue
│   │   ├── common/                  # 通用组件
│   │   │   ├── AnimatedCard.vue
│   │   │   ├── LoadingSkeleton.vue
│   │   │   ├── StatusBadge.vue
│   │   │   └── ThemeToggle.vue
│   │   ├── dashboard/               # 仪表盘模块化组件 (新)
│   │   │   ├── HeroSection.vue      # 英雄区块
│   │   │   ├── ProjectCard.vue      # 项目卡片
│   │   │   ├── ProjectList.vue      # 项目列表
│   │   │   └── AgentStatusList.vue  # Agent状态列表
│   │   ├── copilot/                 # 协同工作区模块化组件 (新)
│   │   │   └── WorkspaceHeader.vue  # 工作区头部
│   │   ├── project/                 # 项目相关组件
│   │   │   └── CreateProjectWizard.vue
│   │   └── workspace/               # 工作区模块化组件 (新)
│   │       ├── types.ts             # 类型定义
│   │       ├── EvolutionMonitor.vue # 进化任务监视器
│   │       ├── YoloMetricsCard.vue  # YOLO训练指标
│   │       ├── LossChartCard.vue    # 损失曲线图
│   │       ├── TrainingDetailsCard.vue # 训练详情
│   │       ├── AgentTelemetryPanel.vue # Agent遥测面板
│   │       ├── McpToolsPanel.vue    # MCP工具面板
│   │       ├── DataInbox.vue        # 左-数据流(收件箱)
│   │       ├── SmartCanvas.vue      # 中-智能画布
│   │       ├── AgentPanel.vue       # 右-Agent分析与进度
│   │       ├── LiveTerminal.vue     # 全局Agent终端
│   │       └── SeedUploadZone.vue
│   │
│   ├── store/                       # Pinia 状态管理
│   │   ├── app.ts                   # 应用全局状态
│   │   └── mission.ts                # 任务/数据流/Agent日志管理
│   │
│   ├── views/
│   │   ├── DashboardView.vue        # 仪表盘页
│   │   ├── WorkspaceView.vue        # 工作区页面（任务监控）
│   │   └── CoPilotWorkspaceView.vue # 协同工作区（数据流+画布+Agent）
│   │
│   ├── assets/
│   │   └── styles/                  # 全局样式/主题（SCSS/Tailwind等）
│   │       ├── _variables.scss     
│   │       ├── themes.scss          
│   │       └── base.scss            
│   │
│   ├── composables/                 # 组合式Hooks
│   │   └── useTheme.ts
│   │
│   ├── router/                      # 路由配置
│   ├── locales/                     # 国际化
│   │   ├── zh-CN.json
│   │   └── en.json
│   ├── App.vue                      # 应用根组件
│   └── main.ts                      # 入口
│
├── package.json
├── tailwind.config.js
├── vite.config.ts
└── README.md
```

---

## 🎨 设计系统

### 配色方案

#### Light Theme (明亮主题)
```scss
--color-bg: #F7F8FC;              // 背景色
--color-surface: #FFFFFF;         // 表面色
--color-primary: #4A69FF;         // 主色调
--color-text-primary: #1F2937;    // 主文本
```

#### Dark Theme (暗黑主题)
```scss
--color-bg: #1A1B26;              // 背景色
--color-surface: #24283B;         // 表面色
--color-primary: #7AA2F7;         // 主色调
--color-text-primary: #C0CAF5;    // 主文本
```

### 动画原则

1. **60fps 优先**: 所有动画使用 `transform` 和 `opacity`
2. **专业缓动**: `cubic-bezier(0.25, 0.1, 0.25, 1)`
3. **Stagger 效果**: 卡片列表逐个动画进场
4. **硬件加速**: `will-change` + `translateZ(0)`

### 字体系统

- **主字体**: Inter (system fallback)
- **代码字体**: Menlo / Monaco / Courier New
- **字号范围**: 12px - 36px (模块化比例)

---

## 🎯 核心功能

### 1. 项目仪表盘 (`DashboardView`)

**功能亮点:**
- 🗂️ 项目卡片网格展示
- 📊 系统指标统计（Active Loops、Accuracy、Latency）
- 🎬 GSAP Stagger 入场动画
- 🎨 项目状态实时更新
- 📸 **智能封面**：创建项目时，第一张上传的图片自动作为项目封面

**关键组件:**
```vue
<AnimatedCard
  v-for="project in projects"
  :key="project.id"
  @click="openProject(project)"
/>
```

**项目创建功能:**
- ✅ 四步向导式创建流程
- ✅ 批量图片上传支持
- ✅ 自动封面生成（使用第一张上传图片）
- ✅ 多种YOLO模型选择（YOLOv5-11、TDA-YOLO）
- ✅ 灵活的模型规模配置（Nano - XLarge）
- ✅ 可选的自定义预训练权重上传

### 2. 工作区监控 (`WorkspaceView`)

**功能亮点:**
- 📈 进化任务监视器（6 步流程可视化）
- 🤖 Multi-Agent 遥测（4 个 Agent 状态）
- 🔧 MCP 工具注册表（5 个工具实时监控）
- 📝 实时日志流
- 📊 训练指标可视化（YOLO mAP、损失曲线）
- 🎯 **项目特定数据支持**：每个项目显示独立的训练数据和指标
- 🎬 **动态更新**：不同项目展示差异化的模型架构、训练配置、损失曲线特性

**项目特定功能:**
- ✅ 支持多项目独立数据管理
- ✅ 每个项目可配置不同的模型架构（YOLO系列）
- ✅ 独立的训练参数配置（批量大小、学习率、输入尺寸）
- ✅ 独立的数据集信息和类别定义
- ✅ 实时硬件资源监控（GPU显存、利用率）
- ✅ 动态训练进度和指标趋势
- ✅ 可配置的损失曲线收敛特性

**布局:**
```
┌─────────────────────────────────────────────┐
│ 进化任务监视器 │  YOLO指标 & 损失曲线 │ 训练详情 │
│   (6 Steps)   │  动态更新            │项目特定 │
│               │  Agent 遥测          │        │
│               │  MCP 注册表          │        │
└─────────────────────────────────────────────┘
```

### 3. 协同工作区 (`CoPilotWorkspaceView`)

**功能亮点:**
- 📥 数据流管理（Incoming/Pending/Library 分类）
- 🎨 智能画布（图像显示 + 边界框覆盖层 + 真实缩放支持）
- 📤 图像上传与标注导出（支持本地图像标注 + YOLO/JSON格式导出）
- 🔍 高级标注工具（缩放 0.25x-5x、平移、选择、绘制）
- 🤖 Agent 分析面板（VLM 分析结果 + 置信度）
- 💻 实时终端（Agent 思考过程日志）

**布局:**
```
┌─────────────────────────────────────────────┐
│ 数据流 │        智能画布        │ Agent分析 │
│(左侧)  │    (图像+边界框)      │  (右侧)   │
│        │  • 缩放/平移/标注      │           │
│        │  • 上传/导出          │           │
├─────────────────────────────────────────────┤
│           实时终端 (底部可折叠)              │
└─────────────────────────────────────────────┘
```

**核心组件:**
- **DataInbox**: 三分类数据流（新到达/待确认/已归档），置信度颜色编码
- **SmartCanvas 智能画布**: 
  - ✨ **真实缩放支持**：标注框随图像缩放自动调整位置和大小，实现像素级精确标注
  - 🖼️ **图像上传**：支持拖拽或点击上传本地图像进行标注，空状态也可直接上传
  - 📊 **标注导出**：
    - YOLO 格式：生成 `.txt` 标注文件和 `classes.txt` 类别文件
    - JSON 格式：包含归一化坐标和像素坐标的完整标注信息
  - 🛠️ **多种工具**：
    - 选择工具 (V)：点选、移动、调整标注框大小
    - 绘制工具 (B)：框选创建新的标注区域
    - 平移工具 (H)：拖拽移动画布视图
  - 🔍 **缩放控制**：
    - 缩放范围：0.25x - 5x（25% - 500%）
    - 滚轮缩放：Ctrl/Cmd + 滚轮
    - 快捷键：+/- 增减缩放，0 重置视图
  - ⌨️ **完整快捷键支持**：
    - `V` - 选择工具
    - `B` - 绘制工具
    - `H` - 平移工具
    - `+/-` - 缩放
    - `0` - 重置视图
    - `空格` - 确认当前标注
    - `Del` - 删除选中标注
  - 📐 **精确编辑**：
    - 8个调整手柄（四角+四边中点）
    - 实时拖拽移动
    - 标签下拉选择
    - 置信度显示
- **AgentPanel**: VLM 分析评论，置信度仪表盘，检测对象列表，操作建议
- **LiveTerminal**: 可折叠终端（30px/200px），实时日志流，自动滚动

### 4. Multi-Agent 可视化

**展示内容:**
- **InferenceAgent**: 推理 + 不确定性量化 + 主动学习信号
- **AnalysisAgent**: LLM 分析 + 智能决策 + 策略规划
- **AcquisitionAgent**: Web 爬取 + 半监督学习 + 质量评估
- **TrainingAgent**: 模型训练 + 课程学习 + 弱监督微调

**指标:**
- Confidence (置信度)
- Uncertainty Score (不确定性分数)
- Quality Score (质量分数)
- Throughput (吞吐量)
- Success Rate (成功率)
- Last Task / Next Action

### 5. MCP Tool Registry

**集成工具:**
1. **Scene_classifier**: 场景分类 (遥感影像)
2. **Keyword_optimizer**: 关键词优化
3. **Quality_guardian**: 质量评估
4. **Uncertainty_oracle**: 不确定性量化
5. **Pseudo_label_curator**: 伪标注策略

**状态监控:**
- ✅ Online
- ⚠️ Degraded
- ❌ Offline

---

## 🌐 国际化 (i18n)

### 支持语言

- 🇺🇸 English (`en`)
- 🇨🇳 简体中文 (`zh-CN`)

### 添加新语言

```bash
# 1. 创建翻译文件
src/locales/ja.json

# 2. 在 main.ts 中导入
import ja from '@/locales/ja.json'

# 3. 注册语言
messages: { en, 'zh-CN': zhCN, ja }
```

---

## 📸 应用截图

<table>
  <tr>
    <td align="center"><b>仪表盘 - 项目管理</b></td>
    <td align="center"><b>工作区监控 - 训练详情</b></td>
    <td align="center"><b>协同工作区 - 智能标注</b></td>
  </tr>
  <tr>
    <td><img src="../docs/images/home.png" alt="仪表盘" /></td>
    <td><img src="../docs/images/ProjectDetails.png" alt="工作区" /></td>
    <td><img src="../docs/images/SmartCanvas.png" alt="智能画布" /></td>
  </tr>
  <tr>
    <td align="center"><i>项目卡片展示、系统指标统计、GSAP动画效果</i></td>
    <td align="center"><i>进化任务监视器、YOLO训练指标、损失曲线、Agent遥测</i></td>
    <td align="center"><i>数据流管理、智能画布、标注工具、Agent分析、实时终端</i></td>
  </tr>
</table>

---

## 🧪 Mock 数据系统

当前版本使用 **本地 Mock 数据** 模拟后端响应，便于前端独立开发和演示。

### Mock 文件

| 文件 | 内容 | 说明 |
|------|------|------|
| `projects.ts` | 项目列表 | 模拟 5 个项目，含状态/进度 |
| `jobStatus.ts` | 任务状态流 | 2秒间隔更新，模拟实时进度 |
| `agents.ts` | Agent 遥测 | 4 个 Agent 的性能指标 |
| `mcpTools.ts` | MCP 工具 | 5 个工具的状态和延迟 |
| `systemMetrics.ts` | 系统指标 | 全局统计数据 |
| `mock_missions.ts` | 任务数据 | 故事驱动的任务Mock（海上风电平台检测等） |
| `mock_stream.ts` | 图像数据流 | 不同来源和置信度的图像任务 |
| `mock_logs.ts` | Agent日志 | 实时日志流推送 |

### 替换为真实 API

```typescript
// 旧代码 (Mock)
import { fetchProjects } from '@/mock/projects'

// 新代码 (API)
import { projectsApi } from '@/api/projects'
const projects = await projectsApi.list()
```

### 状态管理

使用 Pinia Store 管理应用状态：

- **useAppStore**: 全局应用状态（侧边栏、主题、通知等）
- **useMissionStore**: 任务、数据流、Agent 日志管理

---

## 🔧 技术栈详情

### 核心依赖

```json
{
  "electron": "^28.2.0",
  "vue": "^3.4.15",
  "vue-router": "^4.2.5",
  "pinia": "^2.1.7",
  "vite": "^5.0.12",
  "typescript": "^5.3.3"
}
```

### UI 库

```json
{
  "element-plus": "^2.5.6",
  "gsap": "^3.12.5",
  "@iconify/vue": "^4.1.1",
  "tailwindcss": "^3.4.1"
}
```

### 开发工具

- **unplugin-auto-import**: 自动导入 Vue API
- **unplugin-vue-components**: 组件自动注册
- **unplugin-icons**: Iconify 图标集成
- **sass**: SCSS 预处理器

---

## 🎓 学术背景

本项目是**毕业设计项目**的前端部分，配合后端实现了：

1. **Multi-Agent 工作流可视化** (新)
2. **实时任务监控与日志流** (新)
3. **MCP 工具注册表展示** (新)
4. 主动学习进度可视化
5. 数据获取与质量控制监控

---

## 📊 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 启动时间 | < 2s | Electron 冷启动 |
| HMR | < 100ms | Vite 热更新 |
| 动画帧率 | 60fps | GSAP + GPU 加速 |
| 构建大小 | ~50MB | Electron 打包后 |

---

## 🐛 故障排除

### 问题 1: Electron 白屏

**原因**: Preload 脚本路径错误

**解决**:
```typescript
// electron/main.ts
const preloadPath = path.join(__dirname, 'preload.js')
```

### 问题 2: 主题切换不生效

**原因**: CSS 变量未正确加载

**解决**:
```typescript
// src/main.ts
import '@/assets/styles/base.scss'
```

### 问题 3: 图标不显示

**原因**: Iconify 集合未安装

**解决**:
```bash
npm install @iconify/json
```

---

## 📖 相关文档

- [后端 API 文档](../backend/docs/API.md)
- [系统架构设计](../backend/docs/ARCHITECTURE.md)
- [快速开始指南](./QUICKSTART.md)
- [主项目 README](../README.md)

---

## 👨‍💻 开发者

**Ryder Sun**

- 📧 Email: mhumble010221@gmail.com
- 🔗 GitHub: [@Ryder-MHumble](https://github.com/Ryder-MHumble)

---

## 📝 更新日志

### 2025-12-06
- 🔧 模块化重构：DashboardView (1379行→170行)
- 🔧 模块化重构：WorkspaceView (3077行→387行)
- 🔧 模块化重构：CoPilotWorkspaceView (479行→207行)
- 🧩 新增 dashboard/ 组件目录
- 🧩 新增 workspace/ 组件目录
- 🧩 新增 copilot/ 组件目录
- 📊 优化 Agent 遥测面板布局

### 2025-01-XX
- ✨ 实现协同工作区（CoPilot Workspace）
- 📥 数据流管理组件（DataInbox）
- 🎨 智能画布组件（SmartCanvas）
- 🤖 Agent 分析面板（AgentPanel）
- 💻 实时终端组件（LiveTerminal）
- 📦 Mission Store 状态管理
- 📝 故事驱动的 Mock 数据系统

### 2025-11-08
- ✨ 实现完整的 Electron + Vue 3 架构
- 🎨 集成 GSAP 动画系统
- 🌓 完善双主题支持
- 📊 实现 Multi-Agent 可视化
- 🔧 集成 MCP 工具注册表展示

---

<div align="center">

**Made with ❤️ and attention to detail**

⭐ 如果这个项目对你有帮助，请给个 Star！

</div>

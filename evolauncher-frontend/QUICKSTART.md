# 🚀 快速启动指南

## 安装依赖

首先，确保你已经安装了 Node.js 18+ 版本。

```bash
cd evolauncher-frontend
npm install
```

## 开发模式运行

### 选项 1: 仅 Web 模式（推荐用于快速开发）

```bash
npm run dev
```

然后在浏览器中打开 `http://localhost:5173`

### 选项 2: Electron 桌面应用模式

```bash
npm run electron:dev
```

这将同时启动 Vite 开发服务器和 Electron 应用。

## 项目特色功能

### ✨ 主题切换

- 点击右上角的太阳/月亮图标切换主题
- 支持亮色、暗色和自动跟随系统
- 所有颜色平滑过渡

### 🌐 多语言支持

- 点击右上角的翻译图标切换语言
- 支持中文和英文
- 所有界面文本都已国际化

### 🎨 高级动画

- 项目卡片使用 GSAP 的 stagger 效果逐个出现
- 侧边栏导航有平滑的展开/收起动画
- 工作区的进化任务监视器有动态步骤转换
- 所有悬停效果都经过精心调优

### 📊 工作区监控

访问 "Workspace" 页面查看：
- 实时任务进度监控
- 动态步骤指示器
- 实时日志输出
- 性能指标可视化

## 文件结构说明

```
src/
├── components/       # 组件
│   ├── layout/      # 布局组件（Header, Sidebar）
│   └── common/      # 通用组件（Card, Badge, Skeleton）
├── views/           # 页面
│   ├── DashboardView.vue  # 仪表盘
│   └── WorkspaceView.vue  # 工作区
├── assets/styles/   # 样式系统
├── composables/     # 组合式函数
├── mock/            # 模拟数据
└── locales/         # 国际化文件
```

## 技术亮点

1. **TypeScript**: 完整的类型安全
2. **组合式 API**: 使用 `<script setup>` 语法
3. **自动导入**: Vue API 和组件无需手动 import
4. **SCSS 变量**: 全局设计系统
5. **CSS 自定义属性**: 主题系统
6. **GSAP 动画**: 专业级动画效果

## 下一步

当你准备好连接真实后端时：

1. 替换 `src/mock/` 中的模拟数据
2. 创建 API 服务层
3. 更新环境变量配置

## 需要帮助？

查看 `README.md` 获取完整文档。

---

**开始你的开发之旅吧！** 🎉


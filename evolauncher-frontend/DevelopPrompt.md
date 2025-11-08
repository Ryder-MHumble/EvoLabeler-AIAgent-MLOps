你好，我需要你扮演一名顶尖的 **UI/UX 设计师** 和 **高级前端工程师**。我们将共同创建一个名为 "EvoLabeler" 的桌面应用程序的前端部分。

**核心设计哲学 (Design Philosophy):**

我们的首要目标是**创造卓越的用户体验**。功能暂时用静态数据模拟，但应用的**视觉呈现、交互反馈和动画效果**必须达到业界领先水平。整个应用应散发出**专业、现代、科技感**的气质，让用户感觉自己在使用一款强大而优雅的工具。

**技术栈与关键库:**

*   **打包器:** Electron
*   **框架:** Vue 3 (使用 `<script setup lang="ts">` 语法)
*   **构建工具:** Vite
*   **语言:** TypeScript
*   **UI 库:** **Element Plus** (用于基础组件，但我们会进行深度定制)
*   **动画库:** **GSAP (GreenSock Animation Platform)** 用于复杂、高性能的动画；**VueUse 的 `motion`** 用于简单的过渡效果。
*   **图标库:** **Iconify** (通过 `unplugin-icons`)，提供海量高质量图标。
*   **状态管理:** Pinia
*   **国际化 (i18n):** `vue-i18n`
*   **样式:** **Tailwind CSS** (用于快速布局和原子化 CSS) + SCSS (用于全局样式和主题定义)。

---

### **第一部分：项目初始化与配置**

请为我生成一个集成了上述所有技术的 **Electron + Vue 3 + Vite + TypeScript** 模板项目。

**项目结构:**

```
/evolauncher-frontend
|
|-- electron/              # Electron 主进程代码
|   |-- main.ts
|   |-- preload.ts
|
|-- src/
|   |-- assets/
|   |   |-- styles/          # SCSS 文件
|   |   |   |-- _variables.scss
|   |   |   |-- base.scss
|   |   |   |-- themes.scss    # 明暗主题定义
|   |   |-- fonts/           # (可选) 自定义字体
|   |
|   |-- components/
|   |   |-- layout/
|   |   |   |-- AppHeader.vue
|   |   |   |-- AppSidebar.vue
|   |   |-- common/
|   |   |   |-- AnimatedCard.vue # 带动效的卡片组件
|   |   |   |-- ThemeToggle.vue  # 主题切换按钮
|   |
|   |-- views/
|   |   |-- DashboardView.vue
|   |   |-- WorkspaceView.vue
|   |
|   |-- router/
|   |-- store/
|   |   |-- app.ts             # 管理全局状态，如主题、语言
|   |
|   |-- locales/             # i18n 国际化文件
|   |   |-- en.json
|   |   |-- zh-CN.json
|   |
|   |-- mock/                # 静态数据模拟
|   |   |-- projects.ts
|   |   |-- jobStatus.ts
|   |
|   |-- composables/         # 可复用的组合式函数
|   |   |-- useTheme.ts
|   |
|   |-- App.vue
|   |-- main.ts
|
|-- package.json
|-- vite.config.ts
|-- tailwind.config.js
|-- tsconfig.json
```

**配置要求:**

1.  **`vite.config.ts`:** 配置好 Vue、AutoImport (自动导入 Vue API)、Components (组件自动导入)、Unplugin Icons 和 Tailwind CSS。
2.  **`electron/main.ts`:** 创建一个无边框、可拖拽的窗口 (`frame: false, transparent: true`)，为自定义标题栏做准备。
3.  **`tailwind.config.js`:** 配置好主题色，并集成 `@tailwindcss/typography` 插件。
4.  **`main.ts`:** 初始化 Vue app，并正确挂载 Pinia, Vue Router, vue-i18n。

---

### **第二部分：UI/UX 设计与实现**

这是本次任务的核心，请注入你的设计创意。

**2.1 全局布局与主题:**

*   **布局:** 实现一个包含自定义顶部标题栏 (`AppHeader`) 和左侧可伸缩侧边栏 (`AppSidebar`) 的主布局。
*   **主题配色 (Theming):**
    *   **亮色主题 (Light Mode):** 不要用纯白 (`#FFFFFF`)。使用带有微弱冷色调的浅灰色 (如 `#F7F8FC`) 作为背景。主色调使用饱和度稍高的蓝色 (如 `#4A69FF`)。
    *   **暗色主题 (Dark Mode):** 不要用纯黑 (`#000000`)。使用带有深蓝或深紫色调的炭黑色 (如 `#1A1B26`) 作为背景。UI 元素使用柔和的辉光效果（`box-shadow` 或 `filter: drop-shadow`）来创造层次感。
    *   **实现:** 在 `themes.scss` 中使用 CSS 自定义属性 (CSS Variables) 定义两套主题色板。在 `useTheme.ts` composable 中实现切换逻辑，通过给根元素 `<html>` 添加 `class="dark"` 来应用暗色主题。

**2.2 动画与微交互 (Animations & Micro-interactions):**

*   **页面切换:** 使用 Vue Router 的 `<transition>`，配合 GSAP 实现一个流畅的、非线性的页面淡入淡出+轻微位移效果。
*   **组件加载:** 列表、卡片等内容出现时，使用 GSAP 的 `stagger` 特性，让元素逐个、带有轻微延迟地动画入场，营造一种动态和生命感。
*   **悬停效果 (Hover):** 按钮、卡片等可交互元素在鼠标悬停时，应有平滑的放大、上浮或辉光效果（使用 CSS `transition` 或 GSAP）。
*   **点击反馈:** 按钮点击时，应有一个快速的缩小再恢复的“果冻”效果，提供明确的物理反馈。

**2.3 具体组件实现:**

*   **`AppHeader.vue` (自定义标题栏):**
    *   包含应用 Logo、窗口控制按钮（最小化、最大化、关闭，需调用 Electron API）、`ThemeToggle` 组件和语言切换下拉菜单。
    *   窗口可拖拽区域应正确设置。
*   **`AppSidebar.vue` (侧边栏):**
    *   包含指向“仪表盘”和“工作区”的导航链接。
    *   实现一个平滑的展开/收起动画。
*   **`DashboardView.vue` (仪表盘):**
    *   使用 CSS Grid 布局展示项目卡片列表。
    *   卡片 (`AnimatedCard.vue`) 从 `mock/projects.ts` 加载数据。
    *   当页面加载时，卡片列表使用 GSAP 的 `staggerFrom` 效果逐个动画出现。
*   **`WorkspaceView.vue` (工作区):**
    *   实现我们在上一轮讨论的三栏式布局。
    *   **“进化任务监视器”:** 这个步骤条 (`ElSteps`) 必须是动态的。当步骤切换时，高亮点的移动要有平滑的动画效果，而不是瞬间跳变。使用 GSAP 来控制动画。
    *   **数据加载:** 所有从 mock 文件加载数据的地方，都模拟一个 1-2 秒的延迟，并显示一个优雅的骨架屏 (Skeleton Screen) 或加载动画，以优化感知性能。

---

### **第三部分：静态数据与国际化**

*   **`mock/`:**
    *   **`projects.ts`:** 创建一个包含 3-5 个项目对象的数组，每个对象有 `id`, `name`, `imageCount`, `createdAt`, `thumbnailUrl` 等字段。
    *   **`jobStatus.ts`:** 创建一个函数 `createJobStatusStream()`，它使用 `setInterval` 每隔 2 秒返回一个新的 Job 状态对象，模拟后端轮询的过程。
*   **`locales/`:**
    *   **`en.json` 和 `zh-CN.json`:** 为所有界面上的文本（按钮、标题、标签等）提供中英文翻译。
    *   在 Vue 组件中使用 `$t('key')` 的方式来引用文本。

---

### **最终要求:**

*   **以用户为中心:** 你的代码应该优先考虑用户的感受。动画不能卡顿，交互必须直观，视觉必须和谐。
*   **代码即设计:** 在代码注释中，请不仅解释代码的功能，还要解释其背后的**设计意图**。例如：`// 使用 GSAP 的 Power4.easeOut 缓动函数，创造一种快速启动后平滑减速的动画，感觉更自然。`
*   **可维护性:** 即使是静态数据，也要通过模拟服务的形式提供给组件，而不是硬编码在 Vue 文件中。这样，未来从 mock 切换到真实 API 调用时，只需修改服务层的文件即可。

请基于以上详尽的设计蓝图，为我生成这个注重极致用户体验的前端项目。
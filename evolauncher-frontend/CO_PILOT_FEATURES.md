# Co-Pilot 工作区功能说明

## 概述

根据 `Develop.md` 的设计要求，已实现 "任务指挥官" 故事驱动的增量功能优化。新增了以下核心组件和功能：

## 新增文件结构

```
src/
├── api/
│   ├── types.ts                    # 核心类型定义
│   └── mocks/
│       ├── mock_missions.ts        # 任务 Mock 数据
│       ├── mock_stream.ts          # 图像数据流 Mock
│       └── mock_logs.ts            # Agent 日志 Mock
├── store/
│   └── mission.ts                  # Mission Store (Pinia)
├── components/
│   └── workspace/
│       ├── DataInbox.vue           # 左侧数据流面板
│       ├── SmartCanvas.vue         # 中间智能画布
│       ├── AgentPanel.vue          # 右侧 Agent 分析面板
│       └── LiveTerminal.vue        # 底部实时终端
└── views/
    └── CoPilotWorkspaceView.vue    # 新的工作区视图
```

## 核心功能

### 1. 类型定义 (`src/api/types.ts`)

定义了完整的数据类型系统：
- `Mission`: 任务对象
- `ImageTask`: 图像任务
- `BoundingBox`: 边界框标注
- `AgentLog`: Agent 日志
- `AgentAnalysis`: Agent 分析结果

### 2. 故事驱动的 Mock 数据

#### `mock_missions.ts`
- 包含 "海上风电平台检测" 等示例任务
- 支持任务状态管理（idle, scouting, training, labeling, completed）

#### `mock_stream.ts`
- 模拟 Agent 抓取的图像数据流
- 包含不同来源（crawler, agent_recommended, manual）
- 不同置信度的图像和边界框

#### `mock_logs.ts`
- 模拟 Agent 的思考过程日志
- 支持实时日志流推送
- 包含不同级别的日志（info, warning, error, success）

### 3. Mission Store (`src/store/mission.ts`)

使用 Pinia 管理状态：
- 任务列表和当前任务
- 图像数据流
- Agent 日志
- 数据流统计

### 4. 组件功能

#### DataInbox.vue (左侧数据流)
- 三个分类标签：Incoming、Pending、Library
- 图像缩略图展示
- 置信度颜色编码（绿色/黄色/橙色）
- 来源标签（爬虫/Agent推荐/手动）
- 点击选择图像

#### SmartCanvas.vue (中间画布)
- 图像显示和缩放
- 边界框覆盖层（SVG）
- 置信度颜色编码
- 点击边界框切换确认状态
- 空格键快速确认
- 图像信息栏

#### AgentPanel.vue (右侧面板)
- Agent 分析评论展示
- 置信度仪表盘
- 检测对象列表
- 操作建议

#### LiveTerminal.vue (底部终端)
- 可折叠终端（30px/200px）
- 实时日志流
- 日志级别颜色编码
- 自动滚动到最新日志
- 终端风格 UI

## 使用方法

### 访问新工作区

1. **通过路由访问**：
   ```typescript
   router.push({ name: 'CoPilotWorkspace', params: { id: 'mission-001' } })
   ```

2. **从 Dashboard 导航**：
   可以在 DashboardView 中添加导航按钮，链接到新工作区

### 集成到现有视图

如果需要将新组件集成到现有的 `WorkspaceView.vue`，可以：

```vue
<template>
  <div class="workspace-container">
    <!-- 可以选择使用新组件或保留原有组件 -->
    <DataInbox v-if="useNewComponents" />
    <SmartCanvas v-if="useNewComponents" />
    <AgentPanel v-if="useNewComponents" />
    <LiveTerminal v-if="useNewComponents" />
    
    <!-- 或保留原有内容 -->
    <!-- ... -->
  </div>
</template>
```

## 设计特点

### 视觉风格
- **现代深色专业风格**：深蓝/灰色背景 (`#0f172a`)
- **Glassmorphism 效果**：毛玻璃背景和模糊
- **颜色编码**：
  - Agent 操作：Neon Cyan (`#06b6d4`)
  - 用户操作：Electric Purple (`#8b5cf6`)
  - 成功/稳定：Emerald Green (`#10b981`)

### 交互体验
- 平滑的动画过渡
- 响应式布局（支持小屏幕）
- 键盘快捷键支持（空格键确认）
- 实时数据更新

## 下一步优化建议

1. **连接后端 API**：
   - 将 Mock 数据替换为真实 API 调用
   - 在 `src/api/mocks/` 中的函数可以改为调用真实 API

2. **增强功能**：
   - 边界框拖拽编辑
   - 图像缩放和平移
   - 批量操作
   - 导出功能

3. **性能优化**：
   - 虚拟滚动（大量图像时）
   - 图像懒加载
   - 日志分页

4. **用户体验**：
   - 添加加载骨架屏
   - 错误处理和重试机制
   - 操作确认对话框

## 技术栈

- **Vue 3** + **TypeScript**
- **Pinia** 状态管理
- **Tailwind CSS** + **SCSS** 样式
- **Iconify** 图标
- **Element Plus** UI 组件（部分使用）

## 注意事项

1. 所有组件都使用了 `@include custom-scrollbar` mixin，确保在 `_variables.scss` 中已定义
2. 组件使用了响应式设计，在不同屏幕尺寸下会自动调整布局
3. LiveTerminal 使用固定定位，需要为父容器预留底部空间（30px 折叠，200px 展开）



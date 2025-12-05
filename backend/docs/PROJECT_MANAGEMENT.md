# 项目管理功能文档

## 概述

EvoLabeler 项目管理系统提供完整的项目生命周期管理能力，包括项目创建、状态跟踪、数据统计和可视化展示。

## 数据库设计

### Projects 表结构

```sql
CREATE TABLE public.projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL CHECK (status IN ('idle', 'training', 'labeling', 'completed')),
    image_count INTEGER DEFAULT 0,
    accuracy NUMERIC(5, 2),
    thumbnail_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 关键字段说明

- **project_id**: 人类可读的项目标识符 (例如: `proj_wildlife_001`)
- **status**: 项目状态 (`idle` | `training` | `labeling` | `completed`)
- **image_count**: 项目中的图像数量
- **accuracy**: 模型准确率 (0-100)
- **thumbnail_url**: 项目封面图片URL
- **metadata**: 灵活的 JSONB 字段存储额外信息

## API 接口

### 1. 创建项目

```http
POST /api/v1/projects/
```

创建一个新的项目记录。

**请求示例:**
```json
{
  "project_id": "proj_example_001",
  "name": "示例项目",
  "description": "这是一个示例项目",
  "thumbnail_url": "https://example.com/image.jpg",
  "metadata": {
    "model_type": "yolov5s",
    "classes": ["class1", "class2"]
  }
}
```

### 2. 列表查询

```http
GET /api/v1/projects/?page=1&page_size=20&status_filter=training
```

支持分页、过滤和排序的项目列表查询。

### 3. 获取详情

```http
GET /api/v1/projects/{project_id}
```

获取特定项目的详细信息。

### 4. 更新项目

```http
PUT /api/v1/projects/{project_id}
```

更新项目的任意字段（name、description、status、image_count、accuracy 等）。

### 5. 删除项目

```http
DELETE /api/v1/projects/{project_id}
```

删除项目及其关联数据。

### 6. 统计信息

```http
GET /api/v1/projects/stats/summary
```

获取所有项目的聚合统计信息。

## 前端集成

### TypeScript API 客户端

前端提供了完整的 TypeScript API 客户端：

```typescript
import { projectsApi } from '@/api/projects'

// 列表查询
const projects = await projectsApi.list({ page: 1, pageSize: 20 })

// 获取详情
const project = await projectsApi.get('proj_001')

// 创建项目
const newProject = await projectsApi.create({
  projectId: 'proj_new',
  name: 'New Project'
})
```

### 配置说明

前端当前使用 Mock 数据，要切换到后端 API：

1. 在 `.env` 文件中设置：
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   VITE_USE_BACKEND_API=true
   ```

2. 前端代码会自动使用后端 API 而不是 Mock 数据

## 测试数据

### 插入测试数据

运行脚本插入预定义的测试项目：

```bash
cd backend
poetry run python scripts/insert_test_projects.py
```

该脚本会：
1. 检查 projects 表是否存在
2. 清理已存在的测试数据
3. 插入 8 个示例项目
4. 验证数据插入结果

### 测试项目列表

- 野生动物分类识别 (completed, 1250 images, 94.5% accuracy)
- 医学影像数据集 (training, 3420 images, 87.2% accuracy)
- 城市交通分析 (labeling, 8750 images)
- 商品目录管理 (idle, 542 images)
- 卫星遥感影像 (completed, 15600 images, 91.8% accuracy)
- 工业质检系统 (training, 2890 images, 89.3% accuracy)
- 农作物病虫害检测 (labeling, 4520 images)
- 智能安防监控 (completed, 6780 images, 92.7% accuracy)

## 项目与任务关联

### Project-Jobs 关系表

```sql
CREATE TABLE public.project_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id TEXT NOT NULL REFERENCES public.projects(project_id),
    job_id TEXT NOT NULL REFERENCES public.jobs(job_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

该表用于关联项目和任务，支持：
- 一个项目可以有多个任务
- 追踪任务执行历史
- 级联删除（删除项目时自动删除关联）

## 性能优化

### 索引策略

- `project_id`: 唯一索引，快速查询
- `status`: B-tree 索引，支持状态过滤
- `created_at`, `updated_at`: 降序索引，支持时间排序

### 查询建议

1. **列表查询**: 使用分页避免全表扫描
2. **状态过滤**: 利用索引提高查询效率
3. **统计查询**: 定期缓存结果避免重复计算

## 数据迁移

### 运行迁移

在 Supabase SQL Editor 中执行：

```bash
backend/app/db/migrations/002_create_projects_table.sql
```

该脚本会：
1. 创建 projects 表
2. 创建索引
3. 创建自动更新时间戳的触发器
4. 创建 project_jobs 关联表

### 回滚

如需回滚，执行：

```sql
DROP TABLE IF EXISTS public.project_jobs CASCADE;
DROP TABLE IF EXISTS public.projects CASCADE;
DROP FUNCTION IF EXISTS update_projects_updated_at();
```

## 最佳实践

### 1. 项目命名

- 使用有意义的 `project_id`
- 格式建议: `proj_{domain}_{sequence}`
- 例如: `proj_wildlife_001`, `proj_medical_002`

### 2. 状态管理

- 创建时默认为 `idle`
- 开始训练时更新为 `training`
- 标注阶段更新为 `labeling`
- 完成后标记为 `completed`

### 3. 元数据使用

利用 `metadata` 字段存储额外信息：

```json
{
  "model_type": "yolov5m",
  "classes": ["class1", "class2"],
  "training_epochs": 150,
  "dataset_source": "custom"
}
```

## 故障排查

### 常见问题

**Q: 无法创建项目，提示 project_id 已存在**
- A: 使用唯一的 project_id 或先删除已存在的项目

**Q: 测试数据插入失败**
- A: 确认已运行数据库迁移脚本，检查 Supabase 连接配置

**Q: 前端显示空列表**
- A: 确认后端已启动，API 地址配置正确，检查 CORS 设置

## 相关文档

- [API 文档](API.md) - 完整的 API 接口文档
- [数据库设计](../app/db/DATABASE_DESIGN.md) - 数据库架构详解
- [前端 API 客户端](../../evolauncher-frontend/src/api/projects.ts) - TypeScript 接口定义



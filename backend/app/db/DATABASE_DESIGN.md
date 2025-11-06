# 数据仓库设计文档

## 概述

EvoLabeler-Backend 使用 **Supabase (PostgreSQL)** 作为数据存储解决方案，采用轻量级关系型数据库设计。本文档详细说明数据库的表结构、关系、索引策略以及设计理念。

## 设计原则

### 1. 职责分离
- **jobs 表**: 任务状态管理和元数据
- **inference_results 表**: 推理结果存储
- **Storage Buckets**: 文件对象存储

### 2. 可扩展性
- 使用 JSONB 字段存储灵活的元数据
- 预留字段用于未来功能扩展
- 支持水平扩展的表结构设计

### 3. 性能优化
- 关键字段添加索引
- 时间序列数据按时间索引
- 合理的数据类型选择

---

## 核心表结构

### 1. jobs 表 - 任务管理核心表

**用途**: 存储所有 MLOps 任务的状态、进度和元数据

```sql
CREATE TABLE public.jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL CHECK (status IN (
        'UPLOAD', 'INFERENCE', 'ANALYSIS', 'ACQUISITION', 
        'PSEUDO_LABELING', 'TRAINING', 'COMPLETE', 'FAILED'
    )),
    progress_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 字段说明

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `id` | UUID | 内部主键，数据库自动生成 | `550e8400-e29b-41d4-a716-446655440000` |
| `job_id` | TEXT | 外部任务ID，用于API查询（唯一） | `job_2024_001` |
| `status` | TEXT | 任务当前状态（枚举约束） | `INFERENCE` |
| `progress_message` | TEXT | 当前进度描述信息 | `正在分析图像...` |
| `metadata` | JSONB | 灵活的元数据存储 | 见下方详解 |
| `created_at` | TIMESTAMP | 任务创建时间（UTC） | `2024-01-15 10:30:00+00` |
| `updated_at` | TIMESTAMP | 最后更新时间（自动触发器） | `2024-01-15 10:35:00+00` |

#### metadata 字段结构

`metadata` 使用 JSONB 类型，支持灵活的数据存储和高效查询：

```json
{
  // 文件信息
  "filename": "satellite_images.zip",
  "file_size_mb": 25.5,
  "upload_dir": "/tmp/uploads/job_2024_001",
  
  // 处理统计
  "images_uploaded": 10,
  "images_processed": 10,
  "images_acquired": 35,
  "pseudo_labels_generated": 32,
  
  // 分析结果
  "scene_type": "城市遥感影像",
  "search_queries": ["urban satellite", "city remote sensing"],
  "key_features": ["建筑物", "道路", "绿地"],
  
  // 训练配置
  "model_config": {
    "epochs": 100,
    "batch_size": 16,
    "model_type": "yolov5s"
  },
  
  // 性能指标
  "uncertainty_score": 0.45,
  "mean_confidence": 0.72,
  
  // 时间统计
  "stage_durations": {
    "inference": 45.2,
    "analysis": 12.8,
    "acquisition": 120.5,
    "training": 3600.0
  }
}
```

#### 状态流转图

```
UPLOAD → INFERENCE → ANALYSIS → ACQUISITION → PSEUDO_LABELING → TRAINING → COMPLETE
   ↓         ↓           ↓            ↓              ↓              ↓         ↓
   └─────────┴───────────┴────────────┴──────────────┴──────────────┴─────→ FAILED
```

#### 索引策略

```sql
-- 主要查询索引
CREATE INDEX idx_jobs_job_id ON public.jobs(job_id);

-- 状态过滤索引
CREATE INDEX idx_jobs_status ON public.jobs(status);

-- 时间序列索引（降序，最新优先）
CREATE INDEX idx_jobs_created_at ON public.jobs(created_at DESC);

-- JSONB 字段索引（可选，用于复杂查询）
CREATE INDEX idx_jobs_metadata_scene ON public.jobs 
  USING gin ((metadata->'scene_type'));
```

---

### 2. inference_results 表 - 推理结果详细记录

**用途**: 存储每张图片的推理结果，支持主动学习和不确定性分析

```sql
CREATE TABLE public.inference_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id TEXT NOT NULL,
    image_path TEXT NOT NULL,
    predictions JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 字段说明

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `id` | UUID | 记录主键 | - |
| `job_id` | TEXT | 关联的任务ID（外键关系） | `job_2024_001` |
| `image_path` | TEXT | 图片路径或URL | `/uploads/image_001.jpg` |
| `predictions` | JSONB | 检测结果数组 | 见下方详解 |
| `created_at` | TIMESTAMP | 推理时间 | - |

#### predictions 字段结构

存储 YOLO 格式的检测结果：

```json
{
  "detections": [
    {
      "class_id": 0,
      "class_name": "building",
      "confidence": 0.89,
      "bbox": {
        "x": 0.35,      // 归一化中心点 x
        "y": 0.42,      // 归一化中心点 y
        "width": 0.15,  // 归一化宽度
        "height": 0.20  // 归一化高度
      }
    },
    {
      "class_id": 1,
      "class_name": "road",
      "confidence": 0.76,
      "bbox": {
        "x": 0.60,
        "y": 0.55,
        "width": 0.25,
        "height": 0.10
      }
    }
  ],
  
  // 不确定性度量（主动学习）
  "uncertainty_metrics": {
    "entropy": 0.42,
    "variance": 0.15,
    "low_confidence_count": 1
  },
  
  // 图片元信息
  "image_info": {
    "width": 1920,
    "height": 1080,
    "format": "jpeg"
  },
  
  // 推理元数据
  "inference_metadata": {
    "model_version": "yolov5s",
    "inference_time_ms": 45.2,
    "device": "cuda:0"
  }
}
```

#### 索引策略

```sql
-- 按任务查询索引
CREATE INDEX idx_inference_results_job_id 
  ON public.inference_results(job_id);

-- 按时间查询索引
CREATE INDEX idx_inference_results_created_at 
  ON public.inference_results(created_at DESC);

-- JSONB 路径索引（用于不确定性查询）
CREATE INDEX idx_inference_results_uncertainty 
  ON public.inference_results 
  USING gin ((predictions->'uncertainty_metrics'));
```

---

## 表关系图

```
┌─────────────────────────────────────────────────────────┐
│                      jobs (主表)                         │
│  - id (PK)                                              │
│  - job_id (UNIQUE)  ←─────────────────┐                │
│  - status                              │                │
│  - progress_message                    │                │
│  - metadata (JSONB)                    │                │
│  - created_at                          │                │
│  - updated_at                          │                │
└────────────────────────────────────────┘                │
                                         │                │
                                         │ 1:N            │
                                         │                │
┌────────────────────────────────────────┘                │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         inference_results (详情表)                │  │
│  │  - id (PK)                                        │  │
│  │  - job_id (FK) ───────────────────────────────────┘  │
│  │  - image_path                                        │
│  │  - predictions (JSONB)                               │
│  │  - created_at                                        │
│  └──────────────────────────────────────────────────────┘
```

---

## Storage Buckets 设计

### 1. images Bucket - 图片存储

**配置**:
- **可见性**: Public（公开访问）
- **大小限制**: 10 MB/文件
- **允许类型**: `image/jpeg`, `image/png`, `image/gif`, `image/webp`

**目录结构**:
```
images/
├── uploads/
│   └── {job_id}/
│       ├── image_001.jpg
│       ├── image_002.jpg
│       └── ...
├── crawled/
│   └── {job_id}/
│       ├── {query}_001.jpg
│       ├── {query}_002.jpg
│       └── ...
└── processed/
    └── {job_id}/
        ├── labeled_001.jpg
        └── ...
```

### 2. models Bucket - 模型存储

**配置**:
- **可见性**: Private（私有访问）
- **大小限制**: 500 MB/文件
- **允许类型**: 所有文件类型

**目录结构**:
```
models/
├── checkpoints/
│   └── {job_id}/
│       ├── best.pt
│       ├── last.pt
│       └── config.yaml
├── pretrained/
│   ├── yolov5s.pt
│   └── yolov5m.pt
└── logs/
    └── {job_id}/
        └── training.log
```

---

## 数据访问模式

### 1. 高频查询场景

#### 场景 A: 获取任务状态
```sql
SELECT job_id, status, progress_message, updated_at
FROM public.jobs
WHERE job_id = 'job_2024_001';
```
**性能**: O(1) - 使用唯一索引

#### 场景 B: 获取任务推理结果
```sql
SELECT ir.image_path, ir.predictions
FROM public.inference_results ir
WHERE ir.job_id = 'job_2024_001'
ORDER BY ir.created_at DESC;
```
**性能**: O(log N) - 使用索引扫描

#### 场景 C: 查询低置信度样本（主动学习）
```sql
SELECT ir.image_path, 
       ir.predictions->'uncertainty_metrics'->>'entropy' as entropy
FROM public.inference_results ir
WHERE ir.job_id = 'job_2024_001'
  AND (ir.predictions->'uncertainty_metrics'->>'entropy')::float > 0.5
ORDER BY entropy DESC
LIMIT 10;
```
**性能**: O(N) - 全表扫描，可通过 GIN 索引优化

### 2. 低频管理操作

#### 清理过期任务
```sql
DELETE FROM public.jobs
WHERE status = 'COMPLETE'
  AND created_at < NOW() - INTERVAL '30 days';
```

#### 统计分析
```sql
SELECT 
  status,
  COUNT(*) as count,
  AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_duration_seconds
FROM public.jobs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY status;
```

---

## 触发器和约束

### 自动更新时间戳

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_jobs_updated_at
    BEFORE UPDATE ON public.jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 数据完整性约束

```sql
-- 状态枚举约束（已在表定义中）
CHECK (status IN ('UPLOAD', 'INFERENCE', ...))

-- 外键约束（可选，根据需求决定是否启用）
ALTER TABLE inference_results 
ADD CONSTRAINT fk_inference_results_job
FOREIGN KEY (job_id) REFERENCES jobs(job_id)
ON DELETE CASCADE;
```

---

## 数据生命周期管理

### 1. 数据保留策略

| 数据类型 | 保留期限 | 策略 |
|---------|---------|------|
| 活跃任务 | 永久 | 保留所有状态为 UPLOAD-TRAINING 的任务 |
| 完成任务 | 30 天 | 自动归档或删除 |
| 失败任务 | 7 天 | 保留用于调试 |
| 推理结果 | 30 天 | 与任务同步删除 |
| 上传图片 | 30 天 | 任务完成后清理 |
| 模型文件 | 90 天 | 保留最近版本 |

### 2. 归档策略

```sql
-- 创建归档表
CREATE TABLE public.jobs_archive (LIKE public.jobs);

-- 归档完成任务
INSERT INTO public.jobs_archive
SELECT * FROM public.jobs
WHERE status = 'COMPLETE' 
  AND created_at < NOW() - INTERVAL '30 days';

-- 删除已归档数据
DELETE FROM public.jobs
WHERE id IN (SELECT id FROM public.jobs_archive);
```

---

## 扩展性考虑

### 1. 水平分片策略

当数据量增长时，可按以下维度分片：

- **时间分片**: 按月创建分区表
- **任务类型分片**: 按 scene_type 分区
- **地理分片**: 按区域分布式存储

### 2. 缓存层设计

```
Application
    ↓
Redis Cache (任务状态)
    ↓
Supabase (持久化存储)
```

### 3. 未来扩展表

预留以下表结构用于功能扩展：

```sql
-- 用户管理表
CREATE TABLE public.users (
    id UUID PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT,
    created_at TIMESTAMP
);

-- 模型版本管理表
CREATE TABLE public.model_versions (
    id UUID PRIMARY KEY,
    version TEXT,
    model_path TEXT,
    metrics JSONB,
    created_at TIMESTAMP
);

-- 数据集管理表
CREATE TABLE public.datasets (
    id UUID PRIMARY KEY,
    name TEXT,
    source TEXT,
    metadata JSONB,
    created_at TIMESTAMP
);
```

---

## 性能优化建议

### 1. 查询优化

- ✅ 使用 `job_id` 查询而非 `id`
- ✅ 避免 `SELECT *`，明确指定字段
- ✅ 合理使用 JSONB 索引
- ✅ 批量插入使用事务

### 2. 连接池配置

```python
# Supabase 客户端配置
client = create_client(
    supabase_url=settings.supabase_url,
    supabase_key=settings.supabase_key,
    options=ClientOptions(
        postgrest_client_timeout=10,
        storage_client_timeout=15
    )
)
```

### 3. 监控指标

- 查询响应时间
- 表大小增长率
- 索引使用率
- 缓存命中率

---

## 安全性考虑

### 1. 行级安全 (RLS)

```sql
-- 启用 RLS
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

-- 策略示例：用户只能访问自己的任务
CREATE POLICY "Users can view own jobs"
ON public.jobs FOR SELECT
USING (auth.uid() = (metadata->>'user_id')::uuid);
```

### 2. 访问控制

- **anon**: 只读访问任务状态
- **authenticated**: 创建和查询任务
- **service_role**: 完全访问权限（仅后端使用）

---

## 备份和恢复

### 1. 自动备份

Supabase 提供：
- 每日自动备份
- Point-in-time Recovery (PITR)
- 跨区域复制

### 2. 手动导出

```bash
# 导出数据
pg_dump -h db.xxx.supabase.co -U postgres -d postgres > backup.sql

# 恢复数据
psql -h db.xxx.supabase.co -U postgres -d postgres < backup.sql
```

---

## 总结

本数据库设计遵循以下原则：

✅ **简洁性**: 最小化表数量，使用 JSONB 提供灵活性  
✅ **可扩展性**: 预留字段和扩展表结构  
✅ **性能**: 合理的索引策略和查询优化  
✅ **安全性**: RLS 和访问控制  
✅ **可维护性**: 清晰的文档和命名规范  

这个设计能够支持 EvoLabeler 系统从原型到生产的完整生命周期。


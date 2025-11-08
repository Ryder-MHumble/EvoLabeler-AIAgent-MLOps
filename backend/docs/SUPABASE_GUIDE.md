# Supabase 使用指南

## 问题：找不到创建的表？

### ✅ 解决方案

您的表创建在 **`public` schema** 中，而不是 `storage` schema！

### 📋 查看表的正确步骤

#### 方法1：Table Editor（推荐）

1. **打开 Supabase Dashboard**
   ```
   https://app.supabase.com/project/jzkejgtalihqvomdwjrs
   ```

2. **点击左侧菜单 "Table Editor"**

3. **⚠️ 重要：切换 Schema**
   - 在顶部有一个下拉菜单显示当前 schema
   - 默认可能显示 `storage`
   - **点击下拉菜单，选择 `public`**
   
4. **现在您应该能看到您的表了**：
   - `jobs` - 任务管理表
   - `inference_results` - 推理结果表

#### 方法2：SQL Editor（验证）

1. **点击左侧菜单 "SQL Editor"**

2. **运行以下查询验证表是否存在**：
   ```sql
   -- 查看所有表
   SELECT table_schema, table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_type = 'BASE TABLE';
   ```

3. **查看表结构**：
   ```sql
   -- 查看 jobs 表结构
   SELECT column_name, data_type, is_nullable
   FROM information_schema.columns
   WHERE table_schema = 'public' 
   AND table_name = 'jobs';
   
   -- 查看 inference_results 表结构
   SELECT column_name, data_type, is_nullable
   FROM information_schema.columns
   WHERE table_schema = 'public' 
   AND table_name = 'inference_results';
   ```

4. **查看数据**：
   ```sql
   -- 查看 jobs 表（应该是空的）
   SELECT * FROM public.jobs;
   
   -- 查看 inference_results 表
   SELECT * FROM public.inference_results;
   ```

---

## 🗂️ Schema 说明

### `public` Schema
- **用途**: 应用数据表
- **包含的表**:
  - `jobs` - 任务管理
  - `inference_results` - 推理结果
- **权限**: 可读写

### `storage` Schema
- **用途**: Supabase Storage 系统表
- **包含的表**:
  - `buckets` - Bucket 配置
  - `objects` - 文件对象
  - 其他存储相关系统表
- **权限**: 通过 API 操作

---

## 📦 Storage Buckets 验证

### 查看已创建的 Buckets

1. **点击左侧菜单 "Storage"**

2. **您应该看到两个 Buckets**：
   - `images` (public)
   - `models` (private)

3. **验证 Bucket 配置**：

   在 SQL Editor 中运行：
   ```sql
   SELECT 
     id,
     name,
     public,
     file_size_limit,
     allowed_mime_types
   FROM storage.buckets;
   ```

   **期望结果**：
   ```
   id      | name   | public | file_size_limit | allowed_mime_types
   --------|--------|--------|-----------------|-------------------
   images  | images | true   | 10485760        | {image/jpeg,image/png,...}
   models  | models | false  | 524288000       | null
   ```

---

## 🧪 测试数据库连接

### 插入测试数据

在 SQL Editor 中运行：

```sql
-- 插入测试任务
INSERT INTO public.jobs (job_id, status, progress_message, metadata)
VALUES (
    'test_job_001',
    'UPLOAD',
    '测试任务',
    '{"test": true, "created_by": "manual"}'::jsonb
);

-- 查询测试数据
SELECT * FROM public.jobs WHERE job_id = 'test_job_001';

-- 清理测试数据
DELETE FROM public.jobs WHERE job_id = 'test_job_001';
```

---

## 🔍 常见问题

### Q1: 为什么在 storage schema 中看不到 jobs 表？

**A**: `jobs` 表在 `public` schema 中，不在 `storage` schema。请在 Table Editor 顶部切换 schema。

### Q2: 如何切换 Schema？

**A**: 在 Table Editor 页面顶部，有一个下拉菜单：
```
┌─────────────────┐
│ schema: storage ▼│  ← 点击这里
└─────────────────┘
```
选择 `public` 即可。

### Q3: Storage Buckets 在哪里？

**A**: Buckets 不在 Table Editor 中，而是在左侧菜单的 **Storage** 选项中。

### Q4: 如何验证表确实创建成功了？

**A**: 运行以下 SQL：
```sql
-- 方法1：查询系统表
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'jobs'
) AS jobs_exists,
EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'inference_results'
) AS inference_results_exists;

-- 期望结果: jobs_exists=true, inference_results_exists=true
```

---

## 📊 数据库结构概览

```
Supabase 项目
│
├── Schemas
│   ├── public (您的应用数据) ⭐
│   │   ├── jobs
│   │   └── inference_results
│   │
│   ├── storage (Storage 系统表)
│   │   ├── buckets
│   │   ├── objects
│   │   └── ...
│   │
│   └── auth (认证系统表)
│       └── users
│
└── Storage
    ├── images (Bucket)
    └── models (Bucket)
```

---

## 🛠️ 从代码连接验证

运行以下 Python 脚本验证连接：

```python
from supabase import create_client

supabase = create_client(
    "https://jzkejgtalihqvomdwjrs.supabase.co",
    "your-key"
)

# 测试查询
response = supabase.table("jobs").select("*").limit(5).execute()
print(f"✅ 成功连接！找到 {len(response.data)} 条记录")

# 测试插入
test_job = {
    "job_id": "test_from_python",
    "status": "UPLOAD",
    "progress_message": "Python 测试",
    "metadata": {"source": "python_test"}
}

insert_response = supabase.table("jobs").insert(test_job).execute()
print(f"✅ 插入成功！ID: {insert_response.data[0]['id']}")

# 清理
delete_response = supabase.table("jobs").delete().eq("job_id", "test_from_python").execute()
print(f"✅ 清理完成！")
```

---

## 📞 需要帮助？

如果仍然找不到表，请提供以下信息：

1. **运行此 SQL 的结果**：
   ```sql
   SELECT schemaname, tablename 
   FROM pg_tables 
   WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
   ORDER BY schemaname, tablename;
   ```

2. **Table Editor 截图**（显示 schema 选择器）

3. **SQL Editor 中运行 `SELECT * FROM public.jobs;` 的结果**

---

## ✅ 快速检查清单

- [ ] 已在 SQL Editor 执行 `setup_supabase.sql`
- [ ] 已创建 `images` bucket (public)
- [ ] 已创建 `models` bucket (private)
- [ ] 在 Table Editor 中切换到 `public` schema
- [ ] 能看到 `jobs` 表
- [ ] 能看到 `inference_results` 表
- [ ] 运行测试查询成功

---

<div align="center">

**🎉 如果您看到了表，恭喜！数据库配置完成！**

</div>


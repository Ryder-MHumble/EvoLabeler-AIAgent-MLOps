# Supabase API Key 问题解决方案

## 问题诊断

您当前使用的是新的 `publishable` key 格式（`sb_publishable__...`），但 Supabase Python SDK 2.9.0 还不完全支持这个新格式，导致 "Invalid API key" 错误。

## 解决方案

### 方案 1: 使用 SQL 脚本（推荐，最简单）✅

这是最可靠的方法，不需要修改任何配置：

1. **打开 Supabase Dashboard**
   - 访问：https://app.supabase.com/project/jzkejgtalihqvomdwjrs
   - 登录您的账户

2. **进入 SQL Editor**
   - 左侧菜单 → "SQL Editor"

3. **执行 SQL 脚本**
   - 打开文件：`backend/scripts/insert_test_data.sql`
   - 复制全部内容
   - 粘贴到 SQL Editor
   - 点击 "Run" 执行

4. **验证数据**
   - 执行完成后会显示统计信息
   - 或进入 "Table Editor" 查看 `jobs` 和 `inference_results` 表

**优点**：
- ✅ 不需要修改配置
- ✅ 不依赖 Python SDK
- ✅ 100% 可靠
- ✅ 可以立即看到结果

### 方案 2: 使用旧的 anon key

如果您想继续使用 Python 脚本，需要找到旧的 `anon` key：

1. **在 Supabase Dashboard 中找到 anon key**
   - 访问：https://app.supabase.com/project/jzkejgtalihqvomdwjrs/settings/api
   - 查找 "Project API keys" 部分
   - 找到 `anon` `public` key（格式类似：`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`）
   - 如果只看到 `publishable` key，说明项目已经迁移到新系统

2. **更新 .env 文件**
   ```bash
   cd backend
   # 编辑 .env 文件，将 SUPABASE_KEY 改为 anon key
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # 使用 anon key
   ```

3. **运行 Python 脚本**
   ```bash
   python scripts/insert_test_data.py
   ```

**注意**：如果 Dashboard 中只有 `publishable` key，说明项目已迁移，只能使用 SQL 脚本。

### 方案 3: 等待 SDK 更新

Supabase 正在迁移到新的 API key 系统，未来版本的 Python SDK 可能会支持 `publishable` key。但目前（2025年1月），建议使用方案 1。

## 推荐操作

**立即执行**：使用方案 1（SQL 脚本）

这是最快、最可靠的方法，5 分钟即可完成数据插入。

## 验证数据

执行 SQL 脚本后，运行验证：

```bash
cd backend
python scripts/verify_supabase_data.py
```

或者直接在 Supabase Dashboard 的 Table Editor 中查看。




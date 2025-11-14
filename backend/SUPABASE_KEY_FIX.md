# Supabase API Key 配置问题修复指南

## 问题描述
当前配置中使用了 **publishable key** 作为后端 service key，这会导致 "Invalid API key" 错误。

## 解决方案

### 1. 获取正确的 Service Role Key

1. 登录 [Supabase 控制台](https://supabase.com/dashboard)
2. 选择你的项目：`jzkejgtalihqvomdwjrs`
3. 点击左侧菜单 **Settings** > **API**
4. 在 **Project API keys** 部分，找到：
   - **service_role** secret
   - 这个 key 以 `sb_service_` 开头

### 2. 更新 .env 文件

将获取到的 service role key 更新到 `.env` 文件中：

```bash
# 修改这行：
SUPABASE_SERVICE_KEY=sb_service_你的实际service_key
```

### 3. 当前配置对比

**错误的配置（当前）：**
```env
SUPABASE_KEY=sb_publishable__Lfmtm_55MhQlknQTfiEPw_alSivrvJ
SUPABASE_SERVICE_KEY=sb_publishable__Lfmtm_55MhQlknQTfiEPw_alSivrvJ  # ❌ 错误：使用的是 publishable key
```

**正确的配置：**
```env
SUPABASE_KEY=sb_publishable__Lfmtm_55MhQlknQTfiEPw_alSivrvJ          # ✅ 前端使用
SUPABASE_SERVICE_KEY=sb_service_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx    # ✅ 后端使用
```

### 4. 验证修复

更新配置后，运行验证脚本：

```bash
cd backend
python scripts/verify_supabase_data.py
```

应该看到成功的连接信息。

## Key 类型说明

- **Publishable Key** (`sb_publishable_`): 用于前端客户端操作
- **Service Role Key** (`sb_service_`): 用于后端服务器操作，具有更高权限

## 安全提醒

⚠️ **重要安全提醒：**
- Service Role Key 具有最高权限，不要在前端代码中使用
- 不要将 `.env` 文件提交到版本控制系统
- 定期轮换 API keys 以增强安全性

#!/usr/bin/env python
"""
自动创建 Supabase 数据库表。

使用 Supabase Management API 或直接 SQL 执行来创建表。
"""

import sys
from pathlib import Path
import httpx
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


async def execute_sql_via_api(sql: str) -> dict:
    """
    通过 Supabase REST API 执行 SQL。
    
    Args:
        sql: SQL 语句
        
    Returns:
        API 响应
    """
    # Supabase Management API endpoint
    url = f"{settings.supabase_url}/rest/v1/rpc/exec"
    
    headers = {
        "apikey": settings.supabase_key,
        "Authorization": f"Bearer {settings.supabase_key}",
        "Content-Type": "application/json",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=headers,
            json={"query": sql},
            timeout=30.0
        )
        return response.json()


# SQL 创建脚本
CREATE_TABLES_SQL = """
-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建 jobs 表
CREATE TABLE IF NOT EXISTS public.jobs (
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

-- 创建 jobs 表索引
CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON public.jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON public.jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON public.jobs(created_at DESC);

-- 创建 inference_results 表
CREATE TABLE IF NOT EXISTS public.inference_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id TEXT NOT NULL,
    image_path TEXT NOT NULL,
    predictions JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建 inference_results 表索引
CREATE INDEX IF NOT EXISTS idx_inference_results_job_id ON public.inference_results(job_id);

-- 创建自动更新 updated_at 的函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
DROP TRIGGER IF EXISTS update_jobs_updated_at ON public.jobs;
CREATE TRIGGER update_jobs_updated_at
    BEFORE UPDATE ON public.jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 授予权限
GRANT ALL ON public.jobs TO anon, authenticated;
GRANT ALL ON public.inference_results TO anon, authenticated;
"""


def print_manual_instructions():
    """打印手动创建表的说明。"""
    print("""
╔════════════════════════════════════════════════════════════╗
║          手动创建数据表说明                                ║
╚════════════════════════════════════════════════════════════╝

由于 Supabase Python SDK 的限制，请按以下步骤手动创建数据表：

📋 步骤 1: 访问 Supabase Dashboard
-----------------------------------------
打开浏览器，访问:
https://app.supabase.com/project/jzkejgtalihqvomdwjrs

📋 步骤 2: 打开 SQL Editor
-----------------------------------------
在左侧菜单中点击 "SQL Editor"

📋 步骤 3: 执行 SQL 脚本
-----------------------------------------
复制并执行 scripts/setup_supabase.sql 中的 SQL 语句

或者直接复制以下 SQL：

""")
    print(CREATE_TABLES_SQL)
    print("""
📋 步骤 4: 创建 Storage Buckets
-----------------------------------------
1. 在左侧菜单点击 "Storage"
2. 创建两个 Bucket:
   
   a) images bucket:
      - Name: images
      - Public: Yes
      - File size limit: 10 MB
      - Allowed MIME types: image/jpeg, image/png, image/gif

   b) models bucket:
      - Name: models
      - Public: No
      - File size limit: 500 MB

📋 步骤 5: 验证
-----------------------------------------
运行以下命令验证设置:
  poetry run python scripts/setup_database.py

════════════════════════════════════════════════════════════
""")


async def create_tables_programmatically():
    """尝试以编程方式创建表。"""
    print("正在尝试通过 API 创建表...")
    
    from supabase import create_client
    
    try:
        client = create_client(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_key,
        )
        
        # 分别执行每个 SQL 语句
        sql_statements = [
            'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"',
            CREATE_TABLES_SQL,
        ]
        
        print("⚠️  注意：由于 Supabase Python SDK 的限制，")
        print("   我们无法直接通过 SDK 执行 DDL 语句。")
        print("\n请参考下面的手动创建说明。\n")
        
        return False
        
    except Exception as e:
        print(f"❌ API 创建失败: {e}")
        return False


def main():
    """主函数。"""
    print("""
╔════════════════════════════════════════════════════════════╗
║      EvoLabeler-Backend 自动创建数据表工具                ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # 尝试程序化创建
    success = asyncio.run(create_tables_programmatically())
    
    if not success:
        # 显示手动创建说明
        print_manual_instructions()
        
        print("\n💡 提示：")
        print("   创建表后，再次运行 setup_database.py 来验证:")
        print("   poetry run python scripts/setup_database.py\n")


if __name__ == "__main__":
    main()


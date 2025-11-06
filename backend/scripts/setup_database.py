#!/usr/bin/env python
"""
自动设置 Supabase 数据库表结构。

此脚本会：
1. 连接到 Supabase
2. 创建必需的数据表
3. 创建索引
4. 验证设置
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client, Client
from app.core.config import settings


def create_supabase_client() -> Client:
    """创建 Supabase 客户端。"""
    print(f"正在连接到 Supabase: {settings.supabase_url}")
    client = create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_key,
    )
    print("✅ Supabase 连接成功")
    return client


def setup_tables(client: Client) -> None:
    """
    设置数据库表。
    
    注意：Supabase 的 Python SDK 不直接支持 DDL 操作。
    这些操作需要在 Supabase Dashboard 的 SQL 编辑器中执行。
    
    此函数用于验证连接和表是否存在。
    """
    print("\n" + "="*60)
    print("数据库表设置说明")
    print("="*60)
    
    print("""
请在 Supabase Dashboard 中执行以下步骤：

1. 打开 Supabase 项目: https://jzkejgtalihqvomdwjrs.supabase.co
2. 进入 SQL Editor
3. 执行 scripts/setup_supabase.sql 中的 SQL 语句

或者手动创建以下表：

-- Jobs 表
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    progress_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);

-- Inference Results 表
CREATE TABLE IF NOT EXISTS inference_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id TEXT NOT NULL,
    image_path TEXT NOT NULL,
    predictions JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_inference_results_job_id ON inference_results(job_id);

-- Storage Buckets（需要在 Storage 界面创建）
-- Bucket: images (public, 10MB limit)
-- Bucket: models (private, 500MB limit)
""")
    
    print("="*60)


def verify_connection(client: Client) -> bool:
    """
    验证 Supabase 连接和表是否存在。
    
    Returns:
        True 如果连接成功且表存在，否则 False
    """
    print("\n正在验证数据库连接...")
    
    try:
        # 尝试查询 jobs 表
        response = client.table("jobs").select("*").limit(1).execute()
        print("✅ jobs 表存在且可访问")
        
        # 尝试查询 inference_results 表
        response = client.table("inference_results").select("*").limit(1).execute()
        print("✅ inference_results 表存在且可访问")
        
        print("\n✅ 所有数据表验证成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 数据表验证失败: {e}")
        print("\n请确保：")
        print("1. 已在 Supabase Dashboard 中创建了数据表")
        print("2. 使用了正确的 API Key")
        print("3. 表名称和结构正确")
        return False


def test_insert(client: Client) -> bool:
    """
    测试插入数据。
    
    Returns:
        True 如果插入成功，否则 False
    """
    print("\n正在测试数据插入...")
    
    try:
        import uuid
        from datetime import datetime
        
        test_job_id = f"test_{uuid.uuid4()}"
        
        # 插入测试数据
        data = {
            "job_id": test_job_id,
            "status": "TEST",
            "progress_message": "测试数据",
            "metadata": {"test": True},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        response = client.table("jobs").insert(data).execute()
        print(f"✅ 测试数据插入成功: {test_job_id}")
        
        # 查询测试数据
        response = client.table("jobs").select("*").eq("job_id", test_job_id).execute()
        if response.data:
            print(f"✅ 测试数据查询成功")
        
        # 删除测试数据
        client.table("jobs").delete().eq("job_id", test_job_id).execute()
        print(f"✅ 测试数据已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据操作失败: {e}")
        return False


def main() -> None:
    """主函数。"""
    print("""
╔════════════════════════════════════════════════════════════╗
║          EvoLabeler-Backend 数据库设置工具                ║
╚════════════════════════════════════════════════════════════╝
""")
    
    try:
        # 1. 创建客户端
        client = create_supabase_client()
        
        # 2. 显示设置说明
        setup_tables(client)
        
        # 3. 验证连接
        if verify_connection(client):
            # 4. 测试插入
            if test_insert(client):
                print("\n" + "="*60)
                print("🎉 数据库设置和验证完成！")
                print("="*60)
                print("\n现在可以启动应用程序:")
                print("  poetry run python run.py")
                print("\n或访问 API 文档:")
                print("  http://localhost:8000/docs")
                print("="*60 + "\n")
            else:
                print("\n⚠️  数据插入测试失败，请检查权限设置")
        else:
            print("\n⚠️  请先在 Supabase Dashboard 中创建数据表")
            print("详细说明请参考上面的 SQL 语句")
        
    except Exception as e:
        print(f"\n❌ 设置失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


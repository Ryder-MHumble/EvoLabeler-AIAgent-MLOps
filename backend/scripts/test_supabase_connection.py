#!/usr/bin/env python
"""
测试 Supabase 连接的脚本。

用于诊断 API key 问题。
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from supabase import create_client

print("\n" + "="*70)
print("Supabase 连接测试")
print("="*70)

print(f"\n📋 配置信息:")
print(f"   URL: {settings.supabase_url}")
print(f"   Key 前缀: {settings.supabase_key[:20]}...")
print(f"   Key 类型: {'publishable' if 'publishable' in settings.supabase_key else 'anon' if 'anon' in settings.supabase_key.lower() else 'unknown'}")

print("\n🔍 测试连接...")

try:
    # 尝试使用当前配置
    client = create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_key,
    )
    
    # 尝试一个简单的查询
    print("   ✅ 客户端创建成功")
    print("   🔍 测试查询...")
    
    try:
        response = client.table("jobs").select("job_id", count="exact").limit(1).execute()
        print(f"   ✅ 查询成功！找到 {response.count if hasattr(response, 'count') else len(response.data) if response.data else 0} 条记录")
        print("\n✅ Supabase 连接正常！")
        print("\n💡 如果之前插入数据失败，可能是其他原因（如权限问题）")
        print("   建议直接使用 SQL 脚本插入数据：backend/scripts/insert_test_data.sql")
    except Exception as e:
        print(f"   ⚠️  查询失败: {e}")
        print("\n💡 可能的原因：")
        print("   1. 表不存在 - 请先运行 setup_supabase.sql 创建表")
        print("   2. 权限问题 - 检查 RLS (Row Level Security) 策略")
        print("   3. API key 权限不足 - 可能需要使用 service_role key")
        
except Exception as e:
    print(f"   ❌ 连接失败: {e}")
    print("\n💡 解决方案：")
    print("   1. 检查 Supabase Dashboard > Settings > API")
    print("   2. 找到 'Project API keys' 部分")
    print("   3. 如果看到 'anon' key，尝试使用它（而不是 publishable key）")
    print("   4. 或者直接使用 SQL 脚本：backend/scripts/insert_test_data.sql")
    print("\n   注意：新的 publishable key 可能需要更新 Supabase Python SDK")
    print("   当前 SDK 版本可能还不完全支持新的 key 格式")

print("\n" + "="*70 + "\n")




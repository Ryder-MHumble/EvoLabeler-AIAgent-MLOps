#!/usr/bin/env python
"""
验证 Supabase 数据脚本。

检查 jobs 和 inference_results 表中是否有数据。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.db.supabase_init import get_supabase_client
    from app.tools.supabase_client import SupabaseClient
    
    print("\n" + "="*70)
    print("Supabase 数据验证脚本")
    print("="*70)
    
    # 初始化客户端
    print("\n1️⃣  初始化 Supabase 客户端...")
    try:
        supabase_client = SupabaseClient()
        print("   ✅ Supabase 客户端初始化成功\n")
    except Exception as e:
        print(f"   ❌ 初始化失败: {e}")
        print("\n💡 请检查:")
        print("   1. .env 文件是否存在")
        print("   2. SUPABASE_URL 和 SUPABASE_KEY 是否正确配置")
        sys.exit(1)
    
    # 检查 jobs 表
    print("2️⃣  检查 jobs 表...")
    try:
        jobs_response = supabase_client.client.table("jobs").select("*", count="exact").execute()
        jobs_count = jobs_response.count if hasattr(jobs_response, 'count') else len(jobs_response.data) if jobs_response.data else 0
        jobs_data = jobs_response.data if jobs_response.data else []
        
        print(f"   📊 Jobs 表记录数: {jobs_count}")
        
        if jobs_count > 0:
            print(f"\n   ✅ 找到 {jobs_count} 条记录:")
            for i, job in enumerate(jobs_data[:5], 1):  # 只显示前5条
                print(f"      {i}. {job.get('job_id', 'N/A')} - {job.get('status', 'N/A')}")
            if jobs_count > 5:
                print(f"      ... 还有 {jobs_count - 5} 条记录")
        else:
            print("   ⚠️  Jobs 表为空，需要运行 insert_test_data.py")
    except Exception as e:
        print(f"   ❌ 查询失败: {e}")
    
    # 检查 inference_results 表
    print("\n3️⃣  检查 inference_results 表...")
    try:
        results_response = supabase_client.client.table("inference_results").select("*", count="exact").execute()
        results_count = results_response.count if hasattr(results_response, 'count') else len(results_response.data) if results_response.data else 0
        results_data = results_response.data if results_response.data else []
        
        print(f"   📊 Inference Results 表记录数: {results_count}")
        
        if results_count > 0:
            print(f"\n   ✅ 找到 {results_count} 条记录:")
            # 按 job_id 分组统计
            job_ids = {}
            for result in results_data:
                job_id = result.get('job_id', 'N/A')
                job_ids[job_id] = job_ids.get(job_id, 0) + 1
            
            for job_id, count in list(job_ids.items())[:5]:
                print(f"      - {job_id}: {count} 条推理结果")
            if len(job_ids) > 5:
                print(f"      ... 还有 {len(job_ids) - 5} 个任务")
        else:
            print("   ⚠️  Inference Results 表为空，需要运行 insert_test_data.py")
    except Exception as e:
        print(f"   ❌ 查询失败: {e}")
    
    # 总结
    print("\n" + "="*70)
    if jobs_count > 0 and results_count > 0:
        print("✅ 数据验证完成：两个表都有数据")
    elif jobs_count > 0:
        print("⚠️  数据验证完成：jobs 表有数据，但 inference_results 表为空")
    elif results_count > 0:
        print("⚠️  数据验证完成：inference_results 表有数据，但 jobs 表为空")
    else:
        print("❌ 数据验证完成：两个表都为空，请运行 insert_test_data.py 插入测试数据")
    print("="*70 + "\n")
    
except ImportError as e:
    print(f"\n❌ 导入错误: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


#!/usr/bin/env python
"""
向 Supabase 插入测试数据脚本。

此脚本会：
1. 创建多个测试任务（jobs）
2. 爬取一些遥感影像图片
3. 上传图片到 Supabase Storage
4. 创建推理结果记录（inference_results）
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import random

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.supabase_init import get_supabase_client
from app.tools.supabase_client import SupabaseClient
from app.core.logging_config import get_logger

logger = get_logger(__name__)


async def crawl_sample_images(max_images: int = 10) -> list[dict]:
    """
    爬取一些示例遥感影像图片。
    
    Args:
        max_images: 最大图片数量
        
    Returns:
        图片信息列表，包含 URL 和元数据
    """
    try:
        from playwright.async_api import async_playwright
        import httpx
        
        print(f"\n🔍 开始爬取 {max_images} 张遥感影像图片...")
        
        image_data = []
        search_queries = ["遥感影像", "卫星图像", "航拍图像"]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            images_collected = 0
            
            for query in search_queries:
                if images_collected >= max_images:
                    break
                    
                print(f"   搜索关键词: {query}")
                search_url = f"https://www.bing.com/images/search?q={query}&first=1"
                
                try:
                    await page.goto(search_url, wait_until="networkidle", timeout=10000)
                    await page.wait_for_selector("img.mimg", timeout=5000)
                    
                    image_elements = await page.query_selector_all("img.mimg")
                    
                    for img in image_elements:
                        if images_collected >= max_images:
                            break
                            
                        src = await img.get_attribute("src")
                        if src and (src.startswith("http") or src.startswith("https")):
                            # 验证图片是否可访问
                            try:
                                async with httpx.AsyncClient(timeout=5.0) as client:
                                    response = await client.head(src)
                                    if response.status_code == 200:
                                        image_data.append({
                                            "url": src,
                                            "query": query,
                                            "index": images_collected + 1
                                        })
                                        images_collected += 1
                                        print(f"   ✅ 找到图片 {images_collected}/{max_images}")
                            except:
                                continue
                                
                except Exception as e:
                    print(f"   ⚠️  搜索 {query} 时出错: {e}")
                    continue
            
            await browser.close()
        
        print(f"\n✅ 成功爬取 {len(image_data)} 张图片\n")
        return image_data
        
    except ImportError:
        print("⚠️  Playwright 未安装，使用模拟图片数据")
        # 返回模拟数据
        return [
            {"url": f"https://example.com/satellite_{i}.jpg", "query": "遥感影像", "index": i}
            for i in range(1, max_images + 1)
        ]
    except Exception as e:
        print(f"⚠️  爬取图片失败: {e}，使用模拟数据")
        return [
            {"url": f"https://example.com/satellite_{i}.jpg", "query": "遥感影像", "index": i}
            for i in range(1, max_images + 1)
        ]


async def upload_image_to_storage(
    supabase_client: SupabaseClient,
    image_url: str,
    job_id: str,
    image_index: int
) -> str:
    """
    上传图片到 Supabase Storage。
    
    Args:
        supabase_client: Supabase 客户端
        image_url: 图片 URL
        job_id: 任务 ID
        image_index: 图片索引
        
    Returns:
        存储路径
    """
    try:
        import httpx
        
        # 下载图片
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(image_url, follow_redirects=True)
            if response.status_code != 200:
                raise Exception(f"下载图片失败: {response.status_code}")
            
            image_data = response.content
            
        # 确定文件扩展名
        extension = ".jpg"
        if ".png" in image_url.lower():
            extension = ".png"
        elif ".webp" in image_url.lower():
            extension = ".webp"
        
        # 构建存储路径
        storage_path = f"{job_id}/images/image_{image_index:03d}{extension}"
        
        # 上传到 Supabase Storage
        try:
            supabase_client.client.storage.from_("images").upload(
                path=storage_path,
                file=image_data,
                file_options={"content-type": f"image/{extension[1:]}"}
            )
            print(f"   ✅ 上传图片: {storage_path}")
            return storage_path
        except Exception as e:
            # 如果 bucket 不存在，跳过上传
            print(f"   ⚠️  上传失败（可能 bucket 不存在）: {e}")
            return storage_path
            
    except Exception as e:
        print(f"   ⚠️  处理图片失败: {e}")
        return f"{job_id}/images/image_{image_index:03d}.jpg"


async def create_test_jobs(supabase_client: SupabaseClient, num_jobs: int = 5):
    """创建测试任务。"""
    print(f"\n📝 创建 {num_jobs} 个测试任务...")
    
    job_statuses = [
        "UPLOAD",
        "INFERENCE",
        "ANALYSIS",
        "ACQUISITION",
        "PSEUDO_LABELING",
        "TRAINING",
        "COMPLETE",
        "FAILED"
    ]
    
    progress_messages = [
        "正在上传种子数据...",
        "正在进行推理分析...",
        "正在分析数据质量...",
        "正在采集新样本...",
        "正在生成伪标签...",
        "正在训练模型...",
        "任务已完成",
        "任务执行失败"
    ]
    
    jobs = []
    
    for i in range(1, num_jobs + 1):
        status = random.choice(job_statuses)
        status_index = job_statuses.index(status)
        
        job_id = f"test_job_{datetime.now().strftime('%Y%m%d')}_{i:03d}"
        
        # 创建时间：随机分布在过去7天内
        days_ago = random.randint(0, 7)
        created_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
        updated_at = (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat()
        
        metadata = {
            "project_name": f"测试项目 {i}",
            "description": f"这是一个测试项目，用于验证系统功能",
            "model_type": random.choice(["YOLOv8", "YOLOv9", "YOLOv10"]),
            "dataset_size": random.randint(100, 1000),
            "accuracy": round(random.uniform(0.65, 0.95), 3) if status == "COMPLETE" else None,
            "epochs": random.randint(10, 100) if status in ["TRAINING", "COMPLETE"] else None,
            "created_by": "test_script"
        }
        
        job_data = {
            "job_id": job_id,
            "status": status,
            "progress_message": progress_messages[status_index] if status_index < len(progress_messages) else None,
            "metadata": metadata,
            "created_at": created_at,
            "updated_at": updated_at
        }
        
        try:
            response = supabase_client.client.table("jobs").insert(job_data).execute()
            jobs.append(response.data[0] if response.data else job_data)
            print(f"   ✅ 创建任务: {job_id} ({status})")
        except Exception as e:
            print(f"   ⚠️  创建任务失败: {job_id} ({e})")
            # 如果已存在，尝试更新
            try:
                update_data = {k: v for k, v in job_data.items() if k != "job_id"}
                supabase_client.client.table("jobs").update(update_data).eq("job_id", job_id).execute()
                print(f"   ✅ 更新任务: {job_id}")
            except:
                pass
    
    print(f"\n✅ 成功创建/更新 {len(jobs)} 个任务\n")
    return jobs


async def create_test_inference_results(
    supabase_client: SupabaseClient,
    jobs: list[dict],
    images_per_job: int = 3
):
    """为每个任务创建推理结果。"""
    print(f"\n🔬 为每个任务创建 {images_per_job} 条推理结果...")
    
    # 爬取一些图片
    all_images = await crawl_sample_images(max_images=len(jobs) * images_per_job)
    
    object_classes = ["ship", "airplane", "vehicle", "building", "road", "bridge", "port"]
    
    total_created = 0
    
    for job_idx, job in enumerate(jobs):
        job_id = job["job_id"]
        print(f"\n   处理任务: {job_id}")
        
        # 为这个任务分配图片
        start_idx = job_idx * images_per_job
        job_images = all_images[start_idx:start_idx + images_per_job]
        
        for img_idx, img_info in enumerate(job_images, 1):
            # 生成模拟预测结果
            num_detections = random.randint(1, 5)
            predictions = []
            
            for det_idx in range(num_detections):
                predictions.append({
                    "class": random.choice(object_classes),
                    "confidence": round(random.uniform(0.5, 0.95), 3),
                    "bbox": [
                        round(random.uniform(0, 0.7), 2),  # x
                        round(random.uniform(0, 0.7), 2),  # y
                        round(random.uniform(0.2, 0.3), 2),  # width
                        round(random.uniform(0.2, 0.3), 2)   # height
                    ]
                })
            
            # 尝试上传图片（如果可能）
            try:
                image_path = await upload_image_to_storage(
                    supabase_client,
                    img_info["url"],
                    job_id,
                    img_idx
                )
            except:
                image_path = f"{job_id}/images/image_{img_idx:03d}.jpg"
            
            # 创建推理结果记录
            inference_data = {
                "job_id": job_id,
                "image_path": image_path,
                "predictions": predictions,
                "created_at": (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat()
            }
            
            try:
                response = supabase_client.client.table("inference_results").insert(inference_data).execute()
                total_created += 1
                print(f"   ✅ 创建推理结果 {img_idx}/{images_per_job}: {len(predictions)} 个检测")
            except Exception as e:
                print(f"   ⚠️  创建推理结果失败: {e}")
    
    print(f"\n✅ 成功创建 {total_created} 条推理结果记录\n")


async def main():
    """主函数。"""
    print("\n" + "="*70)
    print("Supabase 测试数据插入脚本")
    print("="*70)
    
    try:
        # 初始化 Supabase 客户端
        print("\n1️⃣  初始化 Supabase 客户端...")
        supabase_client = SupabaseClient()
        print("   ✅ Supabase 客户端初始化成功\n")
        
        # 创建测试任务
        print("2️⃣  创建测试任务...")
        jobs = await create_test_jobs(supabase_client, num_jobs=5)
        
        # 创建推理结果
        print("3️⃣  创建推理结果...")
        await create_test_inference_results(supabase_client, jobs, images_per_job=3)
        
        # 验证数据
        print("4️⃣  验证数据...")
        jobs_count = supabase_client.client.table("jobs").select("*", count="exact").execute()
        results_count = supabase_client.client.table("inference_results").select("*", count="exact").execute()
        
        print(f"\n📊 数据统计:")
        print(f"   - Jobs 表: {jobs_count.count if hasattr(jobs_count, 'count') else len(jobs_count.data)} 条记录")
        print(f"   - Inference Results 表: {results_count.count if hasattr(results_count, 'count') else len(results_count.data)} 条记录")
        
        print("\n" + "="*70)
        print("✅ 测试数据插入完成！")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


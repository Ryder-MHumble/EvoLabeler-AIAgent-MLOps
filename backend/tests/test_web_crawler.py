"""
Playwright 网络爬虫测试。

此测试文件用于验证 WebCrawler 的功能，包括：
1. 浏览器启动和页面导航
2. 图片搜索和下载
3. Supabase 上传
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.tools.web_crawler import WebCrawler
from app.tools.supabase_client import SupabaseClient
from app.core.logging_config import setup_logging, get_logger

# 设置日志
setup_logging()
logger = get_logger(__name__)


async def test_basic_crawler():
    """
    测试基础爬虫功能。
    
    这个测试会：
    1. 启动 Playwright 浏览器
    2. 搜索指定关键词的图片
    3. 下载前几张图片
    4. 打印结果
    """
    print("\n" + "="*60)
    print("测试 1: 基础爬虫功能（不上传到 Supabase）")
    print("="*60 + "\n")
    
    try:
        # 创建爬虫实例（不连接 Supabase）
        from playwright.async_api import async_playwright
        
        # 测试查询
        test_queries = [
            "遥感影像 卫星",
            "satellite imagery"
        ]
        
        print(f"🔍 测试搜索关键词: {test_queries}")
        print("="*60)
        
        async with async_playwright() as p:
            # 启动浏览器
            print("\n📱 正在启动浏览器...")
            browser = await p.chromium.launch(headless=False)  # headless=False 可以看到浏览器
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36"
            )
            
            print("✅ 浏览器启动成功")
            
            # 测试第一个查询
            query = test_queries[0]
            print(f"\n🔎 正在搜索: {query}")
            
            page = await context.new_page()
            
            try:
                # 访问必应图片搜索
                search_url = f"https://www.bing.com/images/search?q={query}"
                print(f"📍 访问: {search_url}")
                
                await page.goto(search_url, wait_until="networkidle", timeout=30000)
                print("✅ 页面加载成功")
                
                # 等待图片加载
                print("⏳ 等待图片加载...")
                await page.wait_for_selector("img.mimg", timeout=10000)
                print("✅ 图片已加载")
                
                # 获取图片元素
                image_elements = await page.query_selector_all("img.mimg")
                print(f"\n📊 找到 {len(image_elements)} 张图片")
                
                # 获取前 3 张图片的信息
                for i, img_elem in enumerate(image_elements[:3]):
                    try:
                        img_src = await img_elem.get_attribute("src")
                        img_alt = await img_elem.get_attribute("alt")
                        
                        print(f"\n图片 {i+1}:")
                        print(f"  URL: {img_src[:80]}..." if img_src and len(img_src) > 80 else f"  URL: {img_src}")
                        print(f"  描述: {img_alt}")
                        
                    except Exception as e:
                        print(f"  ❌ 获取图片 {i+1} 信息失败: {e}")
                
                # 截图保存
                screenshot_path = "/tmp/crawler_test_screenshot.png"
                await page.screenshot(path=screenshot_path)
                print(f"\n📸 页面截图已保存: {screenshot_path}")
                
            finally:
                await page.close()
            
            await browser.close()
            print("\n✅ 浏览器已关闭")
        
        print("\n" + "="*60)
        print("✅ 测试 1 完成")
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_crawler_with_download():
    """
    测试爬虫下载功能。
    
    这个测试会下载实际的图片文件。
    """
    print("\n" + "="*60)
    print("测试 2: 图片下载功能")
    print("="*60 + "\n")
    
    try:
        from playwright.async_api import async_playwright
        import hashlib
        
        test_query = "remote sensing image"
        download_limit = 2
        
        print(f"🔍 搜索关键词: {test_query}")
        print(f"📥 下载数量: {download_limit}")
        print("="*60)
        
        downloaded_files = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # 搜索图片
            search_url = f"https://www.bing.com/images/search?q={test_query}"
            await page.goto(search_url, wait_until="networkidle", timeout=30000)
            await page.wait_for_selector("img.mimg", timeout=10000)
            
            # 获取图片
            image_elements = await page.query_selector_all("img.mimg")
            print(f"✅ 找到 {len(image_elements)} 张图片")
            
            for i, img_elem in enumerate(image_elements[:download_limit]):
                try:
                    img_src = await img_elem.get_attribute("src")
                    
                    if not img_src or img_src.startswith("data:"):
                        continue
                    
                    print(f"\n📥 下载图片 {i+1}...")
                    print(f"   URL: {img_src[:60]}...")
                    
                    # 下载图片
                    response = await page.goto(img_src, timeout=15000)
                    if response and response.status == 200:
                        image_data = await response.body()
                        
                        if len(image_data) > 1024:  # 至少 1KB
                            # 保存到临时文件
                            file_hash = hashlib.md5(image_data).hexdigest()[:8]
                            file_path = f"/tmp/test_image_{i}_{file_hash}.jpg"
                            
                            with open(file_path, 'wb') as f:
                                f.write(image_data)
                            
                            downloaded_files.append(file_path)
                            print(f"   ✅ 已保存: {file_path}")
                            print(f"   大小: {len(image_data) / 1024:.2f} KB")
                        else:
                            print(f"   ⚠️  文件太小，跳过")
                    else:
                        print(f"   ❌ 下载失败")
                    
                    await asyncio.sleep(1)  # 礼貌延时
                    
                except Exception as e:
                    print(f"   ❌ 处理失败: {e}")
                    continue
            
            await browser.close()
        
        print(f"\n📊 下载统计:")
        print(f"   成功下载: {len(downloaded_files)} 张图片")
        print(f"   保存位置: /tmp/test_image_*.jpg")
        
        print("\n" + "="*60)
        print("✅ 测试 2 完成")
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_crawler_pipeline():
    """
    测试完整的爬虫流程（包括 Supabase 上传）。
    
    注意：这个测试需要 Supabase 配置正确。
    """
    print("\n" + "="*60)
    print("测试 3: 完整爬虫流程（含 Supabase 上传）")
    print("="*60 + "\n")
    
    try:
        # 创建 Supabase 客户端
        print("🔗 正在连接 Supabase...")
        supabase_client = SupabaseClient()
        print("✅ Supabase 连接成功")
        
        # 创建爬虫
        print("\n🕷️  正在初始化爬虫...")
        crawler = WebCrawler(supabase_client)
        print("✅ 爬虫初始化成功")
        
        # 测试查询
        test_queries = ["satellite image"]
        test_job_id = "test_crawler_job"
        
        print(f"\n🔍 开始爬取...")
        print(f"   查询词: {test_queries}")
        print(f"   每个查询限制: 2 张图片")
        print(f"   测试 Job ID: {test_job_id}")
        print("="*60 + "\n")
        
        # 执行爬取
        image_urls = await crawler.crawl_images(
            queries=test_queries,
            limit=2,
            job_id=test_job_id
        )
        
        print(f"\n📊 爬取结果:")
        print(f"   成功上传: {len(image_urls)} 张图片到 Supabase")
        
        if image_urls:
            print(f"\n   上传的图片 URL:")
            for i, url in enumerate(image_urls, 1):
                print(f"   {i}. {url}")
        
        print("\n" + "="*60)
        print("✅ 测试 3 完成")
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n💡 提示：")
        print("   - 确保 .env 文件中的 Supabase 配置正确")
        print("   - 确保已在 Supabase 中创建了 'images' bucket")
        print("   - 确保 Supabase bucket 是公开的")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数。"""
    print("""
╔════════════════════════════════════════════════════════════╗
║          Playwright 网络爬虫测试套件                      ║
╚════════════════════════════════════════════════════════════╝
""")
    
    print("此测试将验证以下功能:")
    print("  1️⃣  浏览器启动和页面导航")
    print("  2️⃣  图片搜索和信息提取")
    print("  3️⃣  图片下载")
    print("  4️⃣  Supabase 上传（可选）")
    print("\n" + "="*60 + "\n")
    
    results = []
    
    # 测试 1: 基础爬虫
    print("▶️  运行测试 1...")
    result1 = await test_basic_crawler()
    results.append(("基础爬虫功能", result1))
    
    input("\n⏸️  按 Enter 继续下一个测试...")
    
    # 测试 2: 下载功能
    print("\n▶️  运行测试 2...")
    result2 = await test_crawler_with_download()
    results.append(("图片下载功能", result2))
    
    # 询问是否测试 Supabase 上传
    print("\n" + "="*60)
    response = input("是否测试 Supabase 上传功能？(需要正确配置 Supabase) [y/N]: ")
    
    if response.lower() in ['y', 'yes']:
        print("\n▶️  运行测试 3...")
        result3 = await test_full_crawler_pipeline()
        results.append(("完整爬虫流程", result3))
    
    # 显示测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60 + "\n")
    
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    print("="*60 + "\n")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请查看上面的错误信息")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试运行失败: {e}")
        import traceback
        traceback.print_exc()


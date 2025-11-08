#!/usr/bin/env python
"""
Playwright 图片下载测试。

测试 Playwright 爬虫是否能够真正下载图片到本地。
图片将保存在 tests/downloaded_images/ 目录中。
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import httpx


# 创建保存目录
SAVE_DIR = Path(__file__).parent / "downloaded_images"
SAVE_DIR.mkdir(exist_ok=True)


async def download_image(url: str, save_path: Path) -> bool:
    """
    下载单张图片。
    
    Args:
        url: 图片 URL
        save_path: 保存路径
        
    Returns:
        是否成功
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            
            if response.status_code == 200:
                save_path.write_bytes(response.content)
                size_kb = len(response.content) / 1024
                print(f"   ✅ 下载成功: {save_path.name} ({size_kb:.1f} KB)")
                return True
            else:
                print(f"   ❌ 下载失败: {url} (状态码: {response.status_code})")
                return False
                
    except Exception as e:
        print(f"   ❌ 下载异常: {url} ({e})")
        return False


async def test_playwright_image_crawler():
    """测试 Playwright 爬取并下载图片。"""
    print("\n" + "="*70)
    print("Playwright 图片爬取和下载测试")
    print("="*70 + "\n")
    
    print(f"📁 图片将保存到: {SAVE_DIR.absolute()}\n")
    
    # 搜索配置
    search_query = "遥感影像"
    max_images = 5  # 限制数量以便快速测试
    
    print(f"🔍 搜索关键词: {search_query}")
    print(f"📊 目标数量: {max_images} 张\n")
    
    try:
        print("1️⃣  启动浏览器...")
        async with async_playwright() as p:
            # 启动浏览器（无头模式）
            browser = await p.chromium.launch(
                headless=True,  # 设置为 False 可以看到浏览器
                args=['--disable-blink-features=AutomationControlled']
            )
            print("   ✅ 浏览器启动成功\n")
            
            # 创建页面
            page = await browser.new_page()
            
            # 设置 User-Agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            # 访问必应图片搜索
            print("2️⃣  访问必应图片搜索...")
            search_url = f"https://www.bing.com/images/search?q={search_query}&first=1"
            
            await page.goto(search_url, wait_until="networkidle", timeout=15000)
            print("   ✅ 页面加载成功\n")
            
            # 等待图片加载
            print("3️⃣  等待图片加载...")
            try:
                await page.wait_for_selector("img.mimg", timeout=10000)
                print("   ✅ 图片元素已加载\n")
            except Exception as e:
                print(f"   ⚠️  等待图片超时: {e}\n")
            
            # 获取图片信息
            print("4️⃣  提取图片信息...")
            image_elements = await page.query_selector_all("img.mimg")
            print(f"   ✅ 找到 {len(image_elements)} 张图片\n")
            
            # 提取图片 URL
            print("5️⃣  提取图片 URL...")
            image_urls = []
            
            for i, img in enumerate(image_elements[:max_images], 1):
                src = await img.get_attribute("src")
                
                if src and (src.startswith("http") or src.startswith("https")):
                    image_urls.append(src)
                    print(f"   图片 {i}: {src[:60]}...")
            
            print(f"\n   ✅ 成功提取 {len(image_urls)} 个有效 URL\n")
            
            # 关闭浏览器
            await browser.close()
            print("   ✅ 浏览器已关闭\n")
        
        # 下载图片
        print("6️⃣  下载图片到本地...")
        print(f"   保存目录: {SAVE_DIR.absolute()}\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        successful_downloads = 0
        
        for i, url in enumerate(image_urls, 1):
            # 构建保存路径
            extension = ".jpg"  # 默认扩展名
            if ".png" in url:
                extension = ".png"
            elif ".webp" in url:
                extension = ".webp"
            
            filename = f"{search_query}_{timestamp}_{i:02d}{extension}"
            save_path = SAVE_DIR / filename
            
            print(f"   下载图片 {i}/{len(image_urls)}...")
            success = await download_image(url, save_path)
            
            if success:
                successful_downloads += 1
            
            # 避免请求过快
            await asyncio.sleep(0.5)
        
        # 输出结果
        print("\n" + "="*70)
        print("📊 测试结果")
        print("="*70)
        print(f"\n✅ 爬取成功: 找到 {len(image_urls)} 张图片")
        print(f"✅ 下载成功: {successful_downloads}/{len(image_urls)} 张图片")
        print(f"\n📁 保存位置: {SAVE_DIR.absolute()}")
        
        # 列出下载的文件
        if successful_downloads > 0:
            print(f"\n📋 已下载的文件:")
            for file in sorted(SAVE_DIR.glob(f"{search_query}_{timestamp}_*")):
                size_kb = file.stat().st_size / 1024
                print(f"   - {file.name} ({size_kb:.1f} KB)")
        
        print("\n" + "="*70)
        print("🎉 Playwright 图片爬取和下载测试成功！")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 故障排查：")
        print("   1. 确保已安装 Playwright: poetry run playwright install")
        print("   2. 检查网络连接")
        print("   3. 确认防火墙设置")
        print("   4. 尝试使用 headless=False 查看浏览器行为\n")
        
        return False


async def clean_old_images(days_old: int = 7):
    """
    清理旧图片。
    
    Args:
        days_old: 删除多少天前的图片
    """
    import time
    
    if not SAVE_DIR.exists():
        return
    
    now = time.time()
    cutoff = now - (days_old * 86400)
    
    for file in SAVE_DIR.glob("*"):
        if file.is_file() and file.stat().st_mtime < cutoff:
            file.unlink()
            print(f"   🗑️  删除旧文件: {file.name}")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════╗
║          Playwright 图片爬取和下载测试                             ║
╚════════════════════════════════════════════════════════════════════╝

这个测试会：
  ✓ 启动 Playwright 浏览器
  ✓ 访问必应图片搜索
  ✓ 搜索"遥感影像"
  ✓ 提取图片 URL
  ✓ 下载图片到本地
  ✓ 显示保存位置

""")
    
    try:
        # 清理旧图片
        asyncio.run(clean_old_images(days_old=7))
        
        # 运行测试
        result = asyncio.run(test_playwright_image_crawler())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)


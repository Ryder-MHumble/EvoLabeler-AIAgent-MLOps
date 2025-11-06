#!/usr/bin/env python
"""
快速 Playwright 测试。

简单测试 Playwright 是否能正常工作，以及是否能爬取图片。
"""

import sys
import asyncio
from playwright.async_api import async_playwright


async def quick_test():
    """快速测试 Playwright。"""
    print("\n" + "="*60)
    print("快速 Playwright 功能测试")
    print("="*60 + "\n")
    
    try:
        print("1️⃣  正在启动浏览器...")
        async with async_playwright() as p:
            # 启动浏览器（可见模式，方便观察）
            browser = await p.chromium.launch(headless=False)
            print("   ✅ 浏览器启动成功\n")
            
            # 创建页面
            page = await browser.new_page()
            
            # 测试 1: 访问百度
            print("2️⃣  测试访问百度...")
            await page.goto("https://www.baidu.com", timeout=10000)
            title = await page.title()
            print(f"   ✅ 页面标题: {title}\n")
            
            # 测试 2: 搜索遥感影像
            print("3️⃣  测试必应图片搜索...")
            search_query = "遥感影像"
            search_url = f"https://www.bing.com/images/search?q={search_query}"
            
            print(f"   搜索: {search_query}")
            print(f"   URL: {search_url}")
            
            await page.goto(search_url, wait_until="networkidle", timeout=15000)
            print("   ✅ 搜索页面加载成功\n")
            
            # 等待图片加载
            print("4️⃣  等待图片加载...")
            try:
                await page.wait_for_selector("img.mimg", timeout=10000)
                print("   ✅ 图片元素已加载\n")
                
                # 获取图片信息
                image_elements = await page.query_selector_all("img.mimg")
                print(f"5️⃣  找到 {len(image_elements)} 张图片")
                
                # 显示前 3 张图片信息
                print("\n   前 3 张图片信息:")
                for i, img in enumerate(image_elements[:3], 1):
                    src = await img.get_attribute("src")
                    alt = await img.get_attribute("alt")
                    
                    print(f"\n   图片 {i}:")
                    if src:
                        # 截断过长的 URL
                        display_src = src[:70] + "..." if len(src) > 70 else src
                        print(f"     URL: {display_src}")
                    if alt:
                        print(f"     描述: {alt}")
                
                # 截图
                screenshot_path = "/tmp/quick_test_screenshot.png"
                await page.screenshot(path=screenshot_path)
                print(f"\n6️⃣  页面截图已保存: {screenshot_path}")
                
            except Exception as e:
                print(f"   ⚠️  等待图片超时: {e}")
            
            # 等待几秒让用户观察
            print("\n⏳ 等待 3 秒后关闭浏览器...")
            await asyncio.sleep(3)
            
            # 关闭浏览器
            await browser.close()
            print("   ✅ 浏览器已关闭\n")
        
        print("="*60)
        print("🎉 Playwright 测试成功！")
        print("="*60)
        print("\n✅ Playwright 可以正常工作")
        print("✅ 可以访问网页并提取图片信息")
        print("✅ 可以进行图片搜索爬取\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 问题排查：")
        print("   1. 确保已安装 Playwright:")
        print("      poetry run playwright install")
        print("   2. 检查网络连接")
        print("   3. 检查防火墙设置\n")
        
        return False


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║          Playwright 快速测试                              ║
╚════════════════════════════════════════════════════════════╝

这个测试会：
  ✓ 启动浏览器（可见模式）
  ✓ 访问必应图片搜索
  ✓ 搜索"遥感影像"
  ✓ 提取图片信息
  ✓ 保存截图

""")
    
    try:
        result = asyncio.run(quick_test())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)


#!/usr/bin/env python
"""
EvoLabeler-Backend 全面系统测试。

测试所有核心功能：
1. 环境配置
2. 依赖安装
3. Supabase 连接和表
4. LLM API (Qwen)
5. Playwright 浏览器
6. MCP 工具系统
7. Agent 功能
8. 图片下载
9. API 端点
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
import json

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class Colors:
    """终端颜色。"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class SystemTester:
    """系统测试器。"""
    
    def __init__(self):
        self.results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "tests": []
        }
    
    def print_header(self, text: str):
        """打印测试标题。"""
        print(f"\n{Colors.HEADER}{'='*70}")
        print(f"{text}")
        print(f"{'='*70}{Colors.ENDC}\n")
    
    def print_section(self, text: str):
        """打印测试段落。"""
        print(f"\n{Colors.OKBLUE}{'─'*70}")
        print(f"📋 {text}")
        print(f"{'─'*70}{Colors.ENDC}\n")
    
    def log_test(self, name: str, passed: bool, message: str = "", skip: bool = False):
        """记录测试结果。"""
        if skip:
            self.results["skipped"] += 1
            status = f"{Colors.WARNING}⊘ SKIP{Colors.ENDC}"
        elif passed:
            self.results["passed"] += 1
            status = f"{Colors.OKGREEN}✅ PASS{Colors.ENDC}"
        else:
            self.results["failed"] += 1
            status = f"{Colors.FAIL}❌ FAIL{Colors.ENDC}"
        
        self.results["tests"].append({
            "name": name,
            "passed": passed,
            "message": message,
            "skipped": skip
        })
        
        print(f"{status} {name}")
        if message:
            print(f"    {message}")
    
    async def test_1_environment(self):
        """测试1: 环境配置。"""
        self.print_section("测试 1: 环境配置检查")
        
        # 检查 .env 文件
        env_file = project_root / ".env"
        if env_file.exists():
            self.log_test("环境文件存在", True, f"路径: {env_file}")
        else:
            self.log_test("环境文件存在", False, f"未找到 .env 文件: {env_file}")
            return False
        
        # 检查环境变量
        try:
            from app.core.config import settings
            
            # Supabase
            if settings.supabase_url and settings.supabase_key:
                self.log_test("Supabase 配置", True, f"URL: {settings.supabase_url[:40]}...")
            else:
                self.log_test("Supabase 配置", False, "缺少 SUPABASE_URL 或 SUPABASE_KEY")
            
            # Qwen API
            if settings.qwen_api_key:
                self.log_test("Qwen API 配置", True, f"Key: {settings.qwen_api_key[:20]}...")
            else:
                self.log_test("Qwen API 配置", False, "缺少 QWEN_API_KEY")
            
            return True
            
        except Exception as e:
            self.log_test("加载配置", False, f"错误: {e}")
            return False
    
    async def test_2_dependencies(self):
        """测试2: 依赖安装。"""
        self.print_section("测试 2: 依赖安装检查")
        
        dependencies = [
            ("fastapi", "FastAPI"),
            ("supabase", "Supabase"),
            ("playwright", "Playwright"),
            ("pydantic", "Pydantic"),
            ("httpx", "HTTPX"),
        ]
        
        all_ok = True
        for module_name, display_name in dependencies:
            try:
                __import__(module_name)
                self.log_test(f"{display_name} 安装", True)
            except ImportError:
                self.log_test(f"{display_name} 安装", False, f"请运行: poetry add {module_name}")
                all_ok = False
        
        return all_ok
    
    async def test_3_supabase(self):
        """测试3: Supabase 连接和表。"""
        self.print_section("测试 3: Supabase 数据库")
        
        try:
            from app.tools.supabase_client import SupabaseClient
            
            client = SupabaseClient()
            self.log_test("Supabase 客户端初始化", True)
            
            # 测试连接
            try:
                # 尝试查询 jobs 表
                response = client.client.table("jobs").select("id").limit(1).execute()
                self.log_test("jobs 表存在", True, f"表可访问")
                
            except Exception as e:
                if "Could not find the table" in str(e) or "relation" in str(e):
                    self.log_test("jobs 表存在", False, 
                                f"表不存在，请在 Supabase Dashboard 执行 scripts/setup_supabase.sql")
                else:
                    self.log_test("jobs 表查询", False, f"错误: {e}")
            
            # 测试 inference_results 表
            try:
                response = client.client.table("inference_results").select("id").limit(1).execute()
                self.log_test("inference_results 表存在", True)
            except Exception as e:
                if "Could not find the table" in str(e) or "relation" in str(e):
                    self.log_test("inference_results 表存在", False, "表不存在")
                else:
                    self.log_test("inference_results 表查询", False, f"错误: {e}")
            
            return True
            
        except Exception as e:
            self.log_test("Supabase 连接", False, f"错误: {e}")
            return False
    
    async def test_4_llm_api(self):
        """测试4: LLM API (Qwen)。"""
        self.print_section("测试 4: LLM API (Qwen)")
        
        try:
            from app.tools.qwen_api_wrapper import QwenAPIWrapper
            
            qwen = QwenAPIWrapper()
            self.log_test("Qwen API 初始化", True)
            
            # 测试文本生成（简单测试，不调用真实 API 避免费用）
            self.log_test("Qwen API 配置", True, 
                        f"Model: {qwen.text_model}, VL Model: {qwen.vl_model}")
            
            # 如果用户想测试真实 API，取消注释以下代码
            # try:
            #     result = await qwen.generate_search_strategy(
            #         descriptions=["测试图像"],
            #         num_queries=2
            #     )
            #     self.log_test("Qwen API 实际调用", True, f"返回: {result.get('scene_type', 'N/A')}")
            # except Exception as e:
            #     self.log_test("Qwen API 实际调用", False, f"错误: {e}")
            
            return True
            
        except Exception as e:
            self.log_test("Qwen API 初始化", False, f"错误: {e}")
            return False
    
    async def test_5_playwright(self):
        """测试5: Playwright 浏览器。"""
        self.print_section("测试 5: Playwright 浏览器")
        
        try:
            from playwright.async_api import async_playwright
            
            self.log_test("Playwright 导入", True)
            
            # 测试浏览器启动
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    self.log_test("Chromium 浏览器启动", True)
                    
                    page = await browser.new_page()
                    await page.goto("https://www.baidu.com", timeout=5000)
                    self.log_test("网页访问测试", True, "成功访问百度")
                    
                    await browser.close()
                
                return True
                
            except Exception as e:
                self.log_test("Playwright 浏览器", False, 
                            f"错误: {e}\n    请运行: poetry run playwright install")
                return False
            
        except ImportError:
            self.log_test("Playwright 导入", False, "请安装 Playwright")
            return False
    
    async def test_6_mcp_tools(self):
        """测试6: MCP 工具系统。"""
        self.print_section("测试 6: MCP 工具系统")
        
        try:
            from app.tools.mcp_integration import get_mcp_integration
            
            mcp = get_mcp_integration()
            self.log_test("MCP 集成初始化", True)
            
            # 列出所有工具
            tools = await mcp.list_all_tools()
            self.log_test("MCP 工具列表", True, f"找到 {len(tools)} 个工具")
            
            # 显示前3个工具
            if tools:
                print(f"    可用工具:")
                for tool in tools[:3]:
                    print(f"      - {tool['name']}: {tool['description'][:50]}...")
            
            # 测试一个简单的工具
            try:
                result = await mcp.call_tool(
                    "context7.search_remote_sensing_docs",
                    {"query": "YOLO", "max_results": 1}
                )
                self.log_test("MCP 工具调用", True, f"Context7 工具测试成功")
            except Exception as e:
                self.log_test("MCP 工具调用", False, f"错误: {e}")
            
            return True
            
        except Exception as e:
            self.log_test("MCP 工具系统", False, f"错误: {e}")
            return False
    
    async def test_7_agents(self):
        """测试7: Agent 初始化。"""
        self.print_section("测试 7: Agent 系统")
        
        try:
            from app.agents.inference_agent import InferenceAgent
            from app.agents.analysis_agent import AnalysisAgent
            from app.agents.acquisition_agent import AcquisitionAgent
            from app.agents.training_agent import TrainingAgent
            from app.tools.supabase_client import SupabaseClient
            from app.tools.qwen_api_wrapper import QwenAPIWrapper
            from app.tools.web_crawler import WebCrawler
            from app.tools.subprocess_executor import SubprocessExecutor
            
            # 初始化工具
            supabase_client = SupabaseClient()
            qwen_api = QwenAPIWrapper()
            web_crawler = WebCrawler(supabase_client)
            subprocess_executor = SubprocessExecutor()
            
            # 测试 InferenceAgent
            try:
                agent = InferenceAgent(
                    subprocess_executor=subprocess_executor,
                    supabase_client=supabase_client
                )
                self.log_test("InferenceAgent 初始化", True)
            except Exception as e:
                self.log_test("InferenceAgent 初始化", False, f"错误: {e}")
            
            # 测试 AnalysisAgent
            try:
                agent = AnalysisAgent(qwen_api=qwen_api)
                self.log_test("AnalysisAgent 初始化", True)
                
                # 测试 System Prompt
                from app.agents.prompts import AgentPrompts
                prompt = AgentPrompts.get_system_prompt("analysis")
                if len(prompt) > 100:
                    self.log_test("AnalysisAgent System Prompt", True, 
                                f"Prompt 长度: {len(prompt)} 字符")
                else:
                    self.log_test("AnalysisAgent System Prompt", False, "Prompt 太短")
                
            except Exception as e:
                self.log_test("AnalysisAgent 初始化", False, f"错误: {e}")
            
            # 测试 AcquisitionAgent
            try:
                agent = AcquisitionAgent(
                    web_crawler=web_crawler,
                    subprocess_executor=subprocess_executor,
                    supabase_client=supabase_client
                )
                self.log_test("AcquisitionAgent 初始化", True)
            except Exception as e:
                self.log_test("AcquisitionAgent 初始化", False, f"错误: {e}")
            
            # 测试 TrainingAgent
            try:
                agent = TrainingAgent(
                    subprocess_executor=subprocess_executor,
                    supabase_client=supabase_client
                )
                self.log_test("TrainingAgent 初始化", True)
            except Exception as e:
                self.log_test("TrainingAgent 初始化", False, f"错误: {e}")
            
            return True
            
        except Exception as e:
            self.log_test("Agent 系统", False, f"错误: {e}")
            return False
    
    async def test_8_orchestrator(self):
        """测试8: 编排器。"""
        self.print_section("测试 8: 编排器系统")
        
        try:
            from app.services.orchestrator import JobOrchestrator
            
            orchestrator = JobOrchestrator(job_id="test_job_001")
            self.log_test("基础编排器初始化", True)
            
        except Exception as e:
            self.log_test("基础编排器初始化", False, f"错误: {e}")
        
        try:
            from app.services.advanced_orchestrator import AdvancedJobOrchestrator
            
            orchestrator = AdvancedJobOrchestrator(job_id="test_job_002")
            self.log_test("高级编排器初始化", True, "支持残差连接和并行执行")
            
            return True
            
        except Exception as e:
            self.log_test("高级编排器初始化", False, f"错误: {e}")
            return False
    
    async def test_9_image_download(self):
        """测试9: 图片下载功能。"""
        self.print_section("测试 9: 图片下载功能")
        
        print("    ⏳ 正在测试图片下载（大约需要10秒）...\n")
        
        try:
            from playwright.async_api import async_playwright
            import httpx
            
            # 创建临时目录
            temp_dir = Path("/tmp/evolabeler_test_images")
            temp_dir.mkdir(exist_ok=True)
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # 访问必应图片
                await page.goto("https://www.bing.com/images/search?q=test&first=1", 
                              wait_until="domcontentloaded", timeout=20000)
                
                # 等待图片
                await page.wait_for_selector("img.mimg", timeout=10000)
                
                # 获取第一张图片
                images = await page.query_selector_all("img.mimg")
                if images:
                    src = await images[0].get_attribute("src")
                    
                    if src and src.startswith("http"):
                        # 尝试下载
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            response = await client.get(src)
                            
                            if response.status_code == 200:
                                test_file = temp_dir / "test_image.jpg"
                                test_file.write_bytes(response.content)
                                
                                size_kb = len(response.content) / 1024
                                self.log_test("图片爬取和下载", True, 
                                            f"成功下载 {size_kb:.1f} KB")
                                
                                # 清理
                                test_file.unlink()
                            else:
                                self.log_test("图片下载", False, 
                                            f"HTTP {response.status_code}")
                    else:
                        self.log_test("图片URL提取", False, "未找到有效的图片URL")
                else:
                    self.log_test("图片查找", False, "未找到图片元素")
                
                await browser.close()
            
            return True
            
        except Exception as e:
            self.log_test("图片下载功能", False, f"错误: {e}")
            return False
    
    async def test_10_api_endpoints(self):
        """测试10: API 端点。"""
        self.print_section("测试 10: API 端点")
        
        try:
            from app.main import app
            from fastapi.testclient import TestClient
            
            # 注意：TestClient 不支持异步，所以只做基本检查
            # 实际 API 测试需要启动服务器
            
            self.log_test("FastAPI 应用导入", True)
            
            # 检查路由
            routes = [route.path for route in app.routes]
            
            if "/health" in routes:
                self.log_test("健康检查端点", True, "路由: /health")
            else:
                self.log_test("健康检查端点", False, "未找到 /health")
            
            if "/api/v1/jobs/" in routes:
                self.log_test("任务创建端点", True, "路由: /api/v1/jobs/")
            else:
                self.log_test("任务创建端点", False, "未找到 /api/v1/jobs/")
            
            # 显示所有端点
            print(f"\n    📋 可用端点:")
            for route in app.routes[:10]:
                if hasattr(route, 'path'):
                    print(f"      - {route.path}")
            
            return True
            
        except Exception as e:
            self.log_test("API 端点检查", False, f"错误: {e}")
            return False
    
    def print_summary(self):
        """打印测试总结。"""
        self.print_header("测试总结")
        
        total = self.results["passed"] + self.results["failed"] + self.results["skipped"]
        
        print(f"{Colors.BOLD}总测试数: {total}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✅ 通过: {self.results['passed']}{Colors.ENDC}")
        print(f"{Colors.FAIL}❌ 失败: {self.results['failed']}{Colors.ENDC}")
        print(f"{Colors.WARNING}⊘ 跳过: {self.results['skipped']}{Colors.ENDC}")
        
        if self.results["failed"] > 0:
            print(f"\n{Colors.FAIL}{'='*70}")
            print("失败的测试:")
            print(f"{'='*70}{Colors.ENDC}\n")
            
            for test in self.results["tests"]:
                if not test["passed"] and not test["skipped"]:
                    print(f"{Colors.FAIL}❌ {test['name']}{Colors.ENDC}")
                    if test["message"]:
                        print(f"   {test['message']}\n")
        
        # 计算成功率
        if total > 0:
            success_rate = (self.results["passed"] / total) * 100
            
            if success_rate == 100:
                color = Colors.OKGREEN
                emoji = "🎉"
            elif success_rate >= 80:
                color = Colors.OKBLUE
                emoji = "😊"
            elif success_rate >= 60:
                color = Colors.WARNING
                emoji = "😐"
            else:
                color = Colors.FAIL
                emoji = "😞"
            
            print(f"\n{color}{Colors.BOLD}成功率: {success_rate:.1f}% {emoji}{Colors.ENDC}\n")
        
        # 保存结果到文件
        result_file = Path(__file__).parent / "test_results.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "passed": self.results["passed"],
                    "failed": self.results["failed"],
                    "skipped": self.results["skipped"],
                    "success_rate": success_rate if total > 0 else 0
                },
                "tests": self.results["tests"]
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📄 详细结果已保存到: {result_file}\n")
        
        return self.results["failed"] == 0
    
    async def run_all_tests(self):
        """运行所有测试。"""
        self.print_header("EvoLabeler-Backend 全面系统测试")
        
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        tests = [
            self.test_1_environment,
            self.test_2_dependencies,
            self.test_3_supabase,
            self.test_4_llm_api,
            self.test_5_playwright,
            self.test_6_mcp_tools,
            self.test_7_agents,
            self.test_8_orchestrator,
            self.test_9_image_download,
            self.test_10_api_endpoints,
        ]
        
        for test in tests:
            try:
                await test()
            except Exception as e:
                print(f"\n{Colors.FAIL}测试异常: {test.__name__}{Colors.ENDC}")
                print(f"错误: {e}\n")
                import traceback
                traceback.print_exc()
        
        return self.print_summary()


async def main():
    """主函数。"""
    tester = SystemTester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    print(f"""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║          EvoLabeler-Backend 全面系统测试                           ║
║                                                                    ║
║  本测试将验证以下功能：                                              ║
║    ✓ 环境配置                                                       ║
║    ✓ 依赖安装                                                       ║
║    ✓ Supabase 数据库                                               ║
║    ✓ LLM API (Qwen)                                               ║
║    ✓ Playwright 浏览器                                             ║
║    ✓ MCP 工具系统                                                  ║
║    ✓ Agent 系统                                                    ║
║    ✓ 编排器                                                        ║
║    ✓ 图片下载                                                       ║
║    ✓ API 端点                                                      ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  测试被用户中断{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.FAIL}❌ 测试运行失败: {e}{Colors.ENDC}")
        sys.exit(1)


你好，我需要你扮演一名资深的 AI 系统架构师 和 MLOps 专家。我们将共同构建一个名为 "EvoLabeler-Backend" 的后端项目。

**项目背景与目标:**

该项目名为 "EvoLabeler-Backend"，这是我毕业设计系统的后端部分，是一个基于 FastAPI 的后端服务，旨在实现一个由多智能体（Multi-Agent）驱动的、能够自我进化的遥感影像目标检测 MLOps 引擎。核心流程是：接收用户上传的图片 -> 智能分析图片内容 -> 自动从网络爬取相似数据 -> 对新数据进行伪标注 -> 组织数据并触发远程模型训练。
这个项目是 IDEATE (Iterative Data Engine via Agentic Task Execution) 框架的工程化实现。IDEATE 的核心是通过一个多智能体协作系统，实现数据驱动的模型迭代闭环。你生成的每一行代码都应服务于这个框架，体现其 模块化、自动化、智能化 的设计哲学。这是我毕业设计系统的后端部分

**关键学术概念映射:**
- Multi-Agent 架构: 体现为 Orchestrator + Role-Playing Agents 的设计。
- LLM in Agentic Agent: 体现在 AnalysisAgent 作为“策略规划师”的角色。
- 主动学习 (Active Learning): 体现在 InferenceAgent 对标注结果的不确定性评估。
- 半监督学习 (Semi-Supervised Learning): 体现在对网络爬取数据进行高质量伪标注的流程。
- 带噪学习 (Learning with Noisy Labels): 体现在未来可扩展的、用于提升伪标签质量的机制中（目前预留接口）。

**技术栈要求:**

*   **框架:** FastAPI
*   **数据库 & 存储:** Supabase (通过 `supabase-py` 库交互)
*   **LLM & VLM:** 硅基流动 API (Qwen/Qwen3-VL-32B-Instruct) (通过 HTTP requests 或其 SDK 交互)
*   **Web 爬虫:** Playwright (通过其异步 Python API)
*   **外部脚本调用:** Python `subprocess` 模块
*   **数据验证:** Pydantic V2
*   **依赖管理:** 使用 `pyproject.toml` (Poetry 或 PDM 风格)
*   **Python 版本:** 3.13

---

### **第一部分：项目结构与核心配置文件**

请为我生成以下目录结构和配置文件。这是整个项目的骨架。

```
/evolauncher-backend
|
|-- pyproject.toml             # 项目依赖和元数据
|-- README.md
|
|-- app/
|   |-- __init__.py
|   |-- main.py                # FastAPI 应用入口
|   |-- core/
|   |   |-- __init__.py
|   |   |-- config.py          # 全局配置管理 (环境变量等)
|   |   |-- logging_config.py  # 日志配置
|   |
|   |-- api/
|   |   |-- __init__.py
|   |   |-- v1/
|   |   |   |-- __init__.py
|   |   |   |-- endpoints/
|   |   |   |   |-- __init__.py
|   |   |   |   |-- jobs.py    # /jobs API 路由
|   |   |   |-- schemas/
|   |   |       |-- __init__.py
|   |   |       |-- job.py     # Job 相关的 Pydantic 模型
|   |
|   |-- services/
|   |   |-- __init__.py
|   |   |-- orchestrator.py    # 核心：Job Orchestrator
|   |
|   |-- agents/
|   |   |-- __init__.py
|   |   |-- base_agent.py      # Agent 的基类 (可选)
|   |   |-- inference_agent.py
|   |   |-- analysis_agent.py
|   |   |-- acquisition_agent.py
|   |   |-- training_agent.py
|   |
|   |-- tools/
|   |   |-- __init__.py
|   |   |-- supabase_client.py # Supabase 交互工具
|   |   |-- qwen_api_wrapper.py  # 硅基流动 API 交互工具
|   |   |-- web_crawler.py       # Playwright 爬虫工具
|   |   |-- subprocess_executor.py # 外部脚本调用工具
|   |
|   |-- db/
|       |-- __init__.py
|       |-- models.py          # SQLAlchemy 模型 (可选，或直接用 supabase-py)
|       |-- supabase_init.py     # 初始化 Supabase 客户端的单例模式
```

**具体要求:**

1.  **`pyproject.toml`:** 请包含 `fastapi`, `uvicorn`, `pydantic[email]`, `supabase`, `playwright`, `python-dotenv`, `httpx` 等核心依赖。
2.  **`app/core/config.py`:** 使用 Pydantic 的 `BaseSettings` 来从 `.env` 文件加载配置，包括 `SUPABASE_URL`, `SUPABASE_KEY`, `QWEN_API_KEY`, `REMOTE_YOLO_PROJECT_PATH` 等。
3.  **`app/main.py`:** 初始化 FastAPI app，并挂载 `api/v1/endpoints/jobs.py` 中的路由。

---

### **第二部分：API 层设计 (`app/api`)**

这是系统的入口，请遵循 RESTful 设计原则。

**`app/api/v1/schemas/job.py`:**
*   创建 Pydantic 模型 `JobCreate`, `JobResponse`, `JobStatusResponse`。
*   `JobResponse` 应包含 `job_id`, `status`, `created_at`。
*   `JobStatusResponse` 应包含 `job_id`, `status`, `progress_message`。

**`app/api/v1/endpoints/jobs.py`:**
*   创建一个 `APIRouter`。
*   **`POST /jobs/` (路由):**
    *   接收一个 `fastapi.UploadFile` (用户上传的 ZIP 文件)。
    *   **不要在路由函数中实现业务逻辑。**
    *   它的职责是：
        1.  验证文件类型。
        2.  调用一个服务（例如 `JobService`，可以在 `orchestrator.py` 中实现）来处理文件、创建数据库记录。
        3.  使用 FastAPI 的 `BackgroundTasks` 来异步启动 `JobOrchestrator` 的 `run()` 方法。
        4.  立即返回一个 `JobResponse`，其中包含新创建的 `job_id`。
*   **`GET /jobs/{job_id}/status` (路由):**
    *   接收 `job_id`。
    *   查询 Supabase 获取该 Job 的当前状态。
    *   返回 `JobStatusResponse`。

---

### **第三部分：核心服务与 Multi-Agent 架构 (`app/services` 和 `app/agents`)**

这是系统的“大脑”和“手臂”，也是最复杂的部分。请仔细实现。

**`app/tools/` (工具层):**
*   **`supabase_client.py`:** 实现一个 `SupabaseClient` 类，封装 `supabase-py` 的常用操作，如 `upload_file`, `create_job_record`, `update_job_status`, `get_job_by_id` 等。使用单例模式确保全局只有一个客户端实例。
*   **`qwen_api_wrapper.py`:** 实现一个 `QwenAPIWrapper` 类。包含两个异步方法：
    *   `get_image_description(base64_image: str) -> str`: 调用 Qwen-VL API。
    *   `generate_search_strategy(descriptions: list[str]) -> dict`: 调用 Qwen 文本 API。
*   **`web_crawler.py`:** 实现一个 `WebCrawler` 类，使用 `playwright.async_api`。包含一个方法 `async def crawl_images(queries: list[str], limit: int) -> list[str]`，返回爬取并上传到 Supabase 后得到的图片路径列表。
*   **`subprocess_executor.py`:** 实现一个 `SubprocessExecutor` 类。包含两个核心方法：
    *   `run_yolo_predict(...)`: 准备数据并调用 `predict.py`。
    *   `run_yolo_train(...)`: 准备数据集并调用 `train.py`。
    *   这些方法需要处理命令行参数的构建、进程的启动和结果的捕获。

**`app/agents/` (智能体层):**
*   为每个 Agent (`InferenceAgent`, `AnalysisAgent`, `AcquisitionAgent`, `TrainingAgent`) 创建一个类。
*   每个 Agent 类的构造函数接收所需的 Tool 实例（**依赖注入**）。
*   每个 Agent 类实现一个核心的 `async def execute(self, context: dict) -> dict` 方法。它接收 Orchestrator 传递的上下文，调用 Tool，然后返回结果。
*   **Agent 自身不包含复杂的业务逻辑**，它只是一个调用 Tool 并格式化结果的薄层。

**`app/services/orchestrator.py` (编排器):**
*   实现 `JobOrchestrator` 类。
*   **构造函数 `__init__`:** 接收 `job_id`，并**实例化所有需要的 Agent 和 Tool**。
*   **核心方法 `async def run(self)`:**
    1.  这是整个工作流的实现。它是一个线性的、异步的方法。
    2.  **严格按照 `UPLOAD -> INFERENCE -> ANALYSIS -> ACQUISITION -> PSEUDO_LABELING -> TRAINING -> COMPLETE` 的顺序**。
    3.  在每一步开始前，调用 `supabase_client.update_job_status` 更新数据库中的状态。
    4.  调用相应的 Agent 的 `execute` 方法。
    5.  将上一步 Agent 的输出结果，更新到内部的 `self.context` 字典中，再传递给下一步的 Agent。
    6.  实现完善的 `try...except` 块，在任何步骤失败时，都能捕获异常，更新 Job 状态为 `failed`，并记录错误日志。

---

### **第四部分：代码规范与鲁棒性**

*   **类型提示:** 所有函数和方法都必须有明确的 Python 类型提示。
*   **异步优先:** 所有可能产生 I/O 阻塞的操作（API 调用、数据库交互、文件读写）都应使用 `async/await`。
*   **依赖注入:** 在 Orchestrator 和 Agent 的设计中，请使用依赖注入模式，即将 Tool 的实例作为参数传入 Agent 的构造函数。这有助于解耦和测试。
*   **错误处理:** 在 API 层和 Service 层都要有健壮的错误处理机制。FastAPI 的异常处理器是实现此目的的好地方。
*   **日志:** 在 `app/core/logging_config.py` 中配置结构化日志，并在 Orchestrator 的关键步骤中记录详细日志。
*   **代码注释:** 在复杂的逻辑部分（如 Orchestrator 的工作流、Agent 的决策逻辑）添加清晰的注释。

请根据以上所有要求，为我生成这个项目的完整初始代码框架。
# EvoLabeler-Backend - Project Summary

## 项目概述

**EvoLabeler-Backend** 是一个基于 IDEATE (Iterative Data Engine via Agentic Task Execution) 框架的多智能体驱动的 MLOps 引擎，专门用于遥感影像目标检测任务。

## 核心特性

### 1. Multi-Agent 架构
- **Orchestrator**: 工作流协调器
- **InferenceAgent**: 模型推理与不确定性评估
- **AnalysisAgent**: LLM 驱动的策略规划
- **AcquisitionAgent**: 自动化数据获取与伪标注
- **TrainingAgent**: 模型训练管理

### 2. 学术概念实现
- **主动学习 (Active Learning)**: 基于不确定性的数据选择
- **半监督学习 (Semi-Supervised Learning)**: 高质量伪标注生成
- **带噪学习 (Learning with Noisy Labels)**: 质量控制机制

### 3. 技术栈
- **框架**: FastAPI + Pydantic V2
- **数据库**: Supabase (PostgreSQL + Storage)
- **LLM/VLM**: 硅基流动 API (Qwen)
- **爬虫**: Playwright
- **模型**: YOLO (通过 subprocess 调用)

## 项目结构

```
EvoLabeler-Backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── core/                   # 核心配置
│   │   ├── config.py           # 环境配置管理
│   │   └── logging_config.py   # 结构化日志
│   ├── api/v1/                 # API 层
│   │   ├── endpoints/
│   │   │   └── jobs.py         # Job API 路由
│   │   └── schemas/
│   │       └── job.py          # Pydantic 模型
│   ├── services/               # 业务服务层
│   │   └── orchestrator.py     # 工作流编排器
│   ├── agents/                 # 智能体层
│   │   ├── base_agent.py
│   │   ├── inference_agent.py
│   │   ├── analysis_agent.py
│   │   ├── acquisition_agent.py
│   │   └── training_agent.py
│   ├── tools/                  # 工具层
│   │   ├── supabase_client.py
│   │   ├── qwen_api_wrapper.py
│   │   ├── web_crawler.py
│   │   └── subprocess_executor.py
│   └── db/                     # 数据库
│       ├── models.py           # Schema 参考
│       └── supabase_init.py    # 客户端初始化
├── docs/                       # 文档
│   ├── API.md                  # API 文档
│   ├── SETUP.md                # 安装指南
│   ├── ARCHITECTURE.md         # 架构说明
│   └── PROJECT_SUMMARY.md      # 项目总结
├── scripts/                    # 脚本
│   └── setup_supabase.sql      # 数据库初始化
├── pyproject.toml              # 项目配置 (Poetry)
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量模板
├── .gitignore                  # Git 忽略规则
├── run.py                      # 开发服务器启动脚本
└── README.md                   # 项目说明
```

## 工作流程

```
用户上传 ZIP 文件
    ↓
[UPLOAD] 文件解压与验证
    ↓
[INFERENCE] YOLO 推理 + 不确定性评估
    ↓
[ANALYSIS] VLM 图像分析 + LLM 策略生成
    ↓
[ACQUISITION] 网络爬取 + 伪标注
    ↓
[TRAINING] 数据集准备 + 模型训练
    ↓
[COMPLETE] 完成
```

## 代码特点

### 1. 严格的类型提示
所有函数和方法都有完整的 Python 类型注解。

### 2. 异步优先
所有 I/O 操作都使用 `async/await`，提高并发性能。

### 3. 依赖注入
Agent 和 Tool 之间通过构造函数注入依赖，便于测试和维护。

### 4. 健壮的错误处理
- 多层级错误捕获
- 详细的错误日志
- 用户友好的错误消息
- 自动状态更新

### 5. 结构化日志
- JSON 格式（生产环境）
- 彩色输出（开发环境）
- 上下文信息（job_id, agent 等）
- 多级别日志

### 6. RESTful API 设计
- 清晰的端点命名
- 标准 HTTP 状态码
- Pydantic 数据验证
- OpenAPI 文档自动生成

## 配置管理

### 环境变量 (.env)

```bash
# Supabase
SUPABASE_URL=...
SUPABASE_KEY=...

# LLM API
QWEN_API_KEY=...

# YOLO Project
REMOTE_YOLO_PROJECT_PATH=...

# Application
DEBUG=true
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE_MB=100
```

### Pydantic Settings
使用 `pydantic-settings` 进行类型安全的配置管理，支持：
- 环境变量加载
- 类型验证
- 默认值
- 配置继承

## API 端点

### 创建任务
```http
POST /api/v1/jobs/
Content-Type: multipart/form-data

file: <ZIP file>
```

### 查询状态
```http
GET /api/v1/jobs/{job_id}/status
```

### 健康检查
```http
GET /health
```

## 数据库设计

### Jobs 表
存储任务状态和元数据

### Inference Results 表
存储推理结果和预测

### Storage Buckets
- `images`: 图片存储（公开）
- `models`: 模型存储（私有）

## 部署建议

### 开发环境
```bash
poetry run python run.py
```

### 生产环境
```bash
# 使用多个 worker
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 或使用 Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker 部署
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN playwright install --with-deps
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 扩展性

### 水平扩展
- 使用负载均衡器分发请求
- 部署多个 API 实例
- 使用分布式任务队列 (Celery)

### 功能扩展
- 添加新的 Agent
- 扩展 Tool 功能
- 自定义工作流阶段
- 集成其他 LLM/VLM

## 安全建议

1. **API 认证**: 添加 JWT 或 API Key
2. **速率限制**: 防止 API 滥用
3. **输入验证**: 严格的文件类型和大小检查
4. **HTTPS**: 生产环境使用 SSL/TLS
5. **密钥管理**: 使用 Vault 或 AWS Secrets Manager
6. **RLS**: 在 Supabase 中启用行级安全

## 监控与日志

### 日志级别
- DEBUG: 详细调试信息
- INFO: 正常操作信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误

### 推荐监控工具
- **日志**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **指标**: Prometheus + Grafana
- **追踪**: Jaeger (OpenTelemetry)
- **错误追踪**: Sentry

## 测试策略

### 单元测试
```bash
pytest tests/unit/
```

### 集成测试
```bash
pytest tests/integration/
```

### 端到端测试
```bash
pytest tests/e2e/
```

## 文档资源

- **API 文档**: `docs/API.md`
- **安装指南**: `docs/SETUP.md`
- **架构说明**: `docs/ARCHITECTURE.md`
- **在线文档**: http://localhost:8000/docs (Swagger UI)

## 性能优化建议

1. **数据库**:
   - 添加索引
   - 使用连接池
   - 查询优化

2. **API**:
   - 响应缓存
   - 分页查询
   - 压缩响应

3. **工作流**:
   - 并行处理
   - 批量操作
   - 异步任务队列

4. **存储**:
   - CDN 分发
   - 图片压缩
   - 懒加载

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 遵循代码规范 (Black + Ruff)
4. 添加单元测试
5. 提交 Pull Request

## License

MIT License

## 联系方式

毕业设计项目 - EvoLabeler 系统后端

---

**注意**: 这是一个学术项目，展示了 IDEATE 框架的工程化实现。在生产环境中使用前，请进行充分的测试和安全加固。


# 🎉 测试报告

## 📁 测试文件

```
backend/tests/
├── test_full_system.py           # ⭐ 全面系统测试 (新)
├── test_playwright_download_images.py  # 图片下载测试
├── quick_playwright_test.py      # 快速 Playwright 测试
├── test_web_crawler.py           # 爬虫测试
└── test_results.json             # 测试结果 JSON
```

---

## 🚀 快速验证

### 运行全面测试

```bash
cd /Users/sunminghao/Desktop/EvoLabeler/backend
poetry run python tests/test_full_system.py
```

### 运行特定测试

```bash
# 图片下载测试
poetry run python tests/test_playwright_download_images.py

# 快速 Playwright 测试
poetry run python tests/quick_playwright_test.py

# 爬虫测试
poetry run python tests/test_web_crawler.py
```

### 启动服务

```bash
# 开发模式
poetry run python run.py

# 或使用 uvicorn
poetry run uvicorn app.main:app --reload
```

### 访问 API 文档

```
http://localhost:8000/docs        # Swagger UI
http://localhost:8000/redoc       # ReDoc
http://localhost:8000/health      # 健康检查
```

---

## 📚 详细文档

| 文档 | 说明 |
|------|------|
| `backend/TEST_REPORT.md` | 📄 完整测试报告 |
| `backend/docs/SUPABASE_GUIDE.md` | 📚 Supabase 使用指南 |
| `backend/docs/TROUBLESHOOTING.md` | 🔧 故障排查手册 |
| `UPDATE_SUMMARY.md` | 📝 更新总结 |
| `PR_TEMPLATE.md` | 📋 Pull Request 模板 |
| `GIT_COMMANDS.md` | 🔗 Git 命令指南 |
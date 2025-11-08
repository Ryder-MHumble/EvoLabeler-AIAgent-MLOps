# 故障排查指南

## 问题：ModuleNotFoundError: No module named 'supabase'

### 原因

依赖包尚未安装，或者虚拟环境未激活。

### 解决方案

#### 方法1：使用 Poetry 安装依赖（推荐）

```bash
cd /Users/sunminghao/Desktop/EvoLabeler/backend

# 安装所有依赖
poetry install

# 安装 Playwright 浏览器
poetry run playwright install

# 验证安装
poetry run python -c "import supabase; print('✅ Supabase 已安装')"
```

#### 方法2：使用 pip 安装（备选）

```bash
cd /Users/sunminghao/Desktop/EvoLabeler/backend

# 激活虚拟环境（如果有）
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install

# 验证安装
python -c "import supabase; print('✅ Supabase 已安装')"
```

### 验证步骤

运行测试脚本：

```bash
# 测试数据库连接
poetry run python scripts/setup_database.py

# 测试 Playwright
poetry run python tests/quick_playwright_test.py

# 测试图片下载
poetry run python tests/test_playwright_download_images.py
```

---

## 问题：Python 3.13 版本不兼容

### 原因

某些依赖包可能不支持 Python 3.13。

### 解决方案

#### 方法1：降级 Python 版本

```bash
# 安装 Python 3.11 或 3.12
pyenv install 3.12.0
pyenv local 3.12.0

# 重新安装依赖
cd backend
poetry env use 3.12
poetry install
```

#### 方法2：修改 pyproject.toml

编辑 `pyproject.toml`:

```toml
[tool.poetry.dependencies]
python = "^3.11"  # 改为 3.11 或 3.12
```

然后重新安装：

```bash
poetry install
```

---

## 问题：Playwright 浏览器未安装

### 错误信息

```
playwright._impl._api_types.Error: Executable doesn't exist at ...
```

### 解决方案

```bash
# 安装浏览器
poetry run playwright install

# 安装系统依赖（Linux）
poetry run playwright install-deps

# 指定浏览器
poetry run playwright install chromium
```

---

## 问题：Supabase 连接失败

### 错误信息

```
Connection error
Could not reach Supabase
```

### 解决方案

#### 1. 检查 .env 文件

确保 `.env` 文件存在且包含正确的配置：

```bash
# 检查文件
cat backend/.env

# 应该包含：
SUPABASE_URL="https://jzkejgtalihqvomdwjrs.supabase.co"
SUPABASE_KEY="sb_publishable_..."
QWEN_API_KEY="sk-..."
```

#### 2. 验证网络连接

```bash
# 测试连接
curl https://jzkejgtalihqvomdwjrs.supabase.co

# 或使用 Python
poetry run python -c "
import httpx
response = httpx.get('https://jzkejgtalihqvomdwjrs.supabase.co')
print(f'状态码: {response.status_code}')
"
```

#### 3. 检查 API Key

在 Supabase Dashboard 中验证 API Key：

1. 访问 https://app.supabase.com/project/jzkejgtalihqvomdwjrs/settings/api
2. 复制 `anon` `public` key
3. 更新 `.env` 文件

---

## 问题：Poetry 命令找不到

### 错误信息

```
poetry: command not found
```

### 解决方案

#### 安装 Poetry

```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# 添加到 PATH
export PATH="$HOME/.local/bin:$PATH"

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# 验证安装
poetry --version
```

---

## 问题：导入错误 - 找不到 app 模块

### 错误信息

```
ModuleNotFoundError: No module named 'app'
```

### 解决方案

确保从正确的目录运行：

```bash
# 错误：从项目根目录运行
cd /Users/sunminghao/Desktop/EvoLabeler
poetry run python scripts/setup_database.py  # ❌

# 正确：从 backend 目录运行
cd /Users/sunminghao/Desktop/EvoLabeler/backend
poetry run python scripts/setup_database.py  # ✅
```

或者设置 PYTHONPATH：

```bash
export PYTHONPATH="/Users/sunminghao/Desktop/EvoLabeler/backend:$PYTHONPATH"
```

---

## 问题：Git 推送失败

### 错误信息

```
remote: Permission denied
fatal: Authentication failed
```

### 解决方案

#### 1. 检查 Git 凭证

```bash
# 检查远程仓库
git remote -v

# 更新凭证
git config --global user.name "Ryder Sun"
git config --global user.email "mhumble010221@gmail.com"

# 使用 SSH（推荐）
git remote set-url origin git@github.com:Ryder-MHumble/EvoLabeler-AIAgent-MLOps.git
```

#### 2. 生成 SSH Key

```bash
# 生成密钥
ssh-keygen -t ed25519 -C "mhumble010221@gmail.com"

# 添加到 GitHub
cat ~/.ssh/id_ed25519.pub
# 复制输出，添加到 GitHub Settings -> SSH Keys
```

---

## 问题：端口被占用

### 错误信息

```
[ERROR] [Errno 48] error while attempting to bind on address ('0.0.0.0', 8000): address already in use
```

### 解决方案

```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或使用其他端口
poetry run uvicorn app.main:app --port 8001
```

---

## 问题：测试失败

### 常见原因

1. **依赖未安装**
   ```bash
   poetry install
   poetry run playwright install
   ```

2. **环境变量未设置**
   ```bash
   # 检查 .env
   cat backend/.env
   ```

3. **数据库表未创建**
   ```bash
   # 在 Supabase Dashboard 执行 SQL
   # 然后验证
   poetry run python scripts/setup_database.py
   ```

---

## 快速诊断脚本

创建并运行诊断脚本：

```bash
cat > backend/diagnose.py << 'EOF'
#!/usr/bin/env python
"""快速诊断脚本"""
import sys
import subprocess

def check(name, command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ {name}")
            return True
        else:
            print(f"❌ {name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False

print("🔍 系统诊断\n")
check("Python", "python --version")
check("Poetry", "poetry --version")
check("Supabase 包", "python -c 'import supabase'")
check("Playwright", "python -c 'import playwright'")
check("FastAPI", "python -c 'import fastapi'")
check(".env 文件", "test -f .env && echo 'exists'")
print("\n诊断完成！")
EOF

chmod +x backend/diagnose.py
poetry run python backend/diagnose.py
```

---

## 获取帮助

如果问题仍未解决：

1. **查看日志**
   ```bash
   # 应用日志
   tail -f logs/app.log
   
   # Poetry 详细输出
   poetry install -vvv
   ```

2. **提供信息**
   - Python 版本：`python --version`
   - Poetry 版本：`poetry --version`
   - 操作系统：`uname -a` (macOS/Linux)
   - 错误完整堆栈跟踪

3. **社区支持**
   - GitHub Issues
   - 项目文档
   - Stack Overflow

---

## 常用命令速查

```bash
# 安装依赖
poetry install

# 更新依赖
poetry update

# 添加新依赖
poetry add <package-name>

# 运行脚本
poetry run python <script.py>

# 启动服务
poetry run python run.py

# 运行测试
poetry run pytest

# 格式化代码
poetry run black .

# 类型检查
poetry run mypy app/

# 清理缓存
poetry cache clear . --all
poetry install
```

---

<div align="center">

**📧 如需进一步帮助，请联系: mhumble010221@gmail.com**

</div>


# EvoLabeler - AI Agent Driven MLOps Engine

<div align="center">

<img src="evolauncher-frontend/dist/Logo.png" alt="EvoLabeler Logo" width="200"/>

**🚀 Self-Evolving MLOps Engine for Remote Sensing Object Detection Based on Multi-Agent Collaboration**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.13+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.4-brightgreen)](https://vuejs.org/)
[![Electron](https://img.shields.io/badge/Electron-28-blue)](https://www.electronjs.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[English](README_EN.md) | [中文文档](README.md)

</div>

---

## 📖 Introduction

**EvoLabeler** is an innovative MLOps system based on the **IDEATE (Iterative Data Engine via Agentic Task Execution)** framework, implementing fully automated closed-loop remote sensing image object detection through multi-agent collaboration.

### 🎯 Key Features

- **🤖 Multi-Agent Architecture**: 4 specialized agents working collaboratively
- **🔄 Automated Closed-Loop**: Fully automated from data upload to model training
- **🧠 LLM-Driven Decision Making**: Intelligent analysis and strategy planning
- **🌐 Active Learning**: Uncertainty-based data acquisition
- **📊 Semi-Supervised Learning**: High-quality pseudo-label generation
- **🔗 Residual Architecture**: Information preservation and parallel execution
- **📁 Project Management**: Complete project lifecycle management and monitoring
- **🎨 Co-Pilot Workspace**: Data stream management, smart canvas, agent analysis, live terminal
- **💻 Desktop Application**: Electron + Vue 3 modern desktop experience

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (Electron Desktop)                │
│       Vue3 + TypeScript + GSAP + Element Plus               │
│   Project Dashboard | Workspace Monitor | Co-Pilot Workspace│
│   Data Stream | Smart Canvas | Agent Analysis | Live Terminal│
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │       AdvancedJobOrchestrator (Orchestration Layer)     │ │
│ │  Residual Connections | Parallel Execution | Feedback   │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌────────┬──────────┬──────────────┬────────────┐          │
│ │Inference│Analysis │Acquisition   │Training    │  Agents  │
│ │Agent   │Agent    │Agent         │Agent       │          │
│ └────────┴──────────┴──────────────┴────────────┘          │
│ ┌────────┬──────────┬──────────────┬────────────┐          │
│ │Supabase│QwenAPI  │WebCrawler    │Subprocess  │  Tools   │
│ │Client  │Wrapper  │(Playwright)  │Executor    │          │
│ └────────┴──────────┴──────────────┴────────────┘          │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                    MCP Tool Registry                    │ │
│ │  Scene Classification | Keyword Optimization | Quality  │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              External Services / Storage                    │
│   Supabase DB  |  Qwen API  |  YOLO Scripts  |  Storage    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔬 Workflow

### Complete Pipeline

```
User Upload ZIP
    ↓
[UPLOAD] Extract & Validate
    ↓
[INFERENCE] Model Inference (Residual)
    ↓
    ├─ Detection Results
    ├─ Uncertainty Assessment
    └─ Active Learning Signals
    ↓
[ANALYSIS] VLM+LLM Analysis (Residual + Parallel)
    ↓
    ├─ Scene Classification (MCP Tools)
    ├─ Semantic Extraction
    └─ Search Strategy Generation
    ↓
[Conditional Branch] Need More Data?
    ├─ Yes → [ACQUISITION]
    │         ├─ Web Crawling (Playwright)
    │         ├─ Pseudo Labeling (YOLO)
    │         └─ Quality Filtering (MCP Tools)
    │         ↓
    │      [Quality Check] (Feedback Loop)
    │         ├─ Pass → Continue
    │         └─ Fail → Supplement/End
    │
    └─ No → Skip Acquisition
    ↓
[TRAINING] Model Training (Residual)
    ├─ Dataset Preparation
    ├─ Configuration Generation
    └─ Training Monitoring
    ↓
[COMPLETE] Done
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+
- Poetry (Python package manager)
- Supabase Account
- Qwen API Key (SiliconFlow)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Ryder-MHumble/EvoLabeler-AIAgent-MLOps.git
cd EvoLabeler-AIAgent-MLOps

# 2. Install backend dependencies
cd backend
poetry install
poetry run playwright install

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Initialize database
# Run in Supabase SQL Editor: backend/app/db/migrations/002_create_projects_table.sql
poetry run python scripts/insert_test_projects.py

# 5. Start backend service
poetry run python run.py
```

### Start Frontend

#### Development Mode

```bash
# 1. Navigate to frontend directory
cd ../evolauncher-frontend

# 2. Install dependencies
npm install

# 3. Start Electron application
npm run electron:dev
```

#### Build Production Version

**Method 1: One-Click Build (Recommended)**

```bash
cd evolauncher-frontend/scripts
./build-app.sh
```

**Method 2: Manual Build**

```bash
cd evolauncher-frontend

# 1. Generate app icons
cd scripts
./create-icons.sh
cd ..

# 2. Build the application
npm run build:mac
```

**Build Output Location**:
```
evolauncher-frontend/
└── release/
    ├── EvoLabeler-1.0.0-arm64.dmg    # Apple Silicon version
    ├── EvoLabeler-1.0.0.dmg          # Intel version
    └── mac/
        └── EvoLabeler.app
```

**First-Time Run Tips**:

macOS may show a security warning (unsigned app). To resolve:
- Right-click EvoLabeler.app → Select "Open" → Click "Open" button
- Or use command: `xattr -cr /Applications/EvoLabeler.app`

### Access Services

- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Frontend**: Electron window opens automatically

## 🛠️ Tech Stack

### Backend

- **Framework**: FastAPI 0.115
- **Database**: Supabase (PostgreSQL)
- **LLM/VLM**: Qwen API (SiliconFlow)
- **Web Scraping**: Playwright
- **Validation**: Pydantic V2
- **Async**: asyncio

### Frontend

- **Desktop**: Electron 28
- **Framework**: Vue 3.4 (Composition API)
- **Build Tool**: Vite 5.0
- **UI Library**: Element Plus 2.5
- **Animation**: GSAP 3.12
- **Styling**: Tailwind CSS + SCSS
- **State Management**: Pinia 2.1
- **Routing**: Vue Router 4.2
- **i18n**: Vue I18n 9.9

---

## 📖 Documentation

### Backend
- [API Documentation](backend/docs/API.md)
- [Architecture Design](backend/docs/ARCHITECTURE.md)
- [Database Design](backend/app/db/DATABASE_DESIGN.md)
- [Project Management](backend/docs/PROJECT_MANAGEMENT.md)

### Frontend
- [Frontend README](evolauncher-frontend/README.md)
- [Quick Start Guide](evolauncher-frontend/QUICKSTART.md)
- [Co-Pilot Workspace Features](evolauncher-frontend/CO_PILOT_FEATURES.md)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- FastAPI Team
- Supabase Community
- SiliconFlow API
- Playwright Project
- All open-source contributors

---

<div align="center">

**Made with ❤️ by Ryder Sun**

If you find this project helpful, please consider giving it a ⭐!

</div>


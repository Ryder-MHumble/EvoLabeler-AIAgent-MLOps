# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- Multi-agent orchestration system
- Electron desktop frontend
- Project management system
- Residual connection architecture
- MCP tool integration

## [0.2.0] - 2024-12-04

### Added
- Project management REST API
- Supabase projects table
- Project lifecycle tracking
- TypeScript API client
- Test data insertion script
- English README documentation

### Changed
- Updated README with bilingual support
- Improved project structure
- Enhanced documentation

### Fixed
- Electron double window startup issue
- Preload script reload behavior

## [0.1.0] - 2024-11-14

### Added
- Core multi-agent system (4 agents)
- IDEATE workflow implementation
- FastAPI backend with async support
- Vue 3 + Electron frontend
- Supabase database integration
- Playwright web crawler
- Active learning mechanism
- Semi-supervised learning pipeline
- MCP tool registry
- Real-time agent visualization
- Project workspace UI
- Dashboard with GSAP animations

### Backend Features
- InferenceAgent with uncertainty quantification
- AnalysisAgent with VLM integration
- AcquisitionAgent with quality control
- TrainingAgent with adaptive parameters
- AdvancedJobOrchestrator with residual connections
- Parallel task execution support
- Conditional branching logic
- Feedback loop implementation

### Frontend Features
- Modern Electron desktop app
- Vue 3 Composition API
- Element Plus UI components
- GSAP professional animations
- Dark/light theme support
- i18n internationalization
- Project dashboard
- Workspace monitoring
- Agent status visualization

### Infrastructure
- PostgreSQL (Supabase) database
- Qwen LLM/VLM API integration
- Playwright for web scraping
- Poetry dependency management
- Vite build tooling
- TypeScript strict mode

### Documentation
- API documentation
- Architecture design docs
- Database design specs
- Frontend README
- Quick start guide

## [0.0.1] - 2024-10-01

### Added
- Initial project setup
- Basic structure definition
- Development environment configuration

---

## Release Notes

### Version 0.2.0 Highlights

**Project Management System**
- Complete CRUD operations for projects
- Pagination and filtering support
- Project statistics and analytics
- TypeScript type-safe API client

**Bug Fixes**
- Resolved Electron double window issue
- Fixed vite preload configuration
- Improved startup reliability

**Documentation**
- Added English README
- Created CONTRIBUTING guide
- Added CODE_OF_CONDUCT
- Improved API documentation

### Version 0.1.0 Highlights

**Multi-Agent System**
- Implemented 4 specialized agents
- Residual connection architecture
- Parallel execution support
- Feedback loop mechanism

**Desktop Application**
- Modern Electron + Vue 3 frontend
- Professional animations with GSAP
- Real-time monitoring dashboard
- Dark/light theme support

**MLOps Pipeline**
- Automated data acquisition
- Intelligent image crawling
- Quality-controlled pseudo-labeling
- Adaptive model training

---

## Upgrade Guide

### From 0.1.0 to 0.2.0

1. **Database Migration**
   ```bash
   # Run the new migration in Supabase SQL Editor
   # File: backend/app/db/migrations/002_create_projects_table.sql
   ```

2. **Environment Variables**
   ```bash
   # No new environment variables required
   ```

3. **Dependencies**
   ```bash
   # Backend
   cd backend
   poetry install

   # Frontend
   cd evolauncher-frontend
   npm install
   ```

4. **Test Data**
   ```bash
   cd backend
   poetry run python scripts/insert_test_projects.py
   ```

---

## Future Plans

### Version 0.3.0 (Planned)
- [ ] User authentication and authorization
- [ ] Multi-user support
- [ ] Enhanced analytics dashboard
- [ ] Model version management
- [ ] Experiment tracking
- [ ] CI/CD pipeline

### Version 0.4.0 (Planned)
- [ ] Cloud deployment support
- [ ] Docker containerization
- [ ] Kubernetes orchestration
- [ ] Distributed training
- [ ] GPU cluster support

### Version 1.0.0 (Planned)
- [ ] Production-ready release
- [ ] Comprehensive test coverage
- [ ] Performance optimization
- [ ] Security audit
- [ ] Enterprise features

---

[Unreleased]: https://github.com/Ryder-MHumble/EvoLabeler-AIAgent-MLOps/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Ryder-MHumble/EvoLabeler-AIAgent-MLOps/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Ryder-MHumble/EvoLabeler-AIAgent-MLOps/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/Ryder-MHumble/EvoLabeler-AIAgent-MLOps/releases/tag/v0.0.1



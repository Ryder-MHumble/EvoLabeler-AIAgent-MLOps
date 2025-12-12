# Diff Details

Date : 2025-12-07 22:39:51

Directory /Users/sunminghao/Desktop/EvoLabeler/evolauncher-frontend

Total : 129 files,  4334 codes, -2261 comments, -198 blanks, all 1875 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [backend/README.md](/backend/README.md) | Markdown | -426 | 0 | -150 | -576 |
| [backend/SUPABASE\_KEY\_FIX.md](/backend/SUPABASE_KEY_FIX.md) | Markdown | -43 | 0 | -19 | -62 |
| [backend/app/\_\_init\_\_.py](/backend/app/__init__.py) | Python | -1 | -6 | -2 | -9 |
| [backend/app/agents/\_\_init\_\_.py](/backend/app/agents/__init__.py) | Python | 0 | -1 | -1 | -2 |
| [backend/app/agents/acquisition\_agent.py](/backend/app/agents/acquisition_agent.py) | Python | -322 | -234 | -87 | -643 |
| [backend/app/agents/analysis\_agent.py](/backend/app/agents/analysis_agent.py) | Python | -224 | -253 | -53 | -530 |
| [backend/app/agents/base\_agent.py](/backend/app/agents/base_agent.py) | Python | -24 | -45 | -12 | -81 |
| [backend/app/agents/inference\_agent.py](/backend/app/agents/inference_agent.py) | Python | -243 | -170 | -59 | -472 |
| [backend/app/agents/prompts.py](/backend/app/agents/prompts.py) | Python | -133 | -19 | -26 | -178 |
| [backend/app/agents/state.py](/backend/app/agents/state.py) | Python | -17 | -20 | -13 | -50 |
| [backend/app/agents/training\_agent.py](/backend/app/agents/training_agent.py) | Python | -281 | -161 | -63 | -505 |
| [backend/app/api/\_\_init\_\_.py](/backend/app/api/__init__.py) | Python | 0 | -1 | -1 | -2 |
| [backend/app/api/v1/\_\_init\_\_.py](/backend/app/api/v1/__init__.py) | Python | 0 | -1 | -1 | -2 |
| [backend/app/api/v1/endpoints/\_\_init\_\_.py](/backend/app/api/v1/endpoints/__init__.py) | Python | 0 | -1 | -1 | -2 |
| [backend/app/api/v1/endpoints/jobs.py](/backend/app/api/v1/endpoints/jobs.py) | Python | -149 | -71 | -42 | -262 |
| [backend/app/api/v1/endpoints/projects.py](/backend/app/api/v1/endpoints/projects.py) | Python | -222 | -81 | -41 | -344 |
| [backend/app/api/v1/schemas/\_\_init\_\_.py](/backend/app/api/v1/schemas/__init__.py) | Python | 0 | -1 | -1 | -2 |
| [backend/app/api/v1/schemas/job.py](/backend/app/api/v1/schemas/job.py) | Python | -32 | -13 | -21 | -66 |
| [backend/app/api/v1/schemas/project.py](/backend/app/api/v1/schemas/project.py) | Python | -49 | -13 | -28 | -90 |
| [backend/app/core/\_\_init\_\_.py](/backend/app/core/__init__.py) | Python | 0 | -1 | -1 | -2 |
| [backend/app/core/config.py](/backend/app/core/config.py) | Python | -64 | -19 | -19 | -102 |
| [backend/app/core/logging\_config.py](/backend/app/core/logging_config.py) | Python | -71 | -41 | -29 | -141 |
| [backend/app/db/DATABASE\_DESIGN.md](/backend/app/db/DATABASE_DESIGN.md) | Markdown | -450 | 0 | -121 | -571 |
| [backend/app/db/\_\_init\_\_.py](/backend/app/db/__init__.py) | Python | 0 | -1 | -2 | -3 |
| [backend/app/db/migrations/002\_create\_projects\_table.sql](/backend/app/db/migrations/002_create_projects_table.sql) | MS SQL | -58 | -49 | -34 | -141 |
| [backend/app/db/models.py](/backend/app/db/models.py) | Python | -23 | -52 | -13 | -88 |
| [backend/app/db/supabase\_init.py](/backend/app/db/supabase_init.py) | Python | -26 | -22 | -14 | -62 |
| [backend/app/main.py](/backend/app/main.py) | Python | -129 | -27 | -36 | -192 |
| [backend/app/services/\_\_init\_\_.py](/backend/app/services/__init__.py) | Python | 0 | -1 | -1 | -2 |
| [backend/app/services/advanced\_orchestrator.py](/backend/app/services/advanced_orchestrator.py) | Python | -269 | -138 | -68 | -475 |
| [backend/app/services/orchestrator.py](/backend/app/services/orchestrator.py) | Python | -117 | -60 | -26 | -203 |
| [backend/app/services/workflow\_graph.py](/backend/app/services/workflow_graph.py) | Python | -68 | -73 | -28 | -169 |
| [backend/app/tools/\_\_init\_\_.py](/backend/app/tools/__init__.py) | Python | 0 | -1 | -2 | -3 |
| [backend/app/tools/mcp\_integration.py](/backend/app/tools/mcp_integration.py) | Python | -338 | -116 | -64 | -518 |
| [backend/app/tools/mcp\_tools.py](/backend/app/tools/mcp_tools.py) | Python | -254 | -65 | -61 | -380 |
| [backend/app/tools/qwen\_api\_wrapper.py](/backend/app/tools/qwen_api_wrapper.py) | Python | -113 | -172 | -23 | -308 |
| [backend/app/tools/remote\_client.py](/backend/app/tools/remote_client.py) | Python | -217 | -124 | -44 | -385 |
| [backend/app/tools/subprocess\_executor.py](/backend/app/tools/subprocess_executor.py) | Python | -151 | -67 | -33 | -251 |
| [backend/app/tools/supabase\_client.py](/backend/app/tools/supabase_client.py) | Python | -271 | -160 | -59 | -490 |
| [backend/app/tools/web\_crawler.py](/backend/app/tools/web_crawler.py) | Python | -105 | -72 | -43 | -220 |
| [backend/docs/API.md](/backend/docs/API.md) | Markdown | -316 | 0 | -79 | -395 |
| [backend/docs/ARCHITECTURE.md](/backend/docs/ARCHITECTURE.md) | Markdown | -340 | 0 | -109 | -449 |
| [backend/docs/DevelopPrompt.md](/backend/docs/DevelopPrompt.md) | Markdown | -133 | 0 | -26 | -159 |
| [backend/docs/PROJECT\_MANAGEMENT.md](/backend/docs/PROJECT_MANAGEMENT.md) | Markdown | -188 | 0 | -81 | -269 |
| [backend/docs/PROJECT\_SUMMARY.md](/backend/docs/PROJECT_SUMMARY.md) | Markdown | -243 | 0 | -67 | -310 |
| [backend/requirements.txt](/backend/requirements.txt) | pip requirements | -19 | -10 | -10 | -39 |
| [backend/run.py](/backend/run.py) | Python | -22 | -8 | -9 | -39 |
| [backend/scripts/API\_KEY\_SOLUTION.md](/backend/scripts/API_KEY_SOLUTION.md) | Markdown | -54 | 0 | -29 | -83 |
| [backend/scripts/create\_tables\_auto.py](/backend/scripts/create_tables_auto.py) | Python | -158 | -24 | -28 | -210 |
| [backend/scripts/insert\_test\_data.py](/backend/scripts/insert_test_data.py) | Python | -256 | -53 | -67 | -376 |
| [backend/scripts/insert\_test\_data.sql](/backend/scripts/insert_test_data.sql) | MS SQL | -226 | -14 | -11 | -251 |
| [backend/scripts/insert\_test\_projects.py](/backend/scripts/insert_test_projects.py) | Python | -197 | -18 | -28 | -243 |
| [backend/scripts/setup\_database.py](/backend/scripts/setup_database.py) | Python | -129 | -42 | -35 | -206 |
| [backend/scripts/setup\_supabase.sql](/backend/scripts/setup_supabase.sql) | MS SQL | -37 | -55 | -16 | -108 |
| [backend/scripts/test\_supabase\_connection.py](/backend/scripts/test_supabase_connection.py) | Python | -43 | -8 | -15 | -66 |
| [backend/scripts/verify\_supabase\_data.py](/backend/scripts/verify_supabase_data.py) | Python | -75 | -12 | -16 | -103 |
| [backend/tests/TESTING\_COMPLETE.md](/backend/tests/TESTING_COMPLETE.md) | Markdown | -49 | 0 | -18 | -67 |
| [backend/tests/quick\_playwright\_test.py](/backend/tests/quick_playwright_test.py) | Python | -86 | -18 | -27 | -131 |
| [backend/tests/test\_full\_system.py](/backend/tests/test_full_system.py) | Python | -403 | -86 | -119 | -608 |
| [backend/tests/test\_graph.py](/backend/tests/test_graph.py) | Python | -130 | -41 | -26 | -197 |
| [backend/tests/test\_playwright\_download\_images.py](/backend/tests/test_playwright_download_images.py) | Python | -142 | -41 | -49 | -232 |
| [backend/tests/test\_results.json](/backend/tests/test_results.json) | JSON | -192 | 0 | 0 | -192 |
| [backend/tests/test\_web\_crawler.py](/backend/tests/test_web_crawler.py) | Python | -221 | -51 | -76 | -348 |
| [evolauncher-frontend/.eslintrc.cjs](/evolauncher-frontend/.eslintrc.cjs) | JavaScript | 27 | 0 | 2 | 29 |
| [evolauncher-frontend/.prettierrc.json](/evolauncher-frontend/.prettierrc.json) | JSON | 9 | 0 | 2 | 11 |
| [evolauncher-frontend/BUILD\_GUIDE.md](/evolauncher-frontend/BUILD_GUIDE.md) | Markdown | 287 | 0 | 119 | 406 |
| [evolauncher-frontend/CO\_PILOT\_FEATURES.md](/evolauncher-frontend/CO_PILOT_FEATURES.md) | Markdown | 134 | 3 | 41 | 178 |
| [evolauncher-frontend/QUICKSTART.md](/evolauncher-frontend/QUICKSTART.md) | Markdown | 68 | 0 | 32 | 100 |
| [evolauncher-frontend/README.md](/evolauncher-frontend/README.md) | Markdown | 408 | 0 | 121 | 529 |
| [evolauncher-frontend/electron/main.ts](/evolauncher-frontend/electron/main.ts) | TypeScript | 90 | 14 | 23 | 127 |
| [evolauncher-frontend/electron/preload.ts](/evolauncher-frontend/electron/preload.ts) | TypeScript | 30 | 5 | 8 | 43 |
| [evolauncher-frontend/index.html](/evolauncher-frontend/index.html) | HTML | 13 | 0 | 2 | 15 |
| [evolauncher-frontend/package.json](/evolauncher-frontend/package.json) | JSON | 139 | 0 | 1 | 140 |
| [evolauncher-frontend/postcss.config.js](/evolauncher-frontend/postcss.config.js) | JavaScript | 6 | 0 | 2 | 8 |
| [evolauncher-frontend/src/App.vue](/evolauncher-frontend/src/App.vue) | vue | 110 | 0 | 17 | 127 |
| [evolauncher-frontend/src/api/mocks/mock\_logs.ts](/evolauncher-frontend/src/api/mocks/mock_logs.ts) | TypeScript | 124 | 26 | 23 | 173 |
| [evolauncher-frontend/src/api/mocks/mock\_missions.ts](/evolauncher-frontend/src/api/mocks/mock_missions.ts) | TypeScript | 88 | 18 | 8 | 114 |
| [evolauncher-frontend/src/api/mocks/mock\_stream.ts](/evolauncher-frontend/src/api/mocks/mock_stream.ts) | TypeScript | 191 | 29 | 7 | 227 |
| [evolauncher-frontend/src/api/projects.ts](/evolauncher-frontend/src/api/projects.ts) | TypeScript | 234 | 100 | 53 | 387 |
| [evolauncher-frontend/src/api/types.ts](/evolauncher-frontend/src/api/types.ts) | TypeScript | 63 | 39 | 14 | 116 |
| [evolauncher-frontend/src/assets/styles/\_variables.scss](/evolauncher-frontend/src/assets/styles/_variables.scss) | SCSS | 112 | 23 | 27 | 162 |
| [evolauncher-frontend/src/assets/styles/base.scss](/evolauncher-frontend/src/assets/styles/base.scss) | SCSS | 200 | 44 | 55 | 299 |
| [evolauncher-frontend/src/assets/styles/themes.scss](/evolauncher-frontend/src/assets/styles/themes.scss) | SCSS | 93 | 29 | 26 | 148 |
| [evolauncher-frontend/src/components/common/AnimatedCard.vue](/evolauncher-frontend/src/components/common/AnimatedCard.vue) | vue | 118 | 0 | 20 | 138 |
| [evolauncher-frontend/src/components/common/LoadingSkeleton.vue](/evolauncher-frontend/src/components/common/LoadingSkeleton.vue) | vue | 90 | 0 | 13 | 103 |
| [evolauncher-frontend/src/components/common/StatusBadge.vue](/evolauncher-frontend/src/components/common/StatusBadge.vue) | vue | 188 | 0 | 32 | 220 |
| [evolauncher-frontend/src/components/common/ThemeToggle.vue](/evolauncher-frontend/src/components/common/ThemeToggle.vue) | vue | 198 | 0 | 26 | 224 |
| [evolauncher-frontend/src/components/copilot/WorkspaceHeader.vue](/evolauncher-frontend/src/components/copilot/WorkspaceHeader.vue) | vue | 268 | 0 | 37 | 305 |
| [evolauncher-frontend/src/components/dashboard/AgentStatusList.vue](/evolauncher-frontend/src/components/dashboard/AgentStatusList.vue) | vue | 194 | 0 | 29 | 223 |
| [evolauncher-frontend/src/components/dashboard/HeroSection.vue](/evolauncher-frontend/src/components/dashboard/HeroSection.vue) | vue | 441 | 0 | 63 | 504 |
| [evolauncher-frontend/src/components/dashboard/ProjectCard.vue](/evolauncher-frontend/src/components/dashboard/ProjectCard.vue) | vue | 215 | 0 | 32 | 247 |
| [evolauncher-frontend/src/components/dashboard/ProjectList.vue](/evolauncher-frontend/src/components/dashboard/ProjectList.vue) | vue | 158 | 0 | 22 | 180 |
| [evolauncher-frontend/src/components/layout/AppErrorBoundary.vue](/evolauncher-frontend/src/components/layout/AppErrorBoundary.vue) | vue | 88 | 0 | 13 | 101 |
| [evolauncher-frontend/src/components/layout/AppHeader.vue](/evolauncher-frontend/src/components/layout/AppHeader.vue) | vue | 392 | 0 | 60 | 452 |
| [evolauncher-frontend/src/components/layout/AppSidebar.vue](/evolauncher-frontend/src/components/layout/AppSidebar.vue) | vue | 216 | 0 | 28 | 244 |
| [evolauncher-frontend/src/components/project/CreateProjectWizard.vue](/evolauncher-frontend/src/components/project/CreateProjectWizard.vue) | vue | 1,555 | 0 | 204 | 1,759 |
| [evolauncher-frontend/src/components/workspace/AgentPanel.vue](/evolauncher-frontend/src/components/workspace/AgentPanel.vue) | vue | 374 | 0 | 54 | 428 |
| [evolauncher-frontend/src/components/workspace/AgentTelemetryPanel.vue](/evolauncher-frontend/src/components/workspace/AgentTelemetryPanel.vue) | vue | 367 | 0 | 57 | 424 |
| [evolauncher-frontend/src/components/workspace/DataInbox.vue](/evolauncher-frontend/src/components/workspace/DataInbox.vue) | vue | 312 | 0 | 48 | 360 |
| [evolauncher-frontend/src/components/workspace/EvolutionMonitor.vue](/evolauncher-frontend/src/components/workspace/EvolutionMonitor.vue) | vue | 189 | 0 | 34 | 223 |
| [evolauncher-frontend/src/components/workspace/LiveTerminal.vue](/evolauncher-frontend/src/components/workspace/LiveTerminal.vue) | vue | 255 | 0 | 43 | 298 |
| [evolauncher-frontend/src/components/workspace/LossChartCard.vue](/evolauncher-frontend/src/components/workspace/LossChartCard.vue) | vue | 296 | 0 | 43 | 339 |
| [evolauncher-frontend/src/components/workspace/McpToolsPanel.vue](/evolauncher-frontend/src/components/workspace/McpToolsPanel.vue) | vue | 308 | 0 | 47 | 355 |
| [evolauncher-frontend/src/components/workspace/SeedUploadZone.vue](/evolauncher-frontend/src/components/workspace/SeedUploadZone.vue) | vue | 360 | 0 | 63 | 423 |
| [evolauncher-frontend/src/components/workspace/SmartCanvas.vue](/evolauncher-frontend/src/components/workspace/SmartCanvas.vue) | vue | 1,011 | 0 | 155 | 1,166 |
| [evolauncher-frontend/src/components/workspace/TrainingDetailsCard.vue](/evolauncher-frontend/src/components/workspace/TrainingDetailsCard.vue) | vue | 279 | 0 | 34 | 313 |
| [evolauncher-frontend/src/components/workspace/YoloMetricsCard.vue](/evolauncher-frontend/src/components/workspace/YoloMetricsCard.vue) | vue | 283 | 0 | 43 | 326 |
| [evolauncher-frontend/src/components/workspace/types.ts](/evolauncher-frontend/src/components/workspace/types.ts) | TypeScript | 22 | 7 | 7 | 36 |
| [evolauncher-frontend/src/composables/useTheme.ts](/evolauncher-frontend/src/composables/useTheme.ts) | TypeScript | 76 | 39 | 22 | 137 |
| [evolauncher-frontend/src/locales/en.json](/evolauncher-frontend/src/locales/en.json) | JSON | 164 | 0 | 2 | 166 |
| [evolauncher-frontend/src/locales/zh-CN.json](/evolauncher-frontend/src/locales/zh-CN.json) | JSON | 266 | 0 | 1 | 267 |
| [evolauncher-frontend/src/main.ts](/evolauncher-frontend/src/main.ts) | TypeScript | 25 | 16 | 12 | 53 |
| [evolauncher-frontend/src/mock/agents.ts](/evolauncher-frontend/src/mock/agents.ts) | TypeScript | 99 | 0 | 6 | 105 |
| [evolauncher-frontend/src/mock/jobStatus.ts](/evolauncher-frontend/src/mock/jobStatus.ts) | TypeScript | 186 | 51 | 33 | 270 |
| [evolauncher-frontend/src/mock/mcpTools.ts](/evolauncher-frontend/src/mock/mcpTools.ts) | TypeScript | 51 | 0 | 5 | 56 |
| [evolauncher-frontend/src/mock/projects.ts](/evolauncher-frontend/src/mock/projects.ts) | TypeScript | 107 | 27 | 8 | 142 |
| [evolauncher-frontend/src/mock/systemMetrics.ts](/evolauncher-frontend/src/mock/systemMetrics.ts) | TypeScript | 47 | 0 | 3 | 50 |
| [evolauncher-frontend/src/router/index.ts](/evolauncher-frontend/src/router/index.ts) | TypeScript | 43 | 3 | 7 | 53 |
| [evolauncher-frontend/src/store/app.ts](/evolauncher-frontend/src/store/app.ts) | TypeScript | 63 | 14 | 16 | 93 |
| [evolauncher-frontend/src/store/mission.ts](/evolauncher-frontend/src/store/mission.ts) | TypeScript | 196 | 67 | 41 | 304 |
| [evolauncher-frontend/src/types/electron.d.ts](/evolauncher-frontend/src/types/electron.d.ts) | TypeScript | 13 | 0 | 3 | 16 |
| [evolauncher-frontend/src/utils/retry.ts](/evolauncher-frontend/src/utils/retry.ts) | TypeScript | 33 | 4 | 6 | 43 |
| [evolauncher-frontend/src/views/CoPilotWorkspaceView.vue](/evolauncher-frontend/src/views/CoPilotWorkspaceView.vue) | vue | 178 | 0 | 29 | 207 |
| [evolauncher-frontend/src/views/DashboardView.vue](/evolauncher-frontend/src/views/DashboardView.vue) | vue | 218 | 0 | 27 | 245 |
| [evolauncher-frontend/src/views/WorkspaceView.vue](/evolauncher-frontend/src/views/WorkspaceView.vue) | vue | 325 | 0 | 62 | 387 |
| [evolauncher-frontend/tailwind.config.js](/evolauncher-frontend/tailwind.config.js) | JavaScript | 64 | 3 | 2 | 69 |
| [evolauncher-frontend/tsconfig.json](/evolauncher-frontend/tsconfig.json) | JSON with Comments | 26 | 3 | 5 | 34 |
| [evolauncher-frontend/tsconfig.node.json](/evolauncher-frontend/tsconfig.node.json) | JSON | 10 | 0 | 2 | 12 |
| [evolauncher-frontend/vite.config.ts](/evolauncher-frontend/vite.config.ts) | TypeScript | 90 | 8 | 3 | 101 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details
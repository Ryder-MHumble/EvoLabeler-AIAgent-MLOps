# Details

Date : 2025-12-07 22:39:29

Directory /Users/sunminghao/Desktop/EvoLabeler/backend

Total : 63 files,  8549 codes, 2833 comments, 2283 blanks, all 13665 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [backend/README.md](/backend/README.md) | Markdown | 426 | 0 | 150 | 576 |
| [backend/SUPABASE\_KEY\_FIX.md](/backend/SUPABASE_KEY_FIX.md) | Markdown | 43 | 0 | 19 | 62 |
| [backend/app/\_\_init\_\_.py](/backend/app/__init__.py) | Python | 1 | 6 | 2 | 9 |
| [backend/app/agents/\_\_init\_\_.py](/backend/app/agents/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/app/agents/acquisition\_agent.py](/backend/app/agents/acquisition_agent.py) | Python | 322 | 234 | 87 | 643 |
| [backend/app/agents/analysis\_agent.py](/backend/app/agents/analysis_agent.py) | Python | 224 | 253 | 53 | 530 |
| [backend/app/agents/base\_agent.py](/backend/app/agents/base_agent.py) | Python | 24 | 45 | 12 | 81 |
| [backend/app/agents/inference\_agent.py](/backend/app/agents/inference_agent.py) | Python | 243 | 170 | 59 | 472 |
| [backend/app/agents/prompts.py](/backend/app/agents/prompts.py) | Python | 133 | 19 | 26 | 178 |
| [backend/app/agents/state.py](/backend/app/agents/state.py) | Python | 17 | 20 | 13 | 50 |
| [backend/app/agents/training\_agent.py](/backend/app/agents/training_agent.py) | Python | 281 | 161 | 63 | 505 |
| [backend/app/api/\_\_init\_\_.py](/backend/app/api/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/app/api/v1/\_\_init\_\_.py](/backend/app/api/v1/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/app/api/v1/endpoints/\_\_init\_\_.py](/backend/app/api/v1/endpoints/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/app/api/v1/endpoints/jobs.py](/backend/app/api/v1/endpoints/jobs.py) | Python | 149 | 71 | 42 | 262 |
| [backend/app/api/v1/endpoints/projects.py](/backend/app/api/v1/endpoints/projects.py) | Python | 222 | 81 | 41 | 344 |
| [backend/app/api/v1/schemas/\_\_init\_\_.py](/backend/app/api/v1/schemas/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/app/api/v1/schemas/job.py](/backend/app/api/v1/schemas/job.py) | Python | 32 | 13 | 21 | 66 |
| [backend/app/api/v1/schemas/project.py](/backend/app/api/v1/schemas/project.py) | Python | 49 | 13 | 28 | 90 |
| [backend/app/core/\_\_init\_\_.py](/backend/app/core/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/app/core/config.py](/backend/app/core/config.py) | Python | 64 | 19 | 19 | 102 |
| [backend/app/core/logging\_config.py](/backend/app/core/logging_config.py) | Python | 71 | 41 | 29 | 141 |
| [backend/app/db/DATABASE\_DESIGN.md](/backend/app/db/DATABASE_DESIGN.md) | Markdown | 450 | 0 | 121 | 571 |
| [backend/app/db/\_\_init\_\_.py](/backend/app/db/__init__.py) | Python | 0 | 1 | 2 | 3 |
| [backend/app/db/migrations/002\_create\_projects\_table.sql](/backend/app/db/migrations/002_create_projects_table.sql) | MS SQL | 58 | 49 | 34 | 141 |
| [backend/app/db/models.py](/backend/app/db/models.py) | Python | 23 | 52 | 13 | 88 |
| [backend/app/db/supabase\_init.py](/backend/app/db/supabase_init.py) | Python | 26 | 22 | 14 | 62 |
| [backend/app/main.py](/backend/app/main.py) | Python | 129 | 27 | 36 | 192 |
| [backend/app/services/\_\_init\_\_.py](/backend/app/services/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/app/services/advanced\_orchestrator.py](/backend/app/services/advanced_orchestrator.py) | Python | 269 | 138 | 68 | 475 |
| [backend/app/services/orchestrator.py](/backend/app/services/orchestrator.py) | Python | 117 | 60 | 26 | 203 |
| [backend/app/services/workflow\_graph.py](/backend/app/services/workflow_graph.py) | Python | 68 | 73 | 28 | 169 |
| [backend/app/tools/\_\_init\_\_.py](/backend/app/tools/__init__.py) | Python | 0 | 1 | 2 | 3 |
| [backend/app/tools/mcp\_integration.py](/backend/app/tools/mcp_integration.py) | Python | 338 | 116 | 64 | 518 |
| [backend/app/tools/mcp\_tools.py](/backend/app/tools/mcp_tools.py) | Python | 254 | 65 | 61 | 380 |
| [backend/app/tools/qwen\_api\_wrapper.py](/backend/app/tools/qwen_api_wrapper.py) | Python | 113 | 172 | 23 | 308 |
| [backend/app/tools/remote\_client.py](/backend/app/tools/remote_client.py) | Python | 217 | 124 | 44 | 385 |
| [backend/app/tools/subprocess\_executor.py](/backend/app/tools/subprocess_executor.py) | Python | 151 | 67 | 33 | 251 |
| [backend/app/tools/supabase\_client.py](/backend/app/tools/supabase_client.py) | Python | 271 | 160 | 59 | 490 |
| [backend/app/tools/web\_crawler.py](/backend/app/tools/web_crawler.py) | Python | 105 | 72 | 43 | 220 |
| [backend/docs/API.md](/backend/docs/API.md) | Markdown | 316 | 0 | 79 | 395 |
| [backend/docs/ARCHITECTURE.md](/backend/docs/ARCHITECTURE.md) | Markdown | 340 | 0 | 109 | 449 |
| [backend/docs/DevelopPrompt.md](/backend/docs/DevelopPrompt.md) | Markdown | 133 | 0 | 26 | 159 |
| [backend/docs/PROJECT\_MANAGEMENT.md](/backend/docs/PROJECT_MANAGEMENT.md) | Markdown | 188 | 0 | 81 | 269 |
| [backend/docs/PROJECT\_SUMMARY.md](/backend/docs/PROJECT_SUMMARY.md) | Markdown | 243 | 0 | 67 | 310 |
| [backend/requirements.txt](/backend/requirements.txt) | pip requirements | 19 | 10 | 10 | 39 |
| [backend/run.py](/backend/run.py) | Python | 22 | 8 | 9 | 39 |
| [backend/scripts/API\_KEY\_SOLUTION.md](/backend/scripts/API_KEY_SOLUTION.md) | Markdown | 54 | 0 | 29 | 83 |
| [backend/scripts/create\_tables\_auto.py](/backend/scripts/create_tables_auto.py) | Python | 158 | 24 | 28 | 210 |
| [backend/scripts/insert\_test\_data.py](/backend/scripts/insert_test_data.py) | Python | 256 | 53 | 67 | 376 |
| [backend/scripts/insert\_test\_data.sql](/backend/scripts/insert_test_data.sql) | MS SQL | 226 | 14 | 11 | 251 |
| [backend/scripts/insert\_test\_projects.py](/backend/scripts/insert_test_projects.py) | Python | 197 | 18 | 28 | 243 |
| [backend/scripts/setup\_database.py](/backend/scripts/setup_database.py) | Python | 129 | 42 | 35 | 206 |
| [backend/scripts/setup\_supabase.sql](/backend/scripts/setup_supabase.sql) | MS SQL | 37 | 55 | 16 | 108 |
| [backend/scripts/test\_supabase\_connection.py](/backend/scripts/test_supabase_connection.py) | Python | 43 | 8 | 15 | 66 |
| [backend/scripts/verify\_supabase\_data.py](/backend/scripts/verify_supabase_data.py) | Python | 75 | 12 | 16 | 103 |
| [backend/tests/TESTING\_COMPLETE.md](/backend/tests/TESTING_COMPLETE.md) | Markdown | 49 | 0 | 18 | 67 |
| [backend/tests/quick\_playwright\_test.py](/backend/tests/quick_playwright_test.py) | Python | 86 | 18 | 27 | 131 |
| [backend/tests/test\_full\_system.py](/backend/tests/test_full_system.py) | Python | 403 | 86 | 119 | 608 |
| [backend/tests/test\_graph.py](/backend/tests/test_graph.py) | Python | 130 | 41 | 26 | 197 |
| [backend/tests/test\_playwright\_download\_images.py](/backend/tests/test_playwright_download_images.py) | Python | 142 | 41 | 49 | 232 |
| [backend/tests/test\_results.json](/backend/tests/test_results.json) | JSON | 192 | 0 | 0 | 192 |
| [backend/tests/test\_web\_crawler.py](/backend/tests/test_web_crawler.py) | Python | 221 | 51 | 76 | 348 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)
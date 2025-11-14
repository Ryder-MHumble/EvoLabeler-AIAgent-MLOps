-- Supabase 测试数据插入 SQL 脚本
-- 可以直接在 Supabase Dashboard 的 SQL Editor 中执行

-- 清空现有测试数据（可选）
-- DELETE FROM inference_results WHERE job_id LIKE 'test_job_%';
-- DELETE FROM jobs WHERE job_id LIKE 'test_job_%';

-- 插入测试任务数据
INSERT INTO jobs (job_id, status, progress_message, metadata, created_at, updated_at)
VALUES
  (
    'test_job_20241114_001',
    'COMPLETE',
    '任务已完成',
    '{
      "project_name": "测试项目 1",
      "description": "这是一个测试项目，用于验证系统功能",
      "model_type": "YOLOv8",
      "dataset_size": 450,
      "accuracy": 0.875,
      "epochs": 50,
      "created_by": "test_script"
    }'::jsonb,
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '1 day'
  ),
  (
    'test_job_20241114_002',
    'TRAINING',
    '正在训练模型...',
    '{
      "project_name": "测试项目 2",
      "description": "这是一个测试项目，用于验证系统功能",
      "model_type": "YOLOv9",
      "dataset_size": 680,
      "epochs": 35,
      "created_by": "test_script"
    }'::jsonb,
    NOW() - INTERVAL '3 days',
    NOW() - INTERVAL '2 hours'
  ),
  (
    'test_job_20241114_003',
    'PSEUDO_LABELING',
    '正在生成伪标签...',
    '{
      "project_name": "测试项目 3",
      "description": "这是一个测试项目，用于验证系统功能",
      "model_type": "YOLOv10",
      "dataset_size": 320,
      "created_by": "test_script"
    }'::jsonb,
    NOW() - INTERVAL '2 days',
    NOW() - INTERVAL '1 hour'
  ),
  (
    'test_job_20241114_004',
    'ACQUISITION',
    '正在采集新样本...',
    '{
      "project_name": "测试项目 4",
      "description": "这是一个测试项目，用于验证系统功能",
      "model_type": "YOLOv8",
      "dataset_size": 250,
      "created_by": "test_script"
    }'::jsonb,
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '30 minutes'
  ),
  (
    'test_job_20241114_005',
    'INFERENCE',
    '正在进行推理分析...',
    '{
      "project_name": "测试项目 5",
      "description": "这是一个测试项目，用于验证系统功能",
      "model_type": "YOLOv9",
      "dataset_size": 890,
      "created_by": "test_script"
    }'::jsonb,
    NOW() - INTERVAL '6 hours',
    NOW() - INTERVAL '10 minutes'
  );

-- 插入推理结果数据
INSERT INTO inference_results (job_id, image_path, predictions, created_at)
VALUES
  -- test_job_20241114_001 的推理结果
  (
    'test_job_20241114_001',
    'test_job_20241114_001/images/image_001.jpg',
    '[
      {"class": "ship", "confidence": 0.892, "bbox": [0.15, 0.23, 0.25, 0.28]},
      {"class": "airplane", "confidence": 0.756, "bbox": [0.45, 0.12, 0.22, 0.19]}
    ]'::jsonb,
    NOW() - INTERVAL '4 days'
  ),
  (
    'test_job_20241114_001',
    'test_job_20241114_001/images/image_002.jpg',
    '[
      {"class": "vehicle", "confidence": 0.823, "bbox": [0.32, 0.45, 0.18, 0.22]},
      {"class": "building", "confidence": 0.901, "bbox": [0.12, 0.67, 0.35, 0.28]}
    ]'::jsonb,
    NOW() - INTERVAL '4 days' + INTERVAL '1 hour'
  ),
  (
    'test_job_20241114_001',
    'test_job_20241114_001/images/image_003.jpg',
    '[
      {"class": "port", "confidence": 0.945, "bbox": [0.20, 0.30, 0.40, 0.35]}
    ]'::jsonb,
    NOW() - INTERVAL '4 days' + INTERVAL '2 hours'
  ),
  
  -- test_job_20241114_002 的推理结果
  (
    'test_job_20241114_002',
    'test_job_20241114_002/images/image_001.jpg',
    '[
      {"class": "airplane", "confidence": 0.887, "bbox": [0.25, 0.15, 0.28, 0.24]},
      {"class": "airplane", "confidence": 0.734, "bbox": [0.60, 0.20, 0.22, 0.18]}
    ]'::jsonb,
    NOW() - INTERVAL '2 days'
  ),
  (
    'test_job_20241114_002',
    'test_job_20241114_002/images/image_002.jpg',
    '[
      {"class": "road", "confidence": 0.812, "bbox": [0.10, 0.50, 0.80, 0.15]},
      {"class": "vehicle", "confidence": 0.765, "bbox": [0.35, 0.45, 0.18, 0.20]}
    ]'::jsonb,
    NOW() - INTERVAL '2 days' + INTERVAL '1 hour'
  ),
  (
    'test_job_20241114_002',
    'test_job_20241114_002/images/image_003.jpg',
    '[
      {"class": "bridge", "confidence": 0.923, "bbox": [0.15, 0.40, 0.70, 0.25]}
    ]'::jsonb,
    NOW() - INTERVAL '2 days' + INTERVAL '2 hours'
  ),
  
  -- test_job_20241114_003 的推理结果
  (
    'test_job_20241114_003',
    'test_job_20241114_003/images/image_001.jpg',
    '[
      {"class": "building", "confidence": 0.856, "bbox": [0.20, 0.25, 0.30, 0.35]},
      {"class": "building", "confidence": 0.789, "bbox": [0.55, 0.30, 0.28, 0.32]}
    ]'::jsonb,
    NOW() - INTERVAL '1 day'
  ),
  (
    'test_job_20241114_003',
    'test_job_20241114_003/images/image_002.jpg',
    '[
      {"class": "ship", "confidence": 0.912, "bbox": [0.30, 0.50, 0.35, 0.28]}
    ]'::jsonb,
    NOW() - INTERVAL '1 day' + INTERVAL '1 hour'
  ),
  (
    'test_job_20241114_003',
    'test_job_20241114_003/images/image_003.jpg',
    '[
      {"class": "vehicle", "confidence": 0.743, "bbox": [0.15, 0.60, 0.20, 0.22]},
      {"class": "road", "confidence": 0.801, "bbox": [0.10, 0.75, 0.85, 0.12]}
    ]'::jsonb,
    NOW() - INTERVAL '1 day' + INTERVAL '2 hours'
  ),
  
  -- test_job_20241114_004 的推理结果
  (
    'test_job_20241114_004',
    'test_job_20241114_004/images/image_001.jpg',
    '[
      {"class": "port", "confidence": 0.878, "bbox": [0.25, 0.35, 0.45, 0.40]}
    ]'::jsonb,
    NOW() - INTERVAL '12 hours'
  ),
  (
    'test_job_20241114_004',
    'test_job_20241114_004/images/image_002.jpg',
    '[
      {"class": "ship", "confidence": 0.834, "bbox": [0.40, 0.45, 0.30, 0.25]},
      {"class": "ship", "confidence": 0.712, "bbox": [0.10, 0.50, 0.25, 0.22]}
    ]'::jsonb,
    NOW() - INTERVAL '11 hours'
  ),
  (
    'test_job_20241114_004',
    'test_job_20241114_004/images/image_003.jpg',
    '[
      {"class": "airplane", "confidence": 0.901, "bbox": [0.50, 0.20, 0.30, 0.26]}
    ]'::jsonb,
    NOW() - INTERVAL '10 hours'
  ),
  
  -- test_job_20241114_005 的推理结果
  (
    'test_job_20241114_005',
    'test_job_20241114_005/images/image_001.jpg',
    '[
      {"class": "building", "confidence": 0.867, "bbox": [0.15, 0.20, 0.32, 0.38]},
      {"class": "road", "confidence": 0.745, "bbox": [0.05, 0.70, 0.90, 0.15]}
    ]'::jsonb,
    NOW() - INTERVAL '5 hours'
  ),
  (
    'test_job_20241114_005',
    'test_job_20241114_005/images/image_002.jpg',
    '[
      {"class": "bridge", "confidence": 0.934, "bbox": [0.20, 0.45, 0.60, 0.30]}
    ]'::jsonb,
    NOW() - INTERVAL '4 hours'
  ),
  (
    'test_job_20241114_005',
    'test_job_20241114_005/images/image_003.jpg',
    '[
      {"class": "vehicle", "confidence": 0.788, "bbox": [0.30, 0.55, 0.22, 0.24]},
      {"class": "vehicle", "confidence": 0.721, "bbox": [0.65, 0.60, 0.20, 0.21]}
    ]'::jsonb,
    NOW() - INTERVAL '3 hours'
  );

-- 验证数据
SELECT 
  'Jobs 表' AS table_name,
  COUNT(*) AS record_count
FROM jobs
WHERE job_id LIKE 'test_job_%'
UNION ALL
SELECT 
  'Inference Results 表' AS table_name,
  COUNT(*) AS record_count
FROM inference_results
WHERE job_id LIKE 'test_job_%';

-- 显示插入的数据概览
SELECT 
  j.job_id,
  j.status,
  COUNT(ir.id) AS inference_count
FROM jobs j
LEFT JOIN inference_results ir ON j.job_id = ir.job_id
WHERE j.job_id LIKE 'test_job_%'
GROUP BY j.job_id, j.status
ORDER BY j.job_id;


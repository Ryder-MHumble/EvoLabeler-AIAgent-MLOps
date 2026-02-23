"""
Insert test project data into Supabase.

This script populates the projects table with realistic test data
for frontend development and testing purposes.

Usage:
    python scripts/insert_test_projects.py
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.supabase_init import get_supabase_client
from app.core.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


# Test project data matching frontend mock data
TEST_PROJECTS = [
    {
        "project_id": "proj_wildlife_001",
        "name": "野生动物分类识别",
        "description": "野生动物物种识别的自动化标注项目",
        "status": "completed",
        "image_count": 1250,
        "accuracy": 94.5,
        "thumbnail_url": "https://picsum.photos/seed/101/400/300",
        "metadata": {
            "model_type": "yolov5m",
            "classes": ["deer", "bear", "wolf", "fox"],
            "training_epochs": 150,
            "dataset_source": "wildlife_camera_traps"
        }
    },
    {
        "project_id": "proj_medical_002",
        "name": "医学影像数据集",
        "description": "X光和CT扫描图像的标注项目",
        "status": "training",
        "image_count": 3420,
        "accuracy": 87.2,
        "thumbnail_url": "https://picsum.photos/seed/202/400/300",
        "metadata": {
            "model_type": "yolov5l",
            "classes": ["tumor", "fracture", "nodule"],
            "training_epochs": 200,
            "dataset_source": "medical_imaging_db"
        }
    },
    {
        "project_id": "proj_traffic_003",
        "name": "城市交通分析",
        "description": "城市环境中的车辆和行人检测",
        "status": "labeling",
        "image_count": 8750,
        "accuracy": None,
        "thumbnail_url": "https://picsum.photos/seed/303/400/300",
        "metadata": {
            "model_type": "yolov5s",
            "classes": ["car", "bus", "truck", "pedestrian", "bicycle"],
            "training_epochs": None,
            "dataset_source": "city_traffic_cameras"
        }
    },
    {
        "project_id": "proj_ecommerce_004",
        "name": "商品目录管理",
        "description": "电商产品分类与识别",
        "status": "idle",
        "image_count": 542,
        "accuracy": None,
        "thumbnail_url": "https://picsum.photos/seed/404/400/300",
        "metadata": {
            "model_type": "yolov5s",
            "classes": ["clothing", "electronics", "furniture", "toys"],
            "training_epochs": None,
            "dataset_source": "ecommerce_catalog"
        }
    },
    {
        "project_id": "proj_satellite_005",
        "name": "卫星遥感影像",
        "description": "基于卫星数据的土地利用分类",
        "status": "completed",
        "image_count": 15600,
        "accuracy": 91.8,
        "thumbnail_url": "https://picsum.photos/seed/505/400/300",
        "metadata": {
            "model_type": "yolov5x",
            "classes": ["urban", "forest", "water", "agriculture", "barren"],
            "training_epochs": 250,
            "dataset_source": "landsat_8",
            "resolution": "30m"
        }
    },
    {
        "project_id": "proj_factory_006",
        "name": "工业质检系统",
        "description": "自动化产品缺陷检测",
        "status": "training",
        "image_count": 2890,
        "accuracy": 89.3,
        "thumbnail_url": "https://picsum.photos/seed/606/400/300",
        "metadata": {
            "model_type": "yolov5m",
            "classes": ["scratch", "dent", "discoloration", "crack"],
            "training_epochs": 180,
            "dataset_source": "factory_qc_cameras"
        }
    },
    {
        "project_id": "proj_agriculture_007",
        "name": "农作物病虫害检测",
        "description": "农田作物病虫害早期识别",
        "status": "labeling",
        "image_count": 4520,
        "accuracy": None,
        "thumbnail_url": "https://picsum.photos/seed/707/400/300",
        "metadata": {
            "model_type": "yolov5s",
            "classes": ["blight", "rust", "aphids", "caterpillar"],
            "training_epochs": None,
            "dataset_source": "agricultural_drones"
        }
    },
    {
        "project_id": "proj_security_008",
        "name": "智能安防监控",
        "description": "异常行为和入侵检测",
        "status": "completed",
        "image_count": 6780,
        "accuracy": 92.7,
        "thumbnail_url": "https://picsum.photos/seed/808/400/300",
        "metadata": {
            "model_type": "yolov5l",
            "classes": ["person", "vehicle", "package", "weapon"],
            "training_epochs": 220,
            "dataset_source": "security_cameras"
        }
    }
]


def insert_test_projects() -> None:
    """Insert test projects into Supabase."""
    
    print("\n" + "="*70)
    print("Insert Test Projects Script")
    print("="*70 + "\n")
    
    try:
        # Initialize Supabase client
        print("1️⃣  Initializing Supabase client...")
        client = get_supabase_client()
        print("   ✅ Supabase client initialized\n")
        
        # Check if projects table exists
        print("2️⃣  Checking projects table...")
        try:
            response = client.table("projects").select("project_id", count="exact").limit(1).execute()
            print(f"   ✅ Projects table exists (current count: {response.count})\n")
        except Exception as e:
            print(f"   ❌ Error accessing projects table: {e}")
            print("\n💡 Please run the migration SQL first:")
            print("   backend/app/db/migrations/002_create_projects_table.sql\n")
            return
        
        # Clear existing test data
        print("3️⃣  Clearing existing test projects...")
        try:
            test_project_ids = [p["project_id"] for p in TEST_PROJECTS]
            for project_id in test_project_ids:
                try:
                    client.table("projects").delete().eq("project_id", project_id).execute()
                except Exception:
                    pass  # Project doesn't exist, that's fine
            print("   ✅ Cleared existing test data\n")
        except Exception as e:
            print(f"   ⚠️  Warning: Could not clear existing data: {e}\n")
        
        # Insert test projects
        print("4️⃣  Inserting test projects...")
        inserted_count = 0
        
        for i, project in enumerate(TEST_PROJECTS, 1):
            try:
                # Adjust created_at to be recent but spread out
                days_ago = len(TEST_PROJECTS) - i
                created_at = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
                project["created_at"] = created_at
                project["updated_at"] = created_at
                
                response = client.table("projects").insert(project).execute()
                
                if response.data:
                    inserted_count += 1
                    print(f"   ✅ Inserted: {project['name']} ({project['project_id']})")
                else:
                    print(f"   ❌ Failed: {project['name']}")
                    
            except Exception as e:
                print(f"   ❌ Error inserting {project['name']}: {e}")
        
        print(f"\n5️⃣  Summary:")
        print(f"   📊 Total projects inserted: {inserted_count}/{len(TEST_PROJECTS)}")
        
        # Verify insertion
        print("\n6️⃣  Verifying data...")
        response = client.table("projects").select("*", count="exact").execute()
        print(f"   ✅ Total projects in database: {response.count}")
        
        if response.data:
            print("\n   Sample projects:")
            for project in response.data[:3]:
                print(f"      - {project['name']} ({project['status']}) - {project['image_count']} images")
        
        print("\n" + "="*70)
        print("✅ Test data insertion completed successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Failed to insert test data: {e}")
        logger.error(f"Failed to insert test projects: {e}", exc_info=True)
        print("\n💡 Please check:")
        print("   1. Supabase credentials are correctly configured")
        print("   2. The projects table has been created")
        print("   3. Network connection to Supabase is working\n")


if __name__ == "__main__":
    insert_test_projects()







"""
Training Agent for triggering model training.

This agent is responsible for preparing the dataset and
triggering remote YOLO model training.
"""

from typing import Any
from pathlib import Path
import yaml

from app.agents.base_agent import BaseAgent
from app.tools.subprocess_executor import SubprocessExecutor
from app.tools.supabase_client import SupabaseClient
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class TrainingAgent(BaseAgent):
    """
    Agent for model training.
    
    This agent:
    1. Prepares training dataset (combines original + acquired data)
    2. Generates data.yaml configuration
    3. Triggers YOLO training
    4. Monitors training progress
    """

    def __init__(
        self,
        subprocess_executor: SubprocessExecutor,
        supabase_client: SupabaseClient
    ) -> None:
        """
        Initialize the Training Agent.
        
        Args:
            subprocess_executor: Executor for running training scripts
            supabase_client: Client for database operations
        """
        super().__init__(agent_name="TrainingAgent")
        self.subprocess_executor = subprocess_executor
        self.supabase_client = supabase_client

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute model training.
        
        Args:
            context: Must contain:
                - job_id: str
                - uploaded_images: list[str]
                - acquired_images: list[str]
                - pseudo_labels: list[dict]
                
        Returns:
            Dictionary containing:
                - training_started: bool
                - training_config: dict
        """
        self._log_execution_start()
        
        try:
            job_id = context["job_id"]
            uploaded_images = context.get("uploaded_images", [])
            acquired_images = context.get("acquired_images", [])
            pseudo_labels = context.get("pseudo_labels", [])
            
            logger.info(
                f"Preparing training with {len(uploaded_images)} original "
                f"and {len(acquired_images)} acquired images",
                extra={"job_id": job_id}
            )
            
            # Step 1: Prepare dataset directory structure
            dataset_path = await self._prepare_dataset(
                job_id=job_id,
                original_images=uploaded_images,
                acquired_images=acquired_images,
                pseudo_labels=pseudo_labels
            )
            
            # Step 2: Generate data.yaml
            data_yaml_path = await self._generate_data_yaml(
                dataset_path=dataset_path,
                job_id=job_id
            )
            
            # Step 3: Trigger training
            training_result = await self.subprocess_executor.run_yolo_train(
                data_yaml_path=data_yaml_path,
                model_config="yolov5s.yaml",
                epochs=100,
                batch_size=16,
                img_size=640,
                weights="yolov5s.pt",  # Pre-trained weights
            )
            
            logger.info("Training completed successfully")
            
            self._log_execution_end("Training job submitted")
            
            return {
                "training_started": True,
                "training_config": {
                    "dataset_path": dataset_path,
                    "data_yaml": data_yaml_path,
                    "epochs": 100,
                    "batch_size": 16,
                },
                "training_result": training_result,
            }
            
        except Exception as e:
            self._log_error(e)
            raise

    async def _prepare_dataset(
        self,
        job_id: str,
        original_images: list[str],
        acquired_images: list[str],
        pseudo_labels: list[dict[str, Any]]
    ) -> str:
        """
        Prepare dataset in YOLO format.
        
        Creates directory structure:
        /dataset/{job_id}/
            images/
                train/
                val/
            labels/
                train/
                val/
        
        Args:
            job_id: Job identifier
            original_images: Original uploaded images
            acquired_images: Web-acquired images
            pseudo_labels: Pseudo labels for acquired images
            
        Returns:
            Path to dataset directory
        """
        dataset_path = Path(f"/tmp/datasets/{job_id}")
        
        # Create directory structure
        (dataset_path / "images" / "train").mkdir(parents=True, exist_ok=True)
        (dataset_path / "images" / "val").mkdir(parents=True, exist_ok=True)
        (dataset_path / "labels" / "train").mkdir(parents=True, exist_ok=True)
        (dataset_path / "labels" / "val").mkdir(parents=True, exist_ok=True)
        
        # Copy/link images and labels
        # Implementation would:
        # 1. Split data into train/val
        # 2. Copy images to appropriate directories
        # 3. Generate YOLO format label files
        
        logger.info(f"Dataset prepared at: {dataset_path}")
        return str(dataset_path)

    async def _generate_data_yaml(
        self,
        dataset_path: str,
        job_id: str
    ) -> str:
        """
        Generate data.yaml configuration for YOLO training.
        
        Args:
            dataset_path: Path to dataset directory
            job_id: Job identifier
            
        Returns:
            Path to data.yaml file
        """
        data_yaml_path = Path(dataset_path) / "data.yaml"
        
        # Define dataset configuration
        data_config = {
            "path": dataset_path,
            "train": "images/train",
            "val": "images/val",
            "nc": 1,  # Number of classes (adjust as needed)
            "names": ["object"],  # Class names (adjust as needed)
        }
        
        # Write to file
        with open(data_yaml_path, 'w') as f:
            yaml.dump(data_config, f, default_flow_style=False)
        
        logger.info(f"Generated data.yaml at: {data_yaml_path}")
        return str(data_yaml_path)


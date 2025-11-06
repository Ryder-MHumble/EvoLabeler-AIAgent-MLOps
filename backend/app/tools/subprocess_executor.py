"""
Subprocess executor for running external scripts.

This module provides a SubprocessExecutor class for running
YOLO training and prediction scripts as external processes.
"""

import asyncio
import json
from typing import Any, Optional
from pathlib import Path

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class SubprocessExecutor:
    """
    Executor for running external scripts as subprocesses.
    
    This class handles:
    - YOLO model prediction
    - YOLO model training
    - Command line argument construction
    - Process output capture
    """

    def __init__(self) -> None:
        """Initialize the subprocess executor."""
        self.yolo_project_path = Path(settings.remote_yolo_project_path)
        self.train_script = settings.remote_training_script
        self.predict_script = settings.remote_predict_script
        logger.info("SubprocessExecutor initialized")

    async def run_yolo_predict(
        self,
        model_path: str,
        source_path: str,
        output_path: str,
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        additional_args: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Run YOLO prediction on images.
        
        Args:
            model_path: Path to the YOLO model weights
            source_path: Path to input images
            output_path: Path for output results
            conf_threshold: Confidence threshold
            iou_threshold: IOU threshold for NMS
            additional_args: Additional command line arguments
            
        Returns:
            Dictionary containing prediction results and metadata
        """
        try:
            # Build command
            cmd = [
                "python",
                str(self.yolo_project_path / self.predict_script),
                "--weights", model_path,
                "--source", source_path,
                "--output", output_path,
                "--conf-thres", str(conf_threshold),
                "--iou-thres", str(iou_threshold),
                "--save-txt",
                "--save-conf",
            ]
            
            # Add additional arguments
            if additional_args:
                for key, value in additional_args.items():
                    cmd.extend([f"--{key}", str(value)])
            
            logger.info(f"Running YOLO predict: {' '.join(cmd)}")
            
            # Run process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.yolo_project_path)
            )
            
            # Wait for completion with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=settings.job_timeout_seconds
            )
            
            # Check return code
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8')
                logger.error(f"YOLO predict failed: {error_msg}")
                raise RuntimeError(f"YOLO predict failed: {error_msg}")
            
            output_text = stdout.decode('utf-8')
            logger.info("YOLO predict completed successfully")
            
            return {
                "status": "success",
                "output_path": output_path,
                "stdout": output_text,
                "stderr": stderr.decode('utf-8'),
            }
            
        except asyncio.TimeoutError:
            logger.error("YOLO predict timed out")
            raise RuntimeError("YOLO predict timed out")
        except Exception as e:
            logger.error(f"Failed to run YOLO predict: {e}", exc_info=True)
            raise

    async def run_yolo_train(
        self,
        data_yaml_path: str,
        model_config: str = "yolov5s.yaml",
        epochs: int = 100,
        batch_size: int = 16,
        img_size: int = 640,
        weights: Optional[str] = None,
        additional_args: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Run YOLO training.
        
        Args:
            data_yaml_path: Path to data.yaml configuration
            model_config: Model configuration file or name
            epochs: Number of training epochs
            batch_size: Batch size
            img_size: Input image size
            weights: Pre-trained weights path (optional)
            additional_args: Additional command line arguments
            
        Returns:
            Dictionary containing training results and metadata
        """
        try:
            # Build command
            cmd = [
                "python",
                str(self.yolo_project_path / self.train_script),
                "--data", data_yaml_path,
                "--cfg", model_config,
                "--epochs", str(epochs),
                "--batch-size", str(batch_size),
                "--img-size", str(img_size),
                "--cache",
            ]
            
            # Add pre-trained weights if specified
            if weights:
                cmd.extend(["--weights", weights])
            
            # Add additional arguments
            if additional_args:
                for key, value in additional_args.items():
                    cmd.extend([f"--{key}", str(value)])
            
            logger.info(f"Running YOLO train: {' '.join(cmd)}")
            
            # Run process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.yolo_project_path)
            )
            
            # Wait for completion with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=settings.job_timeout_seconds
            )
            
            # Check return code
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8')
                logger.error(f"YOLO train failed: {error_msg}")
                raise RuntimeError(f"YOLO train failed: {error_msg}")
            
            output_text = stdout.decode('utf-8')
            logger.info("YOLO train completed successfully")
            
            return {
                "status": "success",
                "stdout": output_text,
                "stderr": stderr.decode('utf-8'),
            }
            
        except asyncio.TimeoutError:
            logger.error("YOLO train timed out")
            raise RuntimeError("YOLO train timed out")
        except Exception as e:
            logger.error(f"Failed to run YOLO train: {e}", exc_info=True)
            raise

    async def run_command(
        self,
        cmd: list[str],
        cwd: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> dict[str, Any]:
        """
        Run a generic command.
        
        Args:
            cmd: Command and arguments as list
            cwd: Working directory
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with command results
        """
        try:
            logger.info(f"Running command: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            timeout_val = timeout or settings.job_timeout_seconds
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout_val
            )
            
            return {
                "status": "success" if process.returncode == 0 else "error",
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8'),
            }
            
        except asyncio.TimeoutError:
            logger.error("Command timed out")
            raise RuntimeError("Command timed out")
        except Exception as e:
            logger.error(f"Failed to run command: {e}", exc_info=True)
            raise



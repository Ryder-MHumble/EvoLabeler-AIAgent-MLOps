"""
Inference Agent for running YOLO model predictions.

This agent is responsible for running inference on uploaded images
and evaluating prediction uncertainty for active learning.
"""

from typing import Any
from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.tools.subprocess_executor import SubprocessExecutor
from app.tools.supabase_client import SupabaseClient
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class InferenceAgent(BaseAgent):
    """
    Agent for model inference.
    
    This agent:
    1. Takes uploaded images from context
    2. Runs YOLO model prediction
    3. Evaluates prediction confidence/uncertainty
    4. Returns predictions and uncertainty metrics
    """

    def __init__(
        self,
        subprocess_executor: SubprocessExecutor,
        supabase_client: SupabaseClient
    ) -> None:
        """
        Initialize the Inference Agent.
        
        Args:
            subprocess_executor: Executor for running YOLO scripts
            supabase_client: Client for database operations
        """
        super().__init__(agent_name="InferenceAgent")
        self.subprocess_executor = subprocess_executor
        self.supabase_client = supabase_client

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute inference on uploaded images.
        
        Args:
            context: Must contain:
                - job_id: str
                - uploaded_images: list[str] - paths to uploaded images
                - model_path: str - path to YOLO model weights
                
        Returns:
            Dictionary containing:
                - predictions: list[dict] - prediction results
                - uncertainty_metrics: dict - uncertainty analysis
                - inference_completed: bool
        """
        self._log_execution_start()
        
        try:
            job_id = context["job_id"]
            uploaded_images = context.get("uploaded_images", [])
            model_path = context.get("model_path", "yolov5s.pt")
            
            if not uploaded_images:
                raise ValueError("No uploaded images found in context")
            
            logger.info(
                f"Running inference on {len(uploaded_images)} images",
                extra={"job_id": job_id, "num_images": len(uploaded_images)}
            )
            
            # Prepare paths
            source_path = context.get("upload_dir", "/tmp/uploads")
            output_path = f"/tmp/inference_results/{job_id}"
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            # Run YOLO prediction
            result = await self.subprocess_executor.run_yolo_predict(
                model_path=model_path,
                source_path=source_path,
                output_path=output_path,
                conf_threshold=0.25,
                iou_threshold=0.45,
            )
            
            # Parse predictions and calculate uncertainty
            predictions = await self._parse_predictions(output_path, job_id)
            uncertainty_metrics = self._calculate_uncertainty(predictions)
            
            # Store results in database
            for pred in predictions:
                await self.supabase_client.store_inference_results(
                    job_id=job_id,
                    image_path=pred["image_path"],
                    predictions=pred["detections"]
                )
            
            self._log_execution_end(f"Processed {len(predictions)} images")
            
            return {
                "predictions": predictions,
                "uncertainty_metrics": uncertainty_metrics,
                "inference_completed": True,
                "output_path": output_path,
            }
            
        except Exception as e:
            self._log_error(e)
            raise

    async def _parse_predictions(
        self,
        output_path: str,
        job_id: str
    ) -> list[dict[str, Any]]:
        """
        Parse YOLO prediction results.
        
        Args:
            output_path: Path to prediction output directory
            job_id: Job identifier
            
        Returns:
            List of prediction dictionaries
        """
        predictions = []
        output_dir = Path(output_path)
        
        # Look for label files (YOLO format)
        label_files = list(output_dir.glob("**/*.txt"))
        
        for label_file in label_files:
            detections = []
            
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 6:  # class x y w h conf
                        detection = {
                            "class_id": int(parts[0]),
                            "x": float(parts[1]),
                            "y": float(parts[2]),
                            "width": float(parts[3]),
                            "height": float(parts[4]),
                            "confidence": float(parts[5]) if len(parts) > 5 else 1.0,
                        }
                        detections.append(detection)
            
            predictions.append({
                "image_path": str(label_file.stem),
                "detections": detections,
                "num_detections": len(detections),
            })
        
        logger.info(f"Parsed {len(predictions)} prediction files")
        return predictions

    def _calculate_uncertainty(
        self,
        predictions: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Calculate uncertainty metrics for active learning.
        
        This implements a simple uncertainty estimation based on
        prediction confidence scores.
        
        Args:
            predictions: List of prediction dictionaries
            
        Returns:
            Dictionary with uncertainty metrics
        """
        total_detections = 0
        confidence_scores = []
        low_confidence_count = 0
        
        for pred in predictions:
            detections = pred.get("detections", [])
            total_detections += len(detections)
            
            for det in detections:
                conf = det.get("confidence", 0.0)
                confidence_scores.append(conf)
                
                if conf < 0.5:  # Low confidence threshold
                    low_confidence_count += 1
        
        if not confidence_scores:
            return {
                "mean_confidence": 0.0,
                "uncertainty_score": 1.0,
                "low_confidence_ratio": 1.0,
                "requires_more_data": True,
            }
        
        mean_conf = sum(confidence_scores) / len(confidence_scores)
        uncertainty_score = 1.0 - mean_conf
        low_conf_ratio = low_confidence_count / len(confidence_scores)
        
        return {
            "mean_confidence": mean_conf,
            "uncertainty_score": uncertainty_score,
            "low_confidence_ratio": low_conf_ratio,
            "total_detections": total_detections,
            "requires_more_data": uncertainty_score > 0.3 or low_conf_ratio > 0.3,
        }



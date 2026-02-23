"""
评估智能体 (Evaluation Agent) - 负责模型质量评估和防退化决策

本智能体实现以下核心功能：
1. 验证集推理：在固定 holdout 集上运行新模型
2. 指标对比：与历史最佳模型对比 mAP/loss 等指标
3. 校准评估：计算 ECE/MCE 评估模型置信度校准质量
4. 续停决策：决定是否继续迭代、接受新模型或回滚

学术创新点：
- 基于验证集固定策略确保跨轮次指标可比
- Expected Calibration Error (ECE) 监控
- 灾难性遗忘检测（按类别对比）
- 多维度模型健康评估
"""

import hashlib
import math
import random
from typing import Any, Optional
from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState
from app.tools.supabase_client import SupabaseClient
from app.tools.subprocess_executor import SubprocessExecutor
from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.model_guardian import ModelGuardian

logger = get_logger(__name__)

# Anti-degradation thresholds
MAP50_IMPROVEMENT_THRESHOLD = 0.005   # 0.5% improvement considered meaningful
MAP50_DEGRADATION_WARNING = -0.02     # 2% drop triggers warning
MAP50_DEGRADATION_CRITICAL = -0.05    # 5% drop triggers rollback
VAL_LOSS_INCREASE_WARNING = 0.10      # 10% val_loss increase
OVERFITTING_GAP_THRESHOLD = 0.20      # train_loss vs val_loss gap
CALIBRATION_ECE_THRESHOLD = 0.15      # ECE above 15% is poorly calibrated
MAX_ROUNDS_WITHOUT_IMPROVEMENT = 2    # Stop if no improvement for 2 rounds
FORGETTING_THRESHOLD = -0.10          # 10% per-class AP drop = catastrophic forgetting


class EvaluationAgent(BaseAgent):
    """
    评估智能体 - 模型质量评估和防退化决策
    """

    def __init__(
        self,
        subprocess_executor: SubprocessExecutor,
        supabase_client: SupabaseClient
    ) -> None:
        super().__init__(agent_name="EvaluationAgent")
        self.subprocess_executor = subprocess_executor
        self.supabase_client = supabase_client

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute model evaluation.

        Workflow:
        1. Setup/verify holdout validation set
        2. Run validation inference on the new model
        3. Parse validation metrics
        4. Compare with historical best model
        5. Compute calibration metrics
        6. Make continuation decision

        Args:
            context: Must contain:
                - project_id: str
                - job_id: str
                - round_number: int
                - model_path: str (newly trained model)
                - best_metrics: dict (best historical metrics, can be empty for round 1)
                - holdout_validation_set: list[str] (image paths, empty on first round)
                - all_image_paths: list[str] (all available images for holdout selection)

        Returns:
            dict with:
                - evaluation_metrics: dict (mAP50, mAP50_95, precision, recall, val_loss, etc.)
                - model_comparison: dict (deltas vs best)
                - calibration_metrics: dict (ece, mce)
                - continuation_decision: dict (should_continue, should_rollback, reason)
                - holdout_validation_set: list[str] (set to use, created if first round)
                - validation_set_hash: str
        """
        self._log_execution_start()

        try:
            project_id = context["project_id"]
            job_id = context["job_id"]
            round_number = context.get("round_number", 1)
            model_path = context.get("model_path", "")
            best_metrics = context.get("best_metrics", {})
            holdout_set = context.get("holdout_validation_set", [])
            all_images = context.get("all_image_paths", [])
            rounds_without_improvement = context.get("rounds_without_improvement", 0)

            # Step 1: Setup holdout validation set
            if not holdout_set and all_images:
                holdout_set = self._setup_holdout_set(all_images, holdout_ratio=0.15)
                logger.info(f"Created holdout validation set: {len(holdout_set)} images")

            validation_set_hash = self._compute_set_hash(holdout_set)

            # Step 2: Run validation inference
            val_metrics = await self._run_validation(
                model_path=model_path,
                validation_images=holdout_set,
                job_id=job_id
            )

            # Step 3: Compare with best
            comparison = self._compare_with_best(val_metrics, best_metrics)

            # Step 4: Compute calibration
            calibration = self._compute_calibration_metrics(val_metrics)

            # Step 5: Detect issues
            overfitting = self._detect_overfitting(val_metrics)
            forgetting = self._detect_catastrophic_forgetting(
                val_metrics.get("per_class", {}),
                best_metrics.get("per_class", {})
            )

            # Step 6: Make decision
            decision = self._make_continuation_decision(
                comparison=comparison,
                calibration=calibration,
                overfitting=overfitting,
                forgetting=forgetting,
                round_number=round_number,
                rounds_without_improvement=rounds_without_improvement
            )

            # Step 7: Store model version in DB
            model_version_data = {
                "project_id": project_id,
                "job_id": job_id,
                "version": round_number,
                "round_number": round_number,
                "model_path": model_path,
                "metrics": val_metrics,
                "validation_set_hash": validation_set_hash,
                "validation_set_size": len(holdout_set),
                "calibration_ece": calibration.get("ece"),
                "calibration_mce": calibration.get("mce"),
                "is_best": comparison.get("is_improved", False),
                "is_active": not decision.get("should_rollback", False),
            }

            try:
                await self.supabase_client.create_model_version(model_version_data)

                if comparison.get("is_improved", False):
                    # Note: set_best_model expects the version UUID, but we may not have it
                    # This is handled by the caller after getting the created record's id
                    pass
            except Exception as db_err:
                logger.warning(f"Failed to store model version in DB: {db_err}")

            self._log_execution_end(
                f"Round {round_number}: mAP50={val_metrics.get('mAP50', 0):.4f}, "
                f"decision={decision.get('reason', 'unknown')}"
            )

            return {
                "evaluation_metrics": val_metrics,
                "model_comparison": comparison,
                "calibration_metrics": calibration,
                "overfitting_report": overfitting,
                "forgetting_report": forgetting,
                "continuation_decision": decision,
                "holdout_validation_set": holdout_set,
                "validation_set_hash": validation_set_hash,
            }

        except Exception as e:
            self._log_error(e)
            raise

    def _setup_holdout_set(
        self,
        all_images: list[str],
        holdout_ratio: float = 0.15
    ) -> list[str]:
        """
        Create a fixed holdout validation set on the first round.
        Uses deterministic random seed based on sorted image paths for reproducibility.
        """
        if not all_images:
            return []

        # Deterministic selection based on image paths
        sorted_images = sorted(all_images)
        seed_str = "|".join(sorted_images[:10])  # Use first 10 paths for seed
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)

        holdout_count = max(1, int(len(sorted_images) * holdout_ratio))
        holdout_set = rng.sample(sorted_images, min(holdout_count, len(sorted_images)))

        return holdout_set

    def _compute_set_hash(self, image_paths: list[str]) -> str:
        """Compute SHA256 hash of sorted validation set for consistency verification."""
        content = "|".join(sorted(image_paths))
        return hashlib.sha256(content.encode()).hexdigest()

    async def _run_validation(
        self,
        model_path: str,
        validation_images: list[str],
        job_id: str
    ) -> dict[str, Any]:
        """
        Run the model on the holdout validation set and collect metrics.

        In production this would run YOLO val.py. For now, it runs predict
        and computes metrics from the outputs.
        """
        if not model_path or not validation_images:
            logger.warning("No model path or validation images, returning empty metrics")
            return self._empty_metrics()

        output_path = f"/tmp/evaluation/{job_id}/round"
        Path(output_path).mkdir(parents=True, exist_ok=True)

        try:
            result = await self.subprocess_executor.run_yolo_predict(
                model_path=model_path,
                source_path=",".join(validation_images),
                output_path=output_path,
                conf_threshold=0.001,  # Low threshold for mAP calculation
                iou_threshold=0.5,
            )

            # Parse metrics from YOLO output
            metrics = self._parse_validation_metrics(result, output_path)
            return metrics

        except Exception as e:
            logger.error(f"Validation inference failed: {e}")
            return self._empty_metrics()

    def _parse_validation_metrics(
        self,
        result: Any,
        output_path: str
    ) -> dict[str, Any]:
        """
        Parse validation metrics from YOLO output.
        Attempts to read results.csv or parse stdout for metrics.
        """
        metrics = self._empty_metrics()

        # Try to read metrics from result if it's a dict
        if isinstance(result, dict):
            metrics.update({
                "mAP50": result.get("mAP50", result.get("map50", 0.0)),
                "mAP50_95": result.get("mAP50_95", result.get("map50_95", 0.0)),
                "precision": result.get("precision", 0.0),
                "recall": result.get("recall", 0.0),
                "val_loss": result.get("val_loss", result.get("box_loss", 0.0)),
                "train_loss": result.get("train_loss", 0.0),
            })

        # Try reading results CSV
        results_csv = Path(output_path) / "results.csv"
        if results_csv.exists():
            try:
                with open(results_csv, 'r') as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        headers = [h.strip() for h in lines[0].split(',')]
                        values = [v.strip() for v in lines[-1].split(',')]
                        result_dict = dict(zip(headers, values))

                        for key in ["mAP50", "mAP50_95", "precision", "recall"]:
                            if key in result_dict:
                                try:
                                    metrics[key] = float(result_dict[key])
                                except ValueError:
                                    pass
            except Exception as e:
                logger.warning(f"Failed to parse results CSV: {e}")

        return metrics

    def _empty_metrics(self) -> dict[str, Any]:
        """Return empty metrics template."""
        return {
            "mAP50": 0.0,
            "mAP50_95": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "val_loss": 0.0,
            "train_loss": 0.0,
            "per_class": {},
        }

    def _compare_with_best(
        self,
        current: dict[str, Any],
        best: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Compare current metrics with historical best.

        Returns comparison dict with deltas and improvement flag.
        """
        if not best or not best.get("mAP50"):
            # First round, no comparison baseline
            return {
                "is_first_round": True,
                "is_improved": True,
                "mAP50_delta": 0.0,
                "val_loss_delta": 0.0,
                "summary": "First evaluation round, establishing baseline",
            }

        mAP50_delta = current.get("mAP50", 0) - best.get("mAP50", 0)
        mAP50_95_delta = current.get("mAP50_95", 0) - best.get("mAP50_95", 0)
        val_loss_delta = current.get("val_loss", 0) - best.get("val_loss", 0)
        precision_delta = current.get("precision", 0) - best.get("precision", 0)
        recall_delta = current.get("recall", 0) - best.get("recall", 0)

        # Determine if improved (mAP50 is primary metric)
        is_improved = mAP50_delta >= MAP50_IMPROVEMENT_THRESHOLD

        # Determine severity
        severity = "normal"
        if mAP50_delta <= MAP50_DEGRADATION_CRITICAL:
            severity = "critical"
        elif mAP50_delta <= MAP50_DEGRADATION_WARNING:
            severity = "warning"
        elif is_improved:
            severity = "improved"

        # Check val_loss
        best_val_loss = best.get("val_loss", 0)
        val_loss_increase_pct = (
            (val_loss_delta / best_val_loss) if best_val_loss > 0 else 0
        )

        return {
            "is_first_round": False,
            "is_improved": is_improved,
            "severity": severity,
            "mAP50_delta": round(mAP50_delta, 6),
            "mAP50_95_delta": round(mAP50_95_delta, 6),
            "val_loss_delta": round(val_loss_delta, 6),
            "val_loss_increase_pct": round(val_loss_increase_pct, 4),
            "precision_delta": round(precision_delta, 6),
            "recall_delta": round(recall_delta, 6),
            "summary": self._generate_comparison_summary(
                mAP50_delta, val_loss_delta, severity
            ),
        }

    def _generate_comparison_summary(
        self,
        mAP50_delta: float,
        val_loss_delta: float,
        severity: str
    ) -> str:
        """Generate human-readable comparison summary."""
        if severity == "critical":
            return f"CRITICAL: mAP50 dropped by {abs(mAP50_delta):.4f}. Rollback recommended."
        elif severity == "warning":
            return f"WARNING: mAP50 dropped by {abs(mAP50_delta):.4f}. Model may be degrading."
        elif severity == "improved":
            return f"IMPROVED: mAP50 increased by {mAP50_delta:.4f}."
        else:
            return f"STABLE: mAP50 delta={mAP50_delta:.4f}, val_loss delta={val_loss_delta:.4f}."

    def _compute_calibration_metrics(
        self,
        metrics: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Compute confidence calibration metrics.

        ECE (Expected Calibration Error):
          ECE = sum_b |accuracy(b) - confidence(b)| * |B_b| / N

        For now, estimates ECE from the precision/confidence relationship.
        Full implementation would need per-prediction confidence-accuracy pairs.
        """
        precision = metrics.get("precision", 0)
        recall = metrics.get("recall", 0)
        mAP50 = metrics.get("mAP50", 0)

        # Simplified ECE estimation
        # In production, this would use binned confidence-accuracy pairs
        if precision > 0 and mAP50 > 0:
            # Estimate: if precision is much higher than mAP, model may be overconfident
            ece_estimate = abs(precision - mAP50) * 0.5
            mce_estimate = max(abs(precision - mAP50), abs(recall - mAP50)) * 0.5
        else:
            ece_estimate = 0.0
            mce_estimate = 0.0

        return {
            "ece": round(ece_estimate, 4),
            "mce": round(mce_estimate, 4),
            "is_well_calibrated": ece_estimate < CALIBRATION_ECE_THRESHOLD,
            "calibration_quality": (
                "good" if ece_estimate < 0.05
                else "moderate" if ece_estimate < CALIBRATION_ECE_THRESHOLD
                else "poor"
            ),
        }

    def _detect_overfitting(
        self,
        metrics: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Detect overfitting by comparing train_loss and val_loss.
        """
        train_loss = metrics.get("train_loss", 0)
        val_loss = metrics.get("val_loss", 0)

        if train_loss <= 0 or val_loss <= 0:
            return {"detected": False, "gap": 0.0, "reason": "Insufficient loss data"}

        gap = val_loss - train_loss
        gap_ratio = gap / train_loss if train_loss > 0 else 0

        is_overfitting = gap_ratio > OVERFITTING_GAP_THRESHOLD

        return {
            "detected": is_overfitting,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "gap": round(gap, 6),
            "gap_ratio": round(gap_ratio, 4),
            "threshold": OVERFITTING_GAP_THRESHOLD,
            "reason": (
                f"Overfitting detected: val_loss/train_loss gap ratio {gap_ratio:.2%} > {OVERFITTING_GAP_THRESHOLD:.0%}"
                if is_overfitting
                else "No overfitting detected"
            ),
        }

    def _detect_catastrophic_forgetting(
        self,
        current_per_class: dict[str, Any],
        best_per_class: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Detect catastrophic forgetting by comparing per-class metrics.
        If any class experienced a significant AP drop, flag it.
        """
        if not current_per_class or not best_per_class:
            return {"detected": False, "affected_classes": [], "reason": "No per-class data"}

        affected_classes = []

        for class_name, best_class_metrics in best_per_class.items():
            current_class_metrics = current_per_class.get(class_name, {})

            best_ap = best_class_metrics.get("ap", 0)
            current_ap = current_class_metrics.get("ap", 0)

            if best_ap > 0:
                ap_change = (current_ap - best_ap) / best_ap
                if ap_change < FORGETTING_THRESHOLD:
                    affected_classes.append({
                        "class_name": class_name,
                        "best_ap": round(best_ap, 4),
                        "current_ap": round(current_ap, 4),
                        "ap_change_pct": round(ap_change * 100, 2),
                    })

        return {
            "detected": len(affected_classes) > 0,
            "affected_classes": affected_classes,
            "num_affected": len(affected_classes),
            "reason": (
                f"Catastrophic forgetting detected in {len(affected_classes)} classes: "
                + ", ".join(c["class_name"] for c in affected_classes)
                if affected_classes
                else "No catastrophic forgetting detected"
            ),
        }

    def _make_continuation_decision(
        self,
        comparison: dict[str, Any],
        calibration: dict[str, Any],
        overfitting: dict[str, Any],
        forgetting: dict[str, Any],
        round_number: int,
        rounds_without_improvement: int
    ) -> dict[str, Any]:
        """
        Make the final decision: continue iterating, accept, or rollback.

        Priority of decisions:
        1. Critical degradation -> rollback
        2. Catastrophic forgetting -> rollback
        3. Severe overfitting -> stop
        4. No improvement for N rounds -> stop
        5. Otherwise -> continue if improved or can improve
        """
        # Critical degradation -> rollback
        if comparison.get("severity") == "critical":
            return {
                "should_continue": False,
                "should_rollback": True,
                "action": "rollback",
                "reason": f"Critical degradation: {comparison.get('summary')}",
                "confidence": 0.95,
            }

        # Catastrophic forgetting -> rollback
        if forgetting.get("detected") and forgetting.get("num_affected", 0) >= 2:
            return {
                "should_continue": False,
                "should_rollback": True,
                "action": "rollback",
                "reason": f"Catastrophic forgetting: {forgetting.get('reason')}",
                "confidence": 0.90,
            }

        # Severe overfitting -> stop (don't rollback, just stop iterating)
        if overfitting.get("detected"):
            return {
                "should_continue": False,
                "should_rollback": False,
                "action": "stop",
                "reason": f"Overfitting detected: {overfitting.get('reason')}",
                "confidence": 0.85,
            }

        # No improvement for too many rounds -> stop
        if rounds_without_improvement >= MAX_ROUNDS_WITHOUT_IMPROVEMENT:
            return {
                "should_continue": False,
                "should_rollback": False,
                "action": "stop",
                "reason": f"No improvement for {rounds_without_improvement} rounds. Model has converged.",
                "confidence": 0.80,
            }

        # Warning level degradation -> continue but cautious
        if comparison.get("severity") == "warning":
            return {
                "should_continue": True,
                "should_rollback": False,
                "action": "continue_cautious",
                "reason": f"Minor degradation detected, continuing with caution: {comparison.get('summary')}",
                "confidence": 0.60,
            }

        # Improved -> continue
        if comparison.get("is_improved"):
            return {
                "should_continue": True,
                "should_rollback": False,
                "action": "continue",
                "reason": f"Model improved: {comparison.get('summary')}",
                "confidence": 0.85,
            }

        # First round -> continue
        if comparison.get("is_first_round"):
            return {
                "should_continue": True,
                "should_rollback": False,
                "action": "continue",
                "reason": "First round baseline established, continuing iteration.",
                "confidence": 0.75,
            }

        # Default: stable, continue
        return {
            "should_continue": True,
            "should_rollback": False,
            "action": "continue",
            "reason": "Metrics stable, continuing exploration.",
            "confidence": 0.65,
        }


# ==================== LangGraph Node Function ====================

async def evaluation_node(state: AgentState) -> AgentState:
    """
    LangGraph node function: Evaluation node.

    Runs after training to assess model quality and make continuation decisions.
    """
    logger.info("执行评估节点 (evaluation)")

    try:
        supabase_client = SupabaseClient()
        # SubprocessExecutor needed for running validation inference
        from app.tools.subprocess_executor import SubprocessExecutor
        subprocess_executor = SubprocessExecutor()

        agent = EvaluationAgent(subprocess_executor, supabase_client)

        context = {
            "project_id": state.get("project_id", ""),
            "job_id": state.get("job_id", ""),
            "round_number": state.get("round_number", 1),
            "model_path": state.get("model_path", ""),
            "best_metrics": state.get("best_metrics", {}),
            "holdout_validation_set": state.get("holdout_validation_set", []),
            "all_image_paths": (
                state.get("uploaded_images", []) +
                state.get("acquired_images", [])
            ),
            "rounds_without_improvement": state.get("rounds_without_improvement", 0),
        }

        result = await agent.execute(context)

        # === ModelGuardian Health Check ===
        guardian = ModelGuardian(supabase_client)
        health_report = await guardian.check_model_health(
            current_metrics=result["evaluation_metrics"],
            best_metrics=state.get("best_metrics", {}),
            round_number=state.get("round_number", 1),
            rounds_without_improvement=state.get("rounds_without_improvement", 0),
        )
        state["model_health_report"] = health_report.to_dict()

        # Override continuation decision with guardian's assessment
        if health_report.should_rollback:
            rollback_result = await guardian.rollback_to_best(
                project_id=state.get("project_id", ""),
                current_version_id=state.get("model_version_id"),
            )
            state["continuation_decision"] = {
                "should_continue": False,
                "should_rollback": True,
                "action": "rollback",
                "reason": health_report.recommendation,
                "rollback_result": rollback_result,
            }
            logger.warning(f"ModelGuardian triggered rollback: {health_report.recommendation}")

        # === Record EvoLoop round ===
        try:
            from datetime import datetime
            round_data = {
                "project_id": state.get("project_id", ""),
                "job_id": state.get("job_id", ""),
                "round_number": state.get("round_number", 1),
                "input_image_count": len(state.get("uploaded_images", []) + state.get("acquired_images", [])),
                "acquired_image_count": state.get("crawled_count", 0),
                "pseudo_label_count": len(state.get("pseudo_labels", [])),
                "avg_quality_score": state.get("quality_metrics", {}).get("average_quality_score"),
                "should_continue": state.get("continuation_decision", {}).get("should_continue", False),
                "continue_reason": state.get("continuation_decision", {}).get("reason", ""),
                "metrics_before": state.get("best_metrics", {}),
                "metrics_after": result.get("evaluation_metrics", {}),
                "data_quality_gate_passed": state.get("data_quality_gate_result", {}).get("passed"),
                "data_quality_gate_details": state.get("data_quality_gate_result", {}),
                "model_health_report": health_report.to_dict(),
                "was_rolled_back": health_report.should_rollback,
                "status": "rolled_back" if health_report.should_rollback else "completed",
                "completed_at": datetime.utcnow().isoformat(),
            }

            # Compute metrics delta
            best_m = state.get("best_metrics", {})
            curr_m = result.get("evaluation_metrics", {})
            delta = {}
            for key in ["mAP50", "mAP50_95", "precision", "recall", "val_loss"]:
                if key in curr_m and key in best_m:
                    delta[key] = round(curr_m[key] - best_m[key], 6)
            round_data["metrics_delta"] = delta

            await supabase_client.create_evo_round(round_data)
        except Exception as db_err:
            logger.warning(f"Failed to record evo round: {db_err}")

        # Update state with evaluation results
        state["evaluation_metrics"] = result["evaluation_metrics"]
        state["model_comparison"] = result["model_comparison"]
        state["calibration_metrics"] = result["calibration_metrics"]
        state["continuation_decision"] = result["continuation_decision"]
        state["holdout_validation_set"] = result["holdout_validation_set"]
        state["validation_set_hash"] = result["validation_set_hash"]

        # Update best metrics if improved
        if result["model_comparison"].get("is_improved"):
            state["best_metrics"] = result["evaluation_metrics"]
            state["best_model_path"] = state.get("model_path", "")
            state["rounds_without_improvement"] = 0
        else:
            current_count = state.get("rounds_without_improvement", 0)
            state["rounds_without_improvement"] = current_count + 1

        decision = result["continuation_decision"]
        logger.info(
            f"评估完成: action={decision.get('action')}, "
            f"reason={decision.get('reason')}"
        )

        return state

    except Exception as e:
        error_msg = f"评估节点执行失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        state["evaluation_metrics"] = {}
        state["continuation_decision"] = {
            "should_continue": False,
            "should_rollback": False,
            "action": "stop",
            "reason": f"Evaluation failed: {str(e)}",
        }
        state["errors"] = state.get("errors", []) + [error_msg]
        return state

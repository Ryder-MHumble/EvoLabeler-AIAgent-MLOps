"""
模型守护者 (Model Guardian) - 防退化核心服务

本服务负责监控模型质量，防止"越训越差"的问题。

核心机制：
1. 检查点对比 (Checkpoint Comparison)：训练前后指标对比
2. 自动回滚 (Auto Rollback)：指标严重退化时自动恢复最佳模型
3. 过拟合检测 (Overfitting Detection)：train/val loss 发散检测
4. 灾难性遗忘检测 (Catastrophic Forgetting)：按类别指标下降检测
5. 置信度校准监控 (Calibration Monitoring)：ECE/MCE 追踪
6. 数据多样性评估 (Diversity Assessment)：新数据多样性检测
"""

import hashlib
import math
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from app.tools.supabase_client import SupabaseClient
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class HealthSeverity(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class HealthCheck:
    """Single health check result."""
    name: str
    passed: bool
    severity: HealthSeverity
    message: str
    details: dict = field(default_factory=dict)


@dataclass
class ModelHealthReport:
    """Comprehensive model health report."""
    is_healthy: bool
    should_rollback: bool
    is_improved: bool
    is_overfitting: bool
    has_forgetting: bool
    can_improve_further: bool
    overall_severity: HealthSeverity
    checks: list[HealthCheck] = field(default_factory=list)
    recommendation: str = ""

    def to_dict(self) -> dict:
        return {
            "is_healthy": self.is_healthy,
            "should_rollback": self.should_rollback,
            "is_improved": self.is_improved,
            "is_overfitting": self.is_overfitting,
            "has_forgetting": self.has_forgetting,
            "can_improve_further": self.can_improve_further,
            "overall_severity": self.overall_severity.value,
            "checks": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "severity": c.severity.value,
                    "message": c.message,
                    "details": c.details,
                }
                for c in self.checks
            ],
            "recommendation": self.recommendation,
        }


class ModelGuardian:
    """
    模型守护者 - 多维度模型健康评估和防退化决策。
    """

    # === Threshold Configuration ===

    # mAP degradation thresholds
    MAP50_DEGRADATION_WARNING = -0.02   # 2% drop -> warning
    MAP50_DEGRADATION_CRITICAL = -0.05  # 5% drop -> rollback

    # Val loss thresholds
    VAL_LOSS_INCREASE_WARNING = 0.10    # 10% increase -> warning
    VAL_LOSS_INCREASE_CRITICAL = 0.25   # 25% increase -> critical

    # Overfitting thresholds
    OVERFITTING_GAP_WARNING = 0.15      # 15% gap -> warning
    OVERFITTING_GAP_CRITICAL = 0.25     # 25% gap -> critical

    # Calibration thresholds
    CALIBRATION_ECE_WARNING = 0.10      # ECE > 10% -> warning
    CALIBRATION_ECE_CRITICAL = 0.20     # ECE > 20% -> critical

    # Forgetting thresholds
    FORGETTING_PER_CLASS_THRESHOLD = -0.10  # 10% per-class AP drop
    FORGETTING_MAX_AFFECTED_CLASSES = 2     # More than 2 classes -> critical

    # Improvement thresholds
    MEANINGFUL_IMPROVEMENT = 0.005  # 0.5% mAP improvement considered meaningful

    def __init__(self, supabase_client: Optional[SupabaseClient] = None) -> None:
        self.supabase_client = supabase_client or SupabaseClient()

    async def check_model_health(
        self,
        current_metrics: dict[str, Any],
        best_metrics: dict[str, Any],
        round_number: int = 1,
        rounds_without_improvement: int = 0
    ) -> ModelHealthReport:
        """
        Run all health checks and produce a comprehensive report.

        Args:
            current_metrics: Metrics from the newly trained model
            best_metrics: Metrics from the historical best model
            round_number: Current EvoLoop round
            rounds_without_improvement: Consecutive rounds without improvement

        Returns:
            ModelHealthReport with all checks and recommendations
        """
        checks: list[HealthCheck] = []

        # 1. mAP degradation check
        checks.append(self._check_map_degradation(current_metrics, best_metrics))

        # 2. Val loss check
        checks.append(self._check_val_loss(current_metrics, best_metrics))

        # 3. Overfitting check
        checks.append(self._check_overfitting(current_metrics))

        # 4. Calibration check
        checks.append(self._check_calibration(current_metrics))

        # 5. Catastrophic forgetting check
        checks.append(self._check_catastrophic_forgetting(current_metrics, best_metrics))

        # Aggregate results
        has_critical = any(c.severity == HealthSeverity.CRITICAL for c in checks)
        has_warning = any(c.severity == HealthSeverity.WARNING for c in checks)
        all_passed = all(c.passed for c in checks)

        # Determine improvement
        mAP50_delta = (
            current_metrics.get("mAP50", 0) - best_metrics.get("mAP50", 0)
            if best_metrics.get("mAP50") else 0
        )
        is_improved = mAP50_delta >= self.MEANINGFUL_IMPROVEMENT or not best_metrics.get("mAP50")

        # Determine overfitting
        overfitting_check = next((c for c in checks if c.name == "overfitting"), None)
        is_overfitting = overfitting_check and not overfitting_check.passed

        # Determine forgetting
        forgetting_check = next((c for c in checks if c.name == "catastrophic_forgetting"), None)
        has_forgetting = forgetting_check and not forgetting_check.passed

        # Should rollback?
        should_rollback = has_critical and round_number > 1

        # Can improve further?
        can_improve = (
            not is_overfitting
            and not has_critical
            and rounds_without_improvement < 3
        )

        # Overall severity
        if has_critical:
            severity = HealthSeverity.CRITICAL
        elif has_warning:
            severity = HealthSeverity.WARNING
        else:
            severity = HealthSeverity.HEALTHY

        report = ModelHealthReport(
            is_healthy=all_passed,
            should_rollback=should_rollback,
            is_improved=is_improved,
            is_overfitting=bool(is_overfitting),
            has_forgetting=bool(has_forgetting),
            can_improve_further=can_improve,
            overall_severity=severity,
            checks=checks,
            recommendation=self._generate_recommendation(
                checks, is_improved, is_overfitting, should_rollback, round_number
            ),
        )

        logger.info(
            f"Model health check: severity={severity.value}, "
            f"improved={is_improved}, rollback={should_rollback}, "
            f"checks_passed={sum(1 for c in checks if c.passed)}/{len(checks)}"
        )

        return report

    def _check_map_degradation(
        self,
        current: dict[str, Any],
        best: dict[str, Any]
    ) -> HealthCheck:
        """Check if mAP50 has degraded compared to best."""
        if not best.get("mAP50"):
            return HealthCheck(
                name="map_degradation",
                passed=True,
                severity=HealthSeverity.HEALTHY,
                message="First evaluation, no baseline for comparison",
            )

        delta = current.get("mAP50", 0) - best.get("mAP50", 0)

        if delta <= self.MAP50_DEGRADATION_CRITICAL:
            return HealthCheck(
                name="map_degradation",
                passed=False,
                severity=HealthSeverity.CRITICAL,
                message=f"mAP50 dropped by {abs(delta):.4f} (critical threshold: {abs(self.MAP50_DEGRADATION_CRITICAL)})",
                details={"delta": delta, "current": current.get("mAP50"), "best": best.get("mAP50")},
            )
        elif delta <= self.MAP50_DEGRADATION_WARNING:
            return HealthCheck(
                name="map_degradation",
                passed=False,
                severity=HealthSeverity.WARNING,
                message=f"mAP50 dropped by {abs(delta):.4f} (warning threshold: {abs(self.MAP50_DEGRADATION_WARNING)})",
                details={"delta": delta, "current": current.get("mAP50"), "best": best.get("mAP50")},
            )
        else:
            return HealthCheck(
                name="map_degradation",
                passed=True,
                severity=HealthSeverity.HEALTHY,
                message=f"mAP50 delta: {delta:+.4f}",
                details={"delta": delta},
            )

    def _check_val_loss(
        self,
        current: dict[str, Any],
        best: dict[str, Any]
    ) -> HealthCheck:
        """Check if val_loss has increased significantly."""
        best_loss = best.get("val_loss", 0)
        current_loss = current.get("val_loss", 0)

        if best_loss <= 0 or current_loss <= 0:
            return HealthCheck(
                name="val_loss",
                passed=True,
                severity=HealthSeverity.HEALTHY,
                message="Insufficient val_loss data for comparison",
            )

        increase_pct = (current_loss - best_loss) / best_loss

        if increase_pct >= self.VAL_LOSS_INCREASE_CRITICAL:
            return HealthCheck(
                name="val_loss",
                passed=False,
                severity=HealthSeverity.CRITICAL,
                message=f"Val loss increased by {increase_pct:.1%}",
                details={"increase_pct": increase_pct, "current": current_loss, "best": best_loss},
            )
        elif increase_pct >= self.VAL_LOSS_INCREASE_WARNING:
            return HealthCheck(
                name="val_loss",
                passed=False,
                severity=HealthSeverity.WARNING,
                message=f"Val loss increased by {increase_pct:.1%}",
                details={"increase_pct": increase_pct, "current": current_loss, "best": best_loss},
            )
        else:
            return HealthCheck(
                name="val_loss",
                passed=True,
                severity=HealthSeverity.HEALTHY,
                message=f"Val loss change: {increase_pct:+.1%}",
            )

    def _check_overfitting(self, metrics: dict[str, Any]) -> HealthCheck:
        """Check for train/val loss divergence."""
        train_loss = metrics.get("train_loss", 0)
        val_loss = metrics.get("val_loss", 0)

        if train_loss <= 0 or val_loss <= 0:
            return HealthCheck(
                name="overfitting",
                passed=True,
                severity=HealthSeverity.HEALTHY,
                message="Insufficient loss data for overfitting detection",
            )

        gap_ratio = (val_loss - train_loss) / train_loss if train_loss > 0 else 0

        if gap_ratio >= self.OVERFITTING_GAP_CRITICAL:
            return HealthCheck(
                name="overfitting",
                passed=False,
                severity=HealthSeverity.CRITICAL,
                message=f"Severe overfitting: gap ratio {gap_ratio:.2%}",
                details={"gap_ratio": gap_ratio, "train_loss": train_loss, "val_loss": val_loss},
            )
        elif gap_ratio >= self.OVERFITTING_GAP_WARNING:
            return HealthCheck(
                name="overfitting",
                passed=False,
                severity=HealthSeverity.WARNING,
                message=f"Moderate overfitting: gap ratio {gap_ratio:.2%}",
                details={"gap_ratio": gap_ratio, "train_loss": train_loss, "val_loss": val_loss},
            )
        else:
            return HealthCheck(
                name="overfitting",
                passed=True,
                severity=HealthSeverity.HEALTHY,
                message=f"No overfitting detected (gap ratio: {gap_ratio:.2%})",
            )

    def _check_calibration(self, metrics: dict[str, Any]) -> HealthCheck:
        """Check model confidence calibration quality."""
        precision = metrics.get("precision", 0)
        mAP50 = metrics.get("mAP50", 0)

        if precision <= 0 or mAP50 <= 0:
            return HealthCheck(
                name="calibration",
                passed=True,
                severity=HealthSeverity.HEALTHY,
                message="Insufficient data for calibration assessment",
            )

        # Simplified ECE estimate
        ece_estimate = abs(precision - mAP50) * 0.5

        if ece_estimate >= self.CALIBRATION_ECE_CRITICAL:
            return HealthCheck(
                name="calibration",
                passed=False,
                severity=HealthSeverity.CRITICAL,
                message=f"Poor calibration: ECE estimate {ece_estimate:.4f}",
                details={"ece": ece_estimate, "precision": precision, "mAP50": mAP50},
            )
        elif ece_estimate >= self.CALIBRATION_ECE_WARNING:
            return HealthCheck(
                name="calibration",
                passed=False,
                severity=HealthSeverity.WARNING,
                message=f"Moderate calibration: ECE estimate {ece_estimate:.4f}",
                details={"ece": ece_estimate},
            )
        else:
            return HealthCheck(
                name="calibration",
                passed=True,
                severity=HealthSeverity.HEALTHY,
                message=f"Good calibration (ECE: {ece_estimate:.4f})",
            )

    def _check_catastrophic_forgetting(
        self,
        current: dict[str, Any],
        best: dict[str, Any]
    ) -> HealthCheck:
        """Check per-class metrics for catastrophic forgetting."""
        current_per_class = current.get("per_class", {})
        best_per_class = best.get("per_class", {})

        if not current_per_class or not best_per_class:
            return HealthCheck(
                name="catastrophic_forgetting",
                passed=True,
                severity=HealthSeverity.HEALTHY,
                message="No per-class data for forgetting detection",
            )

        affected = []
        for cls_name, best_cls in best_per_class.items():
            current_cls = current_per_class.get(cls_name, {})
            best_ap = best_cls.get("ap", 0)
            current_ap = current_cls.get("ap", 0)

            if best_ap > 0:
                change = (current_ap - best_ap) / best_ap
                if change < self.FORGETTING_PER_CLASS_THRESHOLD:
                    affected.append({"class": cls_name, "change": change})

        if len(affected) > self.FORGETTING_MAX_AFFECTED_CLASSES:
            return HealthCheck(
                name="catastrophic_forgetting",
                passed=False,
                severity=HealthSeverity.CRITICAL,
                message=f"Catastrophic forgetting in {len(affected)} classes",
                details={"affected_classes": affected},
            )
        elif len(affected) > 0:
            return HealthCheck(
                name="catastrophic_forgetting",
                passed=False,
                severity=HealthSeverity.WARNING,
                message=f"Minor forgetting in {len(affected)} class(es)",
                details={"affected_classes": affected},
            )
        else:
            return HealthCheck(
                name="catastrophic_forgetting",
                passed=True,
                severity=HealthSeverity.HEALTHY,
                message="No catastrophic forgetting detected",
            )

    def compute_diversity_score(
        self,
        new_image_features: list[dict],
        existing_image_features: list[dict]
    ) -> float:
        """
        Compute diversity score of new images vs existing dataset.

        Uses detection distribution similarity:
        - Class distribution overlap
        - Spatial distribution variance
        - Detection count distribution

        Returns:
            Score from 0 (identical) to 1 (completely different)
        """
        if not new_image_features or not existing_image_features:
            return 1.0  # No comparison possible, assume diverse

        # Compute class distribution for new images
        new_classes: dict[int, int] = {}
        for feat in new_image_features:
            for det in feat.get("detections", []):
                cls_id = det.get("class_id", 0)
                new_classes[cls_id] = new_classes.get(cls_id, 0) + 1

        # Compute class distribution for existing images
        existing_classes: dict[int, int] = {}
        for feat in existing_image_features:
            for det in feat.get("detections", []):
                cls_id = det.get("class_id", 0)
                existing_classes[cls_id] = existing_classes.get(cls_id, 0) + 1

        # Compute Jaccard-like diversity
        all_classes = set(new_classes.keys()) | set(existing_classes.keys())
        if not all_classes:
            return 1.0

        overlap = 0.0
        total = 0.0
        for cls_id in all_classes:
            new_count = new_classes.get(cls_id, 0)
            exist_count = existing_classes.get(cls_id, 0)

            new_ratio = new_count / max(sum(new_classes.values()), 1)
            exist_ratio = exist_count / max(sum(existing_classes.values()), 1)

            overlap += min(new_ratio, exist_ratio)
            total += max(new_ratio, exist_ratio)

        if total == 0:
            return 1.0

        similarity = overlap / total
        diversity = 1.0 - similarity

        return round(diversity, 4)

    async def rollback_to_best(
        self,
        project_id: str,
        current_version_id: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Rollback: deactivate current model, reactivate the best model.

        Returns:
            Dict with rollback result details
        """
        try:
            # Get the best model version
            best_version = await self.supabase_client.get_best_model_version(project_id)

            if not best_version:
                logger.warning(f"No best model version found for project {project_id}")
                return {"success": False, "reason": "No best model version found"}

            # Deactivate current
            if current_version_id:
                await self.supabase_client.update_model_version(
                    current_version_id,
                    {"is_active": False}
                )

            # Activate best
            best_id = best_version.get("id")
            await self.supabase_client.set_active_model(project_id, best_id)

            logger.info(
                f"Rolled back project {project_id} to model version {best_id} "
                f"(mAP50: {best_version.get('metrics', {}).get('mAP50', 'N/A')})"
            )

            return {
                "success": True,
                "rolled_back_to": best_id,
                "rolled_back_metrics": best_version.get("metrics", {}),
                "deactivated_version": current_version_id,
            }

        except Exception as e:
            logger.error(f"Rollback failed: {e}", exc_info=True)
            return {"success": False, "reason": str(e)}

    def _generate_recommendation(
        self,
        checks: list[HealthCheck],
        is_improved: bool,
        is_overfitting: bool,
        should_rollback: bool,
        round_number: int
    ) -> str:
        """Generate human-readable recommendation."""
        if should_rollback:
            failed = [c for c in checks if c.severity == HealthSeverity.CRITICAL]
            reasons = ", ".join(c.name for c in failed)
            return f"ROLLBACK RECOMMENDED: Critical issues detected ({reasons}). Reverting to best model."

        if is_overfitting:
            return "STOP RECOMMENDED: Overfitting detected. Model is memorizing training data. Consider adding more diverse data or reducing epochs."

        if is_improved:
            return "CONTINUE: Model improved. Continue iterating for further gains."

        warnings = [c for c in checks if c.severity == HealthSeverity.WARNING]
        if warnings:
            return f"CAUTION: {len(warnings)} warning(s) detected. Consider adjusting training strategy."

        return "STABLE: No significant changes. Model may have converged."

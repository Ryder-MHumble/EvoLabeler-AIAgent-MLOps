"""
数据质量门禁 (Data Quality Gate) - 训练前数据质量检查

本服务在训练开始前对数据集进行多维度质量检查，
确保只有满足质量标准的数据才会被用于训练，防止低质量数据污染模型。

检查维度：
1. 样本数量 (Sample Count): 最小样本量要求
2. 伪标签质量 (Pseudo-label Quality): 平均质量分数阈值
3. 类别平衡 (Class Balance): 类别不平衡比阈值
4. 数据多样性 (Diversity): 新数据的多样性评分
5. 近重复检测 (Near-duplicate Detection): 重复数据比例阈值
"""

import hashlib
import math
from typing import Any, Optional
from dataclasses import dataclass, field
from collections import Counter

from app.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class GateCheck:
    """Single quality gate check result."""
    name: str
    passed: bool
    value: float
    threshold: float
    message: str


@dataclass
class GateResult:
    """Aggregate quality gate result."""
    passed: bool
    checks: list[GateCheck]
    failures: list[GateCheck]
    summary: str

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "summary": self.summary,
            "checks": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "value": round(c.value, 4),
                    "threshold": round(c.threshold, 4),
                    "message": c.message,
                }
                for c in self.checks
            ],
            "failures": [c.name for c in self.failures],
            "num_checks": len(self.checks),
            "num_passed": sum(1 for c in self.checks if c.passed),
        }


class DataQualityGate:
    """
    数据质量门禁 - 训练前强制质量检查。

    所有检查项必须全部通过才允许训练。
    任一检查失败将导致本轮训练被跳过，并记录失败原因。
    """

    # === Threshold Configuration ===
    MIN_SAMPLE_COUNT = 10              # Minimum samples to justify training
    MIN_QUALITY_SCORE = 0.4            # Minimum average pseudo-label quality
    MAX_CLASS_IMBALANCE_RATIO = 10.0   # Max ratio between most/least common class
    MIN_DIVERSITY_SCORE = 0.3          # Minimum diversity of new data
    MAX_DUPLICATE_RATIO = 0.20         # Maximum fraction of near-duplicates

    def check(
        self,
        pseudo_labels: list[dict[str, Any]],
        existing_labels: Optional[list[dict[str, Any]]] = None
    ) -> GateResult:
        """
        Run all data quality checks.

        Args:
            pseudo_labels: New pseudo-labeled data to validate
            existing_labels: Existing training data (for diversity comparison)

        Returns:
            GateResult with pass/fail status and detailed check results
        """
        checks: list[GateCheck] = []

        # 1. Sample count check
        checks.append(self._check_sample_count(pseudo_labels))

        # 2. Quality score check
        checks.append(self._check_quality_scores(pseudo_labels))

        # 3. Class balance check
        checks.append(self._check_class_balance(pseudo_labels))

        # 4. Diversity check
        checks.append(self._check_diversity(pseudo_labels, existing_labels))

        # 5. Near-duplicate check
        checks.append(self._check_duplicates(pseudo_labels))

        # Aggregate
        failures = [c for c in checks if not c.passed]
        passed = len(failures) == 0

        if passed:
            summary = f"All {len(checks)} quality checks passed. Data ready for training."
        else:
            failed_names = ", ".join(c.name for c in failures)
            summary = f"Quality gate FAILED: {len(failures)}/{len(checks)} checks failed ({failed_names}). Training skipped."

        result = GateResult(
            passed=passed,
            checks=checks,
            failures=failures,
            summary=summary,
        )

        logger.info(
            f"Data quality gate: {'PASSED' if passed else 'FAILED'} "
            f"({sum(1 for c in checks if c.passed)}/{len(checks)} checks passed)"
        )

        return result

    def _check_sample_count(
        self,
        labels: list[dict[str, Any]]
    ) -> GateCheck:
        """Check minimum sample count."""
        count = len(labels)
        passed = count >= self.MIN_SAMPLE_COUNT

        return GateCheck(
            name="sample_count",
            passed=passed,
            value=float(count),
            threshold=float(self.MIN_SAMPLE_COUNT),
            message=(
                f"Sample count: {count} (minimum: {self.MIN_SAMPLE_COUNT})"
                if passed
                else f"Insufficient samples: {count} < {self.MIN_SAMPLE_COUNT}. Need more data."
            ),
        )

    def _check_quality_scores(
        self,
        labels: list[dict[str, Any]]
    ) -> GateCheck:
        """Check average pseudo-label quality score."""
        quality_scores = [
            label.get("quality_score", 0.0) for label in labels
            if "quality_score" in label
        ]

        if not quality_scores:
            # No quality scores available, compute from confidence
            for label in labels:
                detections = label.get("detections", [])
                if detections:
                    avg_conf = sum(d.get("confidence", 0) for d in detections) / len(detections)
                    quality_scores.append(avg_conf)

        if not quality_scores:
            return GateCheck(
                name="quality_score",
                passed=True,
                value=0.0,
                threshold=self.MIN_QUALITY_SCORE,
                message="No quality data available, skipping check",
            )

        avg_quality = sum(quality_scores) / len(quality_scores)
        passed = avg_quality >= self.MIN_QUALITY_SCORE

        return GateCheck(
            name="quality_score",
            passed=passed,
            value=avg_quality,
            threshold=self.MIN_QUALITY_SCORE,
            message=(
                f"Average quality: {avg_quality:.4f} (minimum: {self.MIN_QUALITY_SCORE})"
                if passed
                else f"Low quality data: {avg_quality:.4f} < {self.MIN_QUALITY_SCORE}. Pseudo-labels are unreliable."
            ),
        )

    def _check_class_balance(
        self,
        labels: list[dict[str, Any]]
    ) -> GateCheck:
        """Check class distribution balance."""
        class_counts: Counter = Counter()

        for label in labels:
            for det in label.get("detections", []):
                class_id = det.get("class_id", 0)
                class_counts[class_id] += 1

        if len(class_counts) <= 1:
            return GateCheck(
                name="class_balance",
                passed=True,
                value=1.0,
                threshold=self.MAX_CLASS_IMBALANCE_RATIO,
                message="Single class or no class data, balance check N/A",
            )

        most_common = class_counts.most_common(1)[0][1]
        least_common = class_counts.most_common()[-1][1]

        if least_common == 0:
            ratio = float('inf')
        else:
            ratio = most_common / least_common

        passed = ratio <= self.MAX_CLASS_IMBALANCE_RATIO

        return GateCheck(
            name="class_balance",
            passed=passed,
            value=ratio,
            threshold=self.MAX_CLASS_IMBALANCE_RATIO,
            message=(
                f"Class imbalance ratio: {ratio:.1f}x (max: {self.MAX_CLASS_IMBALANCE_RATIO}x)"
                if passed
                else f"Severe class imbalance: {ratio:.1f}x > {self.MAX_CLASS_IMBALANCE_RATIO}x. "
                     f"Most common: {most_common}, least common: {least_common}."
            ),
        )

    def _check_diversity(
        self,
        new_labels: list[dict[str, Any]],
        existing_labels: Optional[list[dict[str, Any]]] = None
    ) -> GateCheck:
        """Check data diversity of new samples."""
        if not existing_labels:
            # No existing data to compare against, pass by default
            return GateCheck(
                name="diversity",
                passed=True,
                value=1.0,
                threshold=self.MIN_DIVERSITY_SCORE,
                message="No existing data for diversity comparison, check N/A",
            )

        # Compute feature distributions
        new_features = self._extract_distribution_features(new_labels)
        existing_features = self._extract_distribution_features(existing_labels)

        # Compare distributions using Jensen-Shannon-like divergence
        diversity = self._compute_distribution_divergence(new_features, existing_features)
        passed = diversity >= self.MIN_DIVERSITY_SCORE

        return GateCheck(
            name="diversity",
            passed=passed,
            value=diversity,
            threshold=self.MIN_DIVERSITY_SCORE,
            message=(
                f"Data diversity: {diversity:.4f} (minimum: {self.MIN_DIVERSITY_SCORE})"
                if passed
                else f"Low diversity: {diversity:.4f} < {self.MIN_DIVERSITY_SCORE}. New data too similar to existing dataset."
            ),
        )

    def _check_duplicates(
        self,
        labels: list[dict[str, Any]]
    ) -> GateCheck:
        """Check for near-duplicate samples using feature hashing."""
        if len(labels) < 2:
            return GateCheck(
                name="duplicates",
                passed=True,
                value=0.0,
                threshold=self.MAX_DUPLICATE_RATIO,
                message="Too few samples for duplicate detection",
            )

        hashes = set()
        duplicates = 0

        for label in labels:
            # Compute a hash based on detection features
            feature_str = self._compute_sample_hash(label)
            if feature_str in hashes:
                duplicates += 1
            else:
                hashes.add(feature_str)

        dup_ratio = duplicates / len(labels)
        passed = dup_ratio <= self.MAX_DUPLICATE_RATIO

        return GateCheck(
            name="duplicates",
            passed=passed,
            value=dup_ratio,
            threshold=self.MAX_DUPLICATE_RATIO,
            message=(
                f"Near-duplicate ratio: {dup_ratio:.1%} (max: {self.MAX_DUPLICATE_RATIO:.0%})"
                if passed
                else f"Too many duplicates: {dup_ratio:.1%} > {self.MAX_DUPLICATE_RATIO:.0%}. "
                     f"{duplicates} near-duplicates found in {len(labels)} samples."
            ),
        )

    def _extract_distribution_features(
        self,
        labels: list[dict[str, Any]]
    ) -> dict[str, float]:
        """Extract aggregate feature distribution from a set of labels."""
        class_counts: Counter = Counter()
        total_detections = 0
        total_confidence = 0.0
        spatial_bins: Counter = Counter()

        for label in labels:
            for det in label.get("detections", []):
                class_counts[det.get("class_id", 0)] += 1
                total_detections += 1
                total_confidence += det.get("confidence", 0)

                # Spatial binning (3x3 grid)
                x = int(det.get("x", 0.5) * 3)
                y = int(det.get("y", 0.5) * 3)
                spatial_bins[f"{x}_{y}"] += 1

        features = {}

        # Class distribution
        for cls_id, count in class_counts.items():
            features[f"class_{cls_id}"] = count / max(total_detections, 1)

        # Spatial distribution
        for bin_key, count in spatial_bins.items():
            features[f"spatial_{bin_key}"] = count / max(total_detections, 1)

        # Average confidence
        features["avg_confidence"] = total_confidence / max(total_detections, 1)
        features["avg_detections_per_image"] = total_detections / max(len(labels), 1)

        return features

    def _compute_distribution_divergence(
        self,
        dist_a: dict[str, float],
        dist_b: dict[str, float]
    ) -> float:
        """Compute simplified divergence between two feature distributions."""
        all_keys = set(dist_a.keys()) | set(dist_b.keys())
        if not all_keys:
            return 1.0

        total_diff = 0.0
        for key in all_keys:
            val_a = dist_a.get(key, 0.0)
            val_b = dist_b.get(key, 0.0)
            total_diff += abs(val_a - val_b)

        # Normalize by number of features
        avg_diff = total_diff / len(all_keys)

        # Clamp to [0, 1]
        return min(max(avg_diff, 0.0), 1.0)

    def _compute_sample_hash(self, label: dict[str, Any]) -> str:
        """Compute feature hash for near-duplicate detection."""
        detections = label.get("detections", [])

        features = []
        for det in sorted(detections, key=lambda d: d.get("class_id", 0)):
            cls = det.get("class_id", 0)
            x = round(det.get("x", 0), 1)
            y = round(det.get("y", 0), 1)
            w = round(det.get("width", 0), 1)
            h = round(det.get("height", 0), 1)
            features.append(f"{cls}:{x}:{y}:{w}:{h}")

        feature_str = "|".join(features)
        return hashlib.md5(feature_str.encode()).hexdigest()[:16]

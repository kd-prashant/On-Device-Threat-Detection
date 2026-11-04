"""Base detector interface and unified result structures for SentinelEdge.

Ensures all threat classifiers adhere to a common, typed contract:
predict(input_data) -> DetectionResult
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DetectionResult:
    """Unified classification result across all threat modalities.

    Attributes:
        threat_type: Threat domain ('url', 'sms', or 'network').
        is_threat: Boolean indicator whether sample is flagged as malicious.
        label: Plain-text verdict (e.g. 'phishing', 'scam', 'safe', 'normal').
        confidence: Prediction confidence score between 0.0 and 1.0.
        latency_ms: Measured end-to-end inference latency in milliseconds.
        extracted_features: Key features or tokens extracted during inference.
    """

    threat_type: str
    is_threat: bool
    label: str
    confidence: float
    latency_ms: float
    extracted_features: dict[str, Any] = field(default_factory=dict)


class BaseDetector(ABC):
    """Abstract contract for on-device threat classification engines."""

    @abstractmethod
    def predict(self, input_data: Any) -> DetectionResult:
        """Run inference on a single untrusted input sample.

        Args:
            input_data: Raw URL string, SMS string, or network flow dictionary/row.

        Returns:
            DetectionResult populated with verdict, confidence, and latency.
        """
        pass

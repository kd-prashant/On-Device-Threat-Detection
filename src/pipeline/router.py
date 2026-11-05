"""Unified Threat Detection & Explanation Pipeline for SentinelEdge (FR-6).

Provides a single, hardened entry point that:
1. Automatically identifies the threat modality ('url', 'sms', or 'network').
2. Dispatches to the corresponding ultra-lightweight detector (< 15ms).
3. Passes mathematical telemetry to the anti-prompt-injection explainer.
4. Returns a typed, verifiable PipelineResult with end-to-end latency.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Any

from src.detectors.base import DetectionResult
from src.detectors.network_detector import NetworkDetector
from src.detectors.sms_detector import SMSDetector
from src.detectors.url_detector import URLDetector
from src.explainer.base import BaseExplainer, ExplanationResult
from src.explainer.runtime import get_default_explainer


@dataclass
class PipelineResult:
    """Unified result packaging detection telemetry and plain-English advice.

    Attributes:
        input_type: Resolved modality ('url', 'sms', or 'network').
        raw_input: Original untrusted payload.
        detection: DetectionResult containing verdict, confidence, and latency.
        explanation: ExplanationResult containing rationale and defensive steps.
        total_latency_ms: Combined end-to-end processing time in milliseconds.
    """

    input_type: str
    raw_input: Any
    detection: DetectionResult
    explanation: ExplanationResult
    total_latency_ms: float


# Domain regex for URL auto-detection
URL_PATTERN = re.compile(
    r"^(?:https?://|ftp://|www\.)[^\s/$.?#].[^\s]*$",
    re.IGNORECASE,
)

BARE_DOMAIN_PATTERN = re.compile(
    r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?$",
    re.IGNORECASE,
)


def detect_input_type(input_data: Any) -> str:
    """Automatically determine the modality of an untrusted input.

    Args:
        input_data: Raw input (string, dict, tuple, or list).

    Returns:
        One of 'network', 'url', or 'sms'.
    """
    # 1. Check for Network Flow features
    if isinstance(input_data, dict):
        network_keys = {
            "protocol_type",
            "service",
            "flag",
            "src_bytes",
            "dst_bytes",
            "duration",
        }
        if any(k in input_data for k in network_keys):
            return "network"
        return "sms"

    if isinstance(input_data, (list, tuple)):
        # NSL-KDD row tuple (41 features)
        if len(input_data) in (41, 42, 43):
            return "network"
        return "sms"

    # 2. String inspections (URL vs SMS)
    if isinstance(input_data, str):
        text = input_data.strip()

        # If whitespace is present, it's virtually always an SMS message
        if " " in text or "\n" in text:
            return "sms"

        # Check explicit URL patterns or bare domain patterns
        if URL_PATTERN.match(text) or BARE_DOMAIN_PATTERN.match(text):
            return "url"

        # Check if text looks like an IP address or port
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?(?:/.*)?$", text):
            return "url"

        # Short single words default to SMS
        return "sms"

    return "sms"


class UnifiedPipeline:
    """Production-grade two-tier threat detection and explainable AI assistant."""

    def __init__(
        self,
        url_detector: URLDetector | None = None,
        sms_detector: SMSDetector | None = None,
        network_detector: NetworkDetector | None = None,
        explainer: BaseExplainer | None = None,
    ) -> None:
        self.url_detector = url_detector or URLDetector()
        self.sms_detector = sms_detector or SMSDetector()
        self.network_detector = network_detector or NetworkDetector()
        self.explainer = explainer or get_default_explainer()

    def analyze(
        self,
        input_data: Any,
        input_type: str = "auto",
    ) -> PipelineResult:
        """Analyze arbitrary untrusted input through the two-tier pipeline.

        Args:
            input_data: URL string, SMS text, or network flow dict/row.
            input_type: One of 'auto', 'url', 'sms', or 'network'.

        Returns:
            PipelineResult combining detector metrics and defensive explanation.
        """
        start_time = time.perf_counter()

        # 1. Resolve modality
        norm_type = input_type.lower()
        if norm_type == "auto":
            resolved_type = detect_input_type(input_data)
        elif norm_type in ("url", "sms", "network"):
            resolved_type = norm_type
        else:
            msg = f"Invalid input_type '{input_type}'. Must be auto, url, sms, network."
            raise ValueError(msg)

        # 2. Tier 1: Fast Classical ML Detection (< 15ms)
        if resolved_type == "url":
            detection_res = self.url_detector.predict(str(input_data))
        elif resolved_type == "sms":
            detection_res = self.sms_detector.predict(str(input_data))
        elif resolved_type == "network":
            detection_res = self.network_detector.predict(input_data)
        else:
            raise RuntimeError(f"Unsupported resolved type: {resolved_type}")

        # 3. Tier 2: Safe Explainer Reasoning (< 100 words, strictly defensive)
        explanation_res = self.explainer.explain(detection_res, input_data)

        # 4. Total Pipeline Latency
        total_latency_ms = (time.perf_counter() - start_time) * 1000.0

        return PipelineResult(
            input_type=resolved_type,
            raw_input=input_data,
            detection=detection_res,
            explanation=explanation_res,
            total_latency_ms=round(total_latency_ms, 2),
        )


# Global singleton instance for 1-line usage
_GLOBAL_PIPELINE: UnifiedPipeline | None = None


def analyze(input_data: Any, input_type: str = "auto") -> PipelineResult:
    """Analyze arbitrary untrusted input using the global pipeline instance.

    Convenience 1-line API for production scripts, UI, and external integration.
    """
    global _GLOBAL_PIPELINE
    if _GLOBAL_PIPELINE is None:
        _GLOBAL_PIPELINE = UnifiedPipeline()
    return _GLOBAL_PIPELINE.analyze(input_data, input_type=input_type)

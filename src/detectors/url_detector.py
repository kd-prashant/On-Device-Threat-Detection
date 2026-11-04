"""On-device URL Phishing classification engine.

Extracts static lexical and entropy features from raw URLs and evaluates them
against the trained gradient-boosted decision model without internet connectivity.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.detectors.base import BaseDetector, DetectionResult
from src.utils.url_features import extract_url_features

logger = logging.getLogger(__name__)

DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parent.parent.parent / "models" / "url_detector.pkl"
)


class URLDetector(BaseDetector):
    """Offline Phishing URL Classifier."""

    def __init__(self, model_path: Path | str | None = None) -> None:
        self.model_path = Path(model_path or DEFAULT_MODEL_PATH)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"URL detector model not found at {self.model_path}."
            )
        self.model = joblib.load(self.model_path)
        logger.debug("Loaded URL detector from %s", self.model_path)

    def predict(self, input_data: Any) -> DetectionResult:
        """Analyze a raw URL string for phishing indicators.

        Args:
            input_data: Raw URL string.

        Returns:
            DetectionResult with verdict ('phishing' vs. 'safe'), confidence, latency.
        """
        raw_url = str(input_data).strip()
        start = time.perf_counter()

        features = extract_url_features(raw_url)
        features_df = pd.DataFrame([features])

        # Get prediction and probabilities in a single pass
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(features_df)[0]
            pred = int(probs.argmax())
            confidence = float(probs[pred])
        else:
            pred = int(self.model.predict(features_df)[0])
            confidence = 1.0

        latency_ms = float((time.perf_counter() - start) * 1000.0)

        is_threat = bool(pred == 1)
        label = "phishing" if is_threat else "safe"

        # Highlight salient indicators
        salient: dict[str, Any] = {
            "is_ip": features["is_ip"],
            "entropy": features["entropy"],
            "suspicious_tld": features["suspicious_tld"],
            "has_brand_keyword": features["has_brand_keyword"],
            "url_length": features["url_length"],
        }

        return DetectionResult(
            threat_type="url",
            is_threat=is_threat,
            label=label,
            confidence=confidence,
            latency_ms=latency_ms,
            extracted_features=salient,
        )

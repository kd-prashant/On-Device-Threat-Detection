"""On-device SMS Scam and Smishing classification engine.

Processes raw SMS text, extracts psychological urgency markers and monetary indicators,
and evaluates calibrated probabilistic models entirely on-device.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.detectors.base import BaseDetector, DetectionResult
from src.utils.sms_preprocessor import (
    clean_sms_text,
    extract_sms_metadata_features,
)

logger = logging.getLogger(__name__)

DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parent.parent.parent / "models" / "sms_detector.pkl"
)


class SMSDetector(BaseDetector):
    """Offline SMS Scam & Smishing Classifier."""

    def __init__(self, model_path: Path | str | None = None) -> None:
        self.model_path = Path(model_path or DEFAULT_MODEL_PATH)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"SMS detector model not found at {self.model_path}."
            )
        self.model = joblib.load(self.model_path)
        logger.debug("Loaded SMS detector from %s", self.model_path)

    def predict(self, input_data: Any) -> DetectionResult:
        """Analyze a raw SMS message for social engineering and scam markers.

        Args:
            input_data: Raw text of the SMS message.

        Returns:
            DetectionResult with verdict ('scam' vs. 'legitimate'), confidence, latency.
        """
        raw_text = str(input_data).strip()
        start = time.perf_counter()

        cleaned = clean_sms_text(raw_text)
        metadata = extract_sms_metadata_features(raw_text)

        # Build single-row DataFrame matching the model's FeatureUnion schema
        sample_dict = {"clean_text": [cleaned]}
        for k, v in metadata.items():
            sample_dict[k] = [v]

        sample_df = pd.DataFrame(sample_dict)

        # Single pass probability & prediction
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(sample_df)[0]
            pred = int(probs.argmax())
            confidence = float(probs[pred])
        else:
            pred = int(self.model.predict(sample_df)[0])
            confidence = 1.0

        latency_ms = float((time.perf_counter() - start) * 1000.0)

        is_threat = bool(pred == 1)
        label = "scam" if is_threat else "legitimate"

        salient: dict[str, Any] = {
            "urgency_score": metadata["urgency_score"],
            "financial_scam_score": metadata["financial_scam_score"],
            "has_url": metadata["has_url"],
            "has_currency": metadata["has_currency"],
            "upper_ratio": metadata["upper_ratio"],
        }

        return DetectionResult(
            threat_type="sms",
            is_threat=is_threat,
            label=label,
            confidence=confidence,
            latency_ms=latency_ms,
            extracted_features=salient,
        )

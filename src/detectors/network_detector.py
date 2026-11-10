"""On-device Network Intrusion and Flow Anomaly classification engine.

Processes bidirectional network flow records, detects port scanning, denial-of-service,
and unauthorized access anomalies using lightweight tree boosting.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.detectors.base import BaseDetector, DetectionResult
from src.utils.network_preprocessor import NSL_KDD_COLUMNS

logger = logging.getLogger(__name__)

DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parent.parent.parent / "models" / "network_detector.pkl"
)

# Standard default values for 41 flow attributes
DEFAULT_FLOW_VALUES: dict[str, Any] = {
    "duration": 0,
    "protocol_type": "tcp",
    "service": "http",
    "flag": "SF",
    "src_bytes": 0,
    "dst_bytes": 0,
    "land": 0,
    "wrong_fragment": 0,
    "urgent": 0,
    "hot": 0,
    "num_failed_logins": 0,
    "logged_in": 0,
    "num_compromised": 0,
    "root_shell": 0,
    "su_attempted": 0,
    "num_root": 0,
    "num_file_creations": 0,
    "num_shells": 0,
    "num_access_files": 0,
    "num_outbound_cmds": 0,
    "is_host_login": 0,
    "is_guest_login": 0,
    "count": 1,
    "srv_count": 1,
    "serror_rate": 0.0,
    "srv_serror_rate": 0.0,
    "rerror_rate": 0.0,
    "srv_rerror_rate": 0.0,
    "same_srv_rate": 1.0,
    "diff_srv_rate": 0.0,
    "srv_diff_host_rate": 0.0,
    "dst_host_count": 1,
    "dst_host_srv_count": 1,
    "dst_host_same_srv_rate": 1.0,
    "dst_host_diff_srv_rate": 0.0,
    "dst_host_same_src_port_rate": 0.0,
    "dst_host_srv_diff_host_rate": 0.0,
    "dst_host_serror_rate": 0.0,
    "dst_host_srv_serror_rate": 0.0,
    "dst_host_rerror_rate": 0.0,
    "dst_host_srv_rerror_rate": 0.0,
}


class NetworkDetector(BaseDetector):
    """Offline Network Intrusion & Anomaly Classifier."""

    def __init__(self, model_path: Path | str | None = None) -> None:
        self.model_path = Path(model_path or DEFAULT_MODEL_PATH)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Network detector model not found at {self.model_path}."
            )
        self.model = joblib.load(self.model_path)
        logger.debug("Loaded Network detector from %s", self.model_path)

    def predict(self, input_data: Any) -> DetectionResult:
        """Analyze network flow statistics for anomalous or malicious patterns.

        Args:
            input_data: Dictionary, Series, or DataFrame of flow features.

        Returns:
            DetectionResult with verdict, confidence, and latency.
        """
        start = time.perf_counter()

        if isinstance(input_data, dict):
            # Impute defaults for any missing flow fields
            flow_dict = {
                col: input_data.get(col, DEFAULT_FLOW_VALUES.get(col, 0))
                for col in NSL_KDD_COLUMNS[:41]
            }
            sample_df = pd.DataFrame([flow_dict])
        elif isinstance(input_data, pd.DataFrame):
            sample_df = input_data.copy()
        elif isinstance(input_data, pd.Series):
            sample_df = pd.DataFrame([input_data.to_dict()])
        else:
            raise TypeError(
                f"Unsupported input type for network flow: {type(input_data)}"
            )

        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(sample_df)[0]
            pred = int(probs.argmax())
            confidence = float(probs[pred])
        else:
            pred = int(self.model.predict(sample_df)[0])
            confidence = 1.0

        latency_ms = float((time.perf_counter() - start) * 1000.0)

        is_threat = bool(pred == 1)
        label = "anomalous" if is_threat else "normal"

        salient: dict[str, Any] = {
            "protocol_type": sample_df["protocol_type"].iloc[0],
            "service": sample_df["service"].iloc[0],
            "flag": sample_df["flag"].iloc[0],
            "src_bytes": int(sample_df["src_bytes"].iloc[0]),
            "dst_bytes": int(sample_df["dst_bytes"].iloc[0]),
            "count": int(sample_df["count"].iloc[0]),
        }

        return DetectionResult(
            threat_type="network",
            is_threat=is_threat,
            label=label,
            confidence=confidence,
            latency_ms=latency_ms,
            extracted_features=salient,
        )

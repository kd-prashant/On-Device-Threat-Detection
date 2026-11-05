"""Integration test suite for the SentinelEdge Unified Pipeline (FR-6)."""

from __future__ import annotations

import pytest

from src.pipeline.router import UnifiedPipeline, analyze, detect_input_type


def test_detect_input_type_urls() -> None:
    """Verify robust auto-detection of various URL formats."""
    assert detect_input_type("https://www.google.com") == "url"
    assert detect_input_type("http://paypal-verification.com/login") == "url"
    assert detect_input_type("www.github.com/kd-prashant") == "url"
    assert detect_input_type("bit.ly/secure-auth") == "url"
    assert detect_input_type("192.168.1.55:8080/admin") == "url"


def test_detect_input_type_sms() -> None:
    """Verify auto-detection of SMS text messages."""
    msg = "URGENT: Your bank account is suspended. Verify KYC now: http://scam.ru"
    assert detect_input_type(msg) == "sms"
    assert detect_input_type("Hey Rahul, let's meet at 4 PM in the library.") == "sms"
    assert detect_input_type("Call me when you reach home.") == "sms"
    assert detect_input_type("") == "sms"


def test_detect_input_type_network() -> None:
    """Verify auto-detection of network flow telemetry."""
    flow_dict = {"protocol_type": "tcp", "service": "http", "src_bytes": 100}
    assert detect_input_type(flow_dict) == "network"
    assert detect_input_type([0] * 41) == "network"


def test_url_pipeline_end_to_end() -> None:
    """Verify end-to-end URL analysis with detection and defensive explanation."""
    pipeline = UnifiedPipeline()
    res = pipeline.analyze("http://192.168.1.55/paypal.com/security.top?auth=token")

    assert res.input_type == "url"
    assert res.detection.is_threat is True
    assert res.detection.label.lower() == "phishing"
    assert res.explanation.verdict == "PHISHING"
    assert len(res.explanation.recommended_actions) == 3
    assert res.explanation.mitre_attack is not None
    assert res.explanation.mitre_attack.technique_id == "T1566.002"
    assert res.total_latency_ms > 0.0


def test_sms_pipeline_end_to_end() -> None:
    """Verify end-to-end SMS scam detection and plain-English explanation."""
    res = analyze(
        "URGENT: Your bank account is blocked! Update KYC: http://bit.ly/scam"
    )

    assert res.input_type == "sms"
    assert res.detection.is_threat is True
    assert res.detection.label.lower() == "scam"
    assert res.explanation.verdict == "SCAM"
    assert len(res.explanation.recommended_actions) == 3
    assert "Do NOT click" in res.explanation.recommended_actions[0]
    assert res.explanation.mitre_attack is not None
    assert res.explanation.mitre_attack.technique_id == "T1476"


def test_network_pipeline_end_to_end() -> None:
    """Verify end-to-end Network flow anomaly analysis."""
    syn_flood = {
        "duration": 0,
        "protocol_type": "tcp",
        "service": "private",
        "flag": "S0",
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
        "count": 250,
        "srv_count": 18,
        "serror_rate": 1.0,
        "srv_serror_rate": 1.0,
        "rerror_rate": 0.0,
        "srv_rerror_rate": 0.0,
        "same_srv_rate": 0.07,
        "diff_srv_rate": 0.07,
        "srv_diff_host_rate": 0.0,
        "dst_host_count": 255,
        "dst_host_srv_count": 18,
        "dst_host_same_srv_rate": 0.07,
        "dst_host_diff_srv_rate": 0.07,
        "dst_host_same_src_port_rate": 0.0,
        "dst_host_srv_diff_host_rate": 0.0,
        "dst_host_serror_rate": 1.0,
        "dst_host_srv_serror_rate": 1.0,
        "dst_host_rerror_rate": 0.0,
        "dst_host_srv_rerror_rate": 0.0,
    }
    res = analyze(syn_flood)

    assert res.input_type == "network"
    assert res.detection.is_threat is True
    assert res.detection.label.lower() == "anomalous"
    assert len(res.explanation.recommended_actions) == 3


def test_benign_inputs_produce_safe_advice() -> None:
    """Verify benign inputs produce clean verdicts and non-alarmist advice."""
    res_url = analyze("https://www.google.com")
    assert res_url.detection.is_threat is False
    assert res_url.explanation.is_threat is False
    assert len(res_url.explanation.recommended_actions) == 3

    res_sms = analyze("Hey, see you at the library at 5pm.")
    assert res_sms.detection.is_threat is False
    assert res_sms.explanation.is_threat is False


def test_invalid_input_type_raises_error() -> None:
    """Verify that unsupported input_type raises a helpful ValueError."""
    pipeline = UnifiedPipeline()
    with pytest.raises(ValueError, match="Invalid input_type"):
        pipeline.analyze("test", input_type="bluetooth")

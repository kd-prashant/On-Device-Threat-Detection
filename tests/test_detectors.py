"""Unit and integration tests for SentinelEdge on-device threat detectors (WP3)."""

from __future__ import annotations

import pytest

from src.detectors.network_detector import NetworkDetector
from src.detectors.sms_detector import SMSDetector
from src.detectors.url_detector import URLDetector


@pytest.fixture(scope="module")
def url_detector() -> URLDetector:
    return URLDetector()


@pytest.fixture(scope="module")
def sms_detector() -> SMSDetector:
    return SMSDetector()


@pytest.fixture(scope="module")
def network_detector() -> NetworkDetector:
    return NetworkDetector()


# ---------------------------------------------------------------------------
# URL Detector Tests
# ---------------------------------------------------------------------------


def test_url_detector_benign(url_detector: URLDetector) -> None:
    """Verify that a standard legitimate website is marked safe."""
    res = url_detector.predict("https://www.google.com")
    assert not res.is_threat
    assert res.label == "safe"
    assert res.threat_type == "url"
    assert 0.0 <= res.confidence <= 1.0
    assert res.latency_ms > 0.0


def test_url_detector_phishing(url_detector: URLDetector) -> None:
    """Verify that an IP-based homoglyph URL is flagged as phishing."""
    phishing_url = "http://192.168.1.55/paypal.com/login-verify.top?auth=token"
    res = url_detector.predict(phishing_url)
    assert res.is_threat
    assert res.label == "phishing"
    assert res.threat_type == "url"
    assert res.confidence > 0.5
    assert res.latency_ms > 0.0


# ---------------------------------------------------------------------------
# SMS Detector Tests
# ---------------------------------------------------------------------------


def test_sms_detector_legitimate(sms_detector: SMSDetector) -> None:
    """Verify that a personal conversational message is marked legitimate."""
    msg = "Hey, are we still meeting for lunch at 1pm today?"
    res = sms_detector.predict(msg)
    assert not res.is_threat
    assert res.label == "legitimate"
    assert res.threat_type == "sms"
    assert res.confidence > 0.5
    assert res.latency_ms > 0.0


def test_sms_detector_scam(sms_detector: SMSDetector) -> None:
    """Verify that an urgent KYC financial lure is flagged as a scam."""
    msg = (
        "URGENT: Your bank account is BLOCKED! Immediate KYC update required "
        "within 24 hours. Send ₹5000 fine or face legal action: http://bit.ly/scam"
    )
    res = sms_detector.predict(msg)
    assert res.is_threat
    assert res.label == "scam"
    assert res.threat_type == "sms"
    assert res.confidence > 0.5
    assert res.latency_ms > 0.0


# ---------------------------------------------------------------------------
# Network Anomaly Detector Tests
# ---------------------------------------------------------------------------


def test_network_detector_normal(network_detector: NetworkDetector) -> None:
    """Verify standard legitimate web browsing flow is classified normal."""
    normal_flow = {
        "duration": 0,
        "protocol_type": "tcp",
        "service": "http",
        "flag": "SF",
        "src_bytes": 215,
        "dst_bytes": 4507,
        "logged_in": 1,
        "count": 5,
        "srv_count": 5,
        "same_srv_rate": 1.0,
        "diff_srv_rate": 0.0,
    }
    res = network_detector.predict(normal_flow)
    assert not res.is_threat
    assert res.label == "normal"
    assert res.threat_type == "network"
    assert res.latency_ms > 0.0


def test_network_detector_anomaly(network_detector: NetworkDetector) -> None:
    """Verify that a high-rate SYN flood or scan flow is flagged as anomalous."""
    attack_flow = {
        "duration": 0,
        "protocol_type": "tcp",
        "service": "private",
        "flag": "S0",
        "src_bytes": 0,
        "dst_bytes": 0,
        "logged_in": 0,
        "count": 250,
        "srv_count": 10,
        "serror_rate": 1.0,
        "srv_serror_rate": 1.0,
        "same_srv_rate": 0.04,
        "diff_srv_rate": 0.06,
        "dst_host_count": 255,
        "dst_host_srv_count": 10,
        "dst_host_same_srv_rate": 0.04,
        "dst_host_serror_rate": 1.0,
    }
    res = network_detector.predict(attack_flow)
    assert res.is_threat
    assert res.label == "anomalous"
    assert res.threat_type == "network"
    assert res.confidence > 0.5
    assert res.latency_ms > 0.0


# ---------------------------------------------------------------------------
# Latency Budget Benchmark (< 15 ms target)
# ---------------------------------------------------------------------------


def test_real_time_latency_budget(
    url_detector: URLDetector,
    sms_detector: SMSDetector,
    network_detector: NetworkDetector,
) -> None:
    """Verify that average inference latency satisfies the < 15ms PRD target."""
    # Warm-up passes
    _ = url_detector.predict("https://www.example.com")
    _ = sms_detector.predict("Hello, how are you?")
    _ = network_detector.predict({"protocol_type": "tcp", "service": "http"})

    url_latencies = [
        url_detector.predict("https://www.wikipedia.org").latency_ms for _ in range(20)
    ]
    sms_latencies = [
        sms_detector.predict("Hi there, how are you?").latency_ms for _ in range(20)
    ]
    net_latencies = [
        network_detector.predict({"protocol_type": "tcp", "service": "http"}).latency_ms
        for _ in range(20)
    ]

    avg_url = sum(url_latencies) / len(url_latencies)
    avg_sms = sum(sms_latencies) / len(sms_latencies)
    avg_net = sum(net_latencies) / len(net_latencies)

    # Average latency over repeated runs must be under 15ms
    assert avg_url < 15.0, f"URL average latency too high: {avg_url:.2f}ms"
    assert avg_sms < 15.0, f"SMS average latency too high: {avg_sms:.2f}ms"
    assert avg_net < 15.0, f"Network average latency too high: {avg_net:.2f}ms"

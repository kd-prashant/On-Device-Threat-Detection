"""Unit tests for SentinelEdge mobile deployment and edge runtime engines (WP8)."""

from __future__ import annotations

import socket
from pathlib import Path

import pytest

from deploy.edge_runtime import MobileEdgePipeline, PortableSMSScorer
from deploy.export_detectors import (
    export_network_detector,
    export_sms_detector,
    export_url_detector,
    verify_sms_parity,
)
from deploy.export_llama_pte import generate_aot_specification
from deploy.verify_offline_contract import (
    AirGapViolationError,
    install_network_interceptor,
)


@pytest.fixture(scope="module")
def models_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "models"


@pytest.fixture(scope="module")
def export_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("deploy_test")
    return out


def test_export_detectors_pipeline(models_dir: Path, export_dir: Path) -> None:
    """Verify that export_detectors produces all required mobile artifacts."""
    sms_res = export_sms_detector(models_dir / "sms_detector.pkl", export_dir)
    assert Path(sms_res["output_path"]).exists()
    assert sms_res["vocab_size"] > 1000

    url_res = export_url_detector(models_dir / "url_detector.pkl", export_dir)
    assert Path(url_res["spec_path"]).exists()
    assert Path(url_res["mobile_joblib_path"]).exists()

    net_res = export_network_detector(models_dir / "network_detector.pkl", export_dir)
    assert Path(net_res["mobile_joblib_path"]).exists()


def test_sms_portable_exact_parity(models_dir: Path, export_dir: Path) -> None:
    """Verify 100% mathematical parity between scikit-learn and portable SMS engine."""
    sms_res = export_sms_detector(models_dir / "sms_detector.pkl", export_dir)
    parity = verify_sms_parity(
        models_dir / "sms_detector.pkl",
        Path(sms_res["output_path"]),
    )
    assert parity == 1.0, f"Parity mismatch: expected 1.0, got {parity}"


def test_portable_sms_scorer_live(models_dir: Path, export_dir: Path) -> None:
    """Verify PortableSMSScorer inference on threat and benign inputs."""
    sms_res = export_sms_detector(models_dir / "sms_detector.pkl", export_dir)
    scorer = PortableSMSScorer(sms_res["output_path"])

    # High urgency scam test
    pred, prob, salient = scorer.score(
        "URGENT: Your account is suspended! Verify at http://fake.ru"
    )
    assert pred == 1
    assert prob > 0.5
    assert salient["urgency_score"] > 0

    # Benign SMS test
    pred_b, prob_b, _ = scorer.score("Hey, are we still meeting for lunch tomorrow?")
    assert pred_b == 0
    assert prob_b < 0.5


def test_mobile_edge_pipeline_multimodal(models_dir: Path, export_dir: Path) -> None:
    """Test unified MobileEdgePipeline on SMS, URL, and Network flows."""
    export_sms_detector(models_dir / "sms_detector.pkl", export_dir)
    export_url_detector(models_dir / "url_detector.pkl", export_dir)
    export_network_detector(models_dir / "network_detector.pkl", export_dir)

    pipeline = MobileEdgePipeline(export_dir)

    # 1. SMS
    res_sms = pipeline.analyze_sms("URGENT: Call 9999 now to claim your cash award!")
    assert res_sms.threat_type == "sms"
    assert res_sms.is_threat is True
    assert res_sms.latency_ms < 50.0

    # 2. URL
    res_url = pipeline.analyze_url("http://192.168.1.1/paypal.com/security")
    assert res_url.threat_type == "url"
    assert res_url.is_threat is True
    assert res_url.confidence > 0.8

    # 3. Network
    res_net = pipeline.analyze_network({"flag": "S0", "count": 400})
    assert res_net.threat_type == "network"
    assert res_net.latency_ms < 50.0


def test_llama_aot_specification_contract() -> None:
    """Verify ExecuTorch AOT specifications adhere to 4-bit mobile constraints."""
    spec = generate_aot_specification(
        model_id="meta-llama/Llama-3.2-1B-Instruct",
        output_path=Path("dummy.pte"),
        quant_group_size=128,
        backend="xnnpack",
    )
    assert spec["quantization"]["precision"] == "INT4"
    assert spec["quantization"]["group_size"] == 128
    assert spec["hardware_target"]["delegate_backend"] == "xnnpack"
    assert spec["quantization"]["estimated_binary_size_mb"] <= 800.0


def test_airgap_interceptor_blocks_sockets() -> None:
    """Verify air-gap interceptor successfully prevents socket creation."""
    orig_socket = socket.socket
    orig_conn = socket.create_connection
    orig_addr = socket.getaddrinfo
    try:
        install_network_interceptor()
        with pytest.raises(AirGapViolationError) as exc_info:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        assert "AIR-GAP VIOLATION" in str(exc_info.value)
    finally:
        socket.socket = orig_socket
        socket.create_connection = orig_conn
        socket.getaddrinfo = orig_addr

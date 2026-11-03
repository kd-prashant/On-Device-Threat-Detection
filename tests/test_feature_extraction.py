"""Unit tests for offline feature extraction and preprocessing logic."""

from __future__ import annotations

from src.utils.sms_preprocessor import (
    clean_sms_text,
    extract_sms_metadata_features,
)
from src.utils.url_features import (
    calculate_shannon_entropy,
    extract_url_features,
)


def test_url_benign_features() -> None:
    """Verify feature extraction on a clean benign domain."""
    url = "https://www.google.com/search?q=machine+learning"
    feats = extract_url_features(url)

    assert feats["is_ip"] == 0
    assert feats["has_https"] == 1
    assert feats["suspicious_tld"] == 0
    assert feats["num_dots"] >= 2
    assert feats["entropy"] > 0.0


def test_url_phishing_features() -> None:
    """Verify feature extraction flags known deceptive signals."""
    url = "http://192.168.1.100/paypal.com/login-verify.top?session=secure"
    feats = extract_url_features(url)

    assert feats["is_ip"] == 1
    assert feats["has_https"] == 0
    assert feats["suspicious_tld"] == 1
    assert feats["has_brand_keyword"] == 1
    assert feats["num_slashes"] >= 4


def test_url_edge_cases() -> None:
    """Verify robustness to empty, minimal, and scheme-less URLs."""
    feats_empty = extract_url_features("")
    assert feats_empty["url_length"] == 0
    assert feats_empty["entropy"] == 0.0

    feats_no_scheme = extract_url_features("my-bank-login.xyz/update")
    assert feats_no_scheme["suspicious_tld"] == 1
    assert feats_no_scheme["has_brand_keyword"] == 1


def test_shannon_entropy_calculation() -> None:
    """Check mathematical sanity of Shannon entropy."""
    # A string of identical characters has 0 entropy (no surprise/randomness)
    assert calculate_shannon_entropy("aaaaaaa") == 0.0
    # Random varied characters have positive entropy
    assert calculate_shannon_entropy("abcdefgh") > 2.5


def test_sms_urgency_and_metadata_features() -> None:
    """Verify extraction of urgency tokens and monetary triggers."""
    sms = (
        "URGENT! Your bank account KYC expired. Transfer ₹5000 immediately "
        "or account blocked within 24 hours: http://bit.ly/scam"
    )
    feats = extract_sms_metadata_features(sms)

    assert feats["num_exclamation"] >= 1
    assert feats["has_url"] == 1
    assert feats["has_currency"] == 1
    assert feats["urgency_score"] >= 2
    assert feats["financial_scam_score"] >= 1
    assert feats["upper_ratio"] > 0.05


def test_sms_cleaner() -> None:
    """Verify semantic normalization of URLs and currency symbols."""
    raw = "Claim your $500 reward now at https://prize.top or call 9876543210!"
    cleaned = clean_sms_text(raw)

    assert "<url>" in cleaned
    assert "<currency>" in cleaned
    assert "<phone>" in cleaned
    assert "https://" not in cleaned

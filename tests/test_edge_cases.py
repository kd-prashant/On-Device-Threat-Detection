"""Edge-case robustness and fuzzing test suite for SentinelEdge (PRD WP5).

Verifies stability and safe degradation under:
- Empty and whitespace-only inputs
- Extremely long inputs (10,000+ characters)
- Multilingual and non-English scripts (Hindi, Chinese, Russian, Spanish)
- Malformed and edge-case URLs (missing hosts, raw IPs, excessive params)
- Emoji-heavy and punctuation spam
- Incomplete and partial network telemetry dictionaries
- Non-string and boundary types
"""

from __future__ import annotations

from src.pipeline.router import analyze


def test_empty_and_whitespace_inputs() -> None:
    """Verify that empty or whitespace inputs degrade gracefully to safe verdicts."""
    res_empty = analyze("")
    assert res_empty.detection.is_threat is False
    assert res_empty.explanation.is_threat is False
    assert len(res_empty.explanation.recommended_actions) == 3

    res_ws = analyze("   \n\t  \r  ")
    assert res_ws.detection.is_threat is False
    assert res_ws.explanation.is_threat is False


def test_extremely_long_inputs() -> None:
    """Verify that 10,000+ character inputs do not crash or cause memory exhaustion."""
    long_benign = "Hello world! " * 800  # ~10,400 chars
    res_long = analyze(long_benign)
    assert res_long is not None
    assert res_long.total_latency_ms > 0.0
    assert len(res_long.explanation.recommended_actions) == 3
    assert len(res_long.explanation.reasoning) > 0

    long_malicious = (
        "URGENT: Your bank account is locked! Verify KYC now: http://bit.ly/scam "
        + ("A" * 8000)
    )
    res_mal = analyze(long_malicious)
    assert res_mal.detection.is_threat is True
    assert res_mal.explanation.verdict == "SCAM"


def test_non_english_multilingual_inputs() -> None:
    """Verify UTF-8 resilience across Hindi, Chinese, Russian, and Spanish."""
    # Hindi scam text
    hindi_scam = (
        "चेतावनी: आपका बैंक खाता ब्लॉक कर दिया गया है। "
        "तुरंत सत्यापन करें: http://bit.ly/sbi-verify"
    )
    res_hi = analyze(hindi_scam)
    assert res_hi.input_type == "sms"
    assert len(res_hi.explanation.recommended_actions) == 3

    # Chinese text
    chinese_text = "紧急通知：您的账号存在安全风险，请立即登录验证：http://phish.cn"
    res_zh = analyze(chinese_text)
    assert res_zh.input_type == "sms"

    # Russian text
    russian_text = (
        "Срочно: Ваша карта заблокирована. Перейдите по ссылке: http://scam.ru"
    )
    res_ru = analyze(russian_text)
    assert res_ru.input_type == "sms"

    # Spanish text
    spanish_text = (
        "Urgente: Su cuenta ha sido suspendida. Verifique sus datos: http://scam.es"
    )
    res_es = analyze(spanish_text)
    assert res_es.input_type == "sms"


def test_malformed_urls() -> None:
    """Verify handling of malformed, exotic, or edge-case URLs."""
    # Missing host / protocol only
    res1 = analyze("http://", input_type="url")
    assert res1.input_type == "url"
    assert len(res1.explanation.recommended_actions) == 3

    # Excessive subdomains with suspicious TLD
    res2 = analyze(
        "http://secure.login.portal.account.verification.bank.service.top/auth"
    )
    assert res2.input_type == "url"
    assert res2.detection.is_threat is True
    assert res2.explanation.verdict == "PHISHING"

    # Raw IP address with port
    res3 = analyze("http://192.168.1.100:8080/admin/credentials")
    assert res3.input_type == "url"
    assert res3.detection.is_threat is True

    # Very long query parameter string
    long_query_url = "https://example.com/search?data=" + ("x" * 2000)
    res4 = analyze(long_query_url)
    assert res4.input_type == "url"


def test_emoji_heavy_inputs() -> None:
    """Verify that emojis and symbols parse smoothly without unicode errors."""
    emoji_scam = (
        "🚨🚨 URGENT! 💰💰 You won Rs. 50,000! "
        "Call 📱 +91-9876543210 or claim now 👉 http://prize-win.top 🎁"
    )
    res = analyze(emoji_scam)
    assert res.input_type == "sms"
    assert res.detection.is_threat is True
    assert res.explanation.verdict == "SCAM"


def test_punctuation_spam() -> None:
    """Verify that inputs with pure punctuation do not cause zero-division or crash."""
    punct = "!@#$%^&*()_+{}[]:;\"'|<>,.?/~`"
    res = analyze(punct)
    assert res.input_type == "sms"
    assert len(res.explanation.recommended_actions) == 3


def test_incomplete_network_telemetry() -> None:
    """Verify network detector imputes standard defaults on partial dictionaries."""
    # Empty dictionary
    res_empty = analyze({}, input_type="network")
    assert res_empty.input_type == "network"
    assert len(res_empty.explanation.recommended_actions) == 3

    # Partial dictionary with only a few critical SYN-flood features
    partial_dos = {
        "protocol_type": "tcp",
        "service": "private",
        "flag": "S0",
        "serror_rate": 1.0,
        "srv_serror_rate": 1.0,
        "dst_host_serror_rate": 1.0,
        "count": 300,
    }
    res_dos = analyze(partial_dos, input_type="network")
    assert res_dos.input_type == "network"
    assert res_dos.detection.is_threat is True
    assert res_dos.explanation.verdict == "ANOMALOUS"


def test_non_string_types_gracefully_handled() -> None:
    """Verify numeric or boundary types passed to analyze() handle safely."""
    res_int = analyze(123456789)
    assert res_int.input_type == "sms"
    assert len(res_int.explanation.recommended_actions) == 3

    res_none = analyze(None)
    assert res_none.input_type == "sms"

"""SMS preprocessing and feature extraction module for SentinelEdge.

Extracts urgency markers, monetary indicators, and linguistic metrics from SMS text,
and prepares clean text tokens for downstream TF-IDF / classical NLP models.
"""

from __future__ import annotations

import re

import pandas as pd

PHONE_PATTERN = re.compile(
    r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\b\d{5,10}\b"
)
URL_PATTERN = re.compile(
    r"https?://\S+|www\.\S+|\b[a-zA-Z0-9.-]+\.(?:com|org|net|top|xyz|tk|info|cc)\b"
)
CURRENCY_PATTERN = re.compile(r"[\$£€₹]|(\b(?:rs|inr|usd|eur|gbp)\b)", re.IGNORECASE)

URGENCY_KEYWORDS = {
    "urgent",
    "immediately",
    "blocked",
    "suspended",
    "expire",
    "action required",
    "warning",
    "alert",
    "24 hours",
    "penalty",
    "restricted",
}

FINANCIAL_SCAM_KEYWORDS = {
    "kyc",
    "pan",
    "lottery",
    "won",
    "winner",
    "prize",
    "cash",
    "claim",
    "reward",
    "free",
    "loan",
    "income",
    "refund",
    "tax",
    "otp",
}


def clean_sms_text(text: str) -> str:
    """Normalize SMS text for TF-IDF / Bag-of-Words representation.

    Replaces URLs, phone numbers, and currency values with semantic token markers,
    then lowercases and normalizes whitespace.
    """
    s = str(text)
    # Replace URLs and numbers with normalized semantic tokens
    s = URL_PATTERN.sub(" <URL> ", s)
    s = PHONE_PATTERN.sub(" <PHONE> ", s)
    s = CURRENCY_PATTERN.sub(" <CURRENCY> ", s)
    # Remove non-alphanumeric except tokens
    s = re.sub(r"[^\w\s<>!$₹€£]", " ", s)
    # Collapse multiple whitespaces
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def extract_sms_metadata_features(text: str) -> dict[str, float | int]:
    """Extract structural, linguistic, and scam features from an SMS message.

    Args:
        text: Raw SMS message string.

    Returns:
        Dictionary of numeric feature indicators.
    """
    raw = str(text)
    lower = raw.lower()
    msg_len = len(raw)

    num_upper = sum(1 for c in raw if c.isupper())
    upper_ratio = num_upper / max(msg_len, 1)

    has_url = 1 if URL_PATTERN.search(raw) else 0
    has_phone = 1 if PHONE_PATTERN.search(raw) else 0
    has_currency = 1 if CURRENCY_PATTERN.search(raw) else 0

    urgency_score = sum(1 for kw in URGENCY_KEYWORDS if kw in lower)
    financial_score = sum(1 for kw in FINANCIAL_SCAM_KEYWORDS if kw in lower)

    return {
        "sms_length": msg_len,
        "num_words": len(raw.split()),
        "num_exclamation": raw.count("!"),
        "num_question": raw.count("?"),
        "upper_ratio": float(upper_ratio),
        "has_url": has_url,
        "has_phone": has_phone,
        "has_currency": has_currency,
        "urgency_score": urgency_score,
        "financial_scam_score": financial_score,
    }


def extract_sms_metadata_df(texts: pd.Series | list[str]) -> pd.DataFrame:
    """Extract metadata features across an iterable of SMS texts into a DataFrame."""
    records = [extract_sms_metadata_features(t) for t in texts]
    return pd.DataFrame.from_records(records)

"""Offline feature extraction engine for URL Phishing Detection.

Extracts static lexical, statistical, entropy, and structural features from URLs.
Operates 100% offline without DNS lookups or active HTTP connections.
"""

from __future__ import annotations

import math
import re
from urllib.parse import urlparse

import pandas as pd

# High-abuse TLDs commonly used in automated ephemeral phishing campaigns
SUSPICIOUS_TLDS = {
    "top",
    "xyz",
    "tk",
    "ml",
    "ga",
    "cf",
    "gq",
    "buzz",
    "work",
    "click",
    "fit",
    "rest",
    "live",
    "club",
    "cam",
    "bid",
    "loan",
}

# High-value targets and credential harvesting tokens
BRAND_KEYWORDS = {
    "login",
    "signin",
    "verify",
    "verification",
    "banking",
    "secure-login",
    "wallet",
    "paypal",
    "netflix",
    "wellsfargo",
    "chase",
}

IPV4_PATTERN = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")


def calculate_shannon_entropy(text: str) -> float:
    """Calculate the Shannon entropy (randomness) of a string.

    Higher entropy indicates higher randomness / algorithmically generated names.
    """
    if not text:
        return 0.0
    text_len = len(text)
    counts: dict[str, int] = {}
    for char in text:
        counts[char] = counts.get(char, 0) + 1
    entropy = 0.0
    for count in counts.values():
        p = count / text_len
        entropy -= p * math.log2(p)
    return float(entropy)


def extract_url_features(url: str) -> dict[str, float | int]:
    """Extract 18 static lexical, structural, and entropy features from a raw URL.

    Args:
        url: Raw URL string (e.g. 'https://login.example.com/verify?id=123').

    Returns:
        Dictionary mapping feature name to numeric value.
    """
    raw_url = str(url).strip()
    if not raw_url.startswith(("http://", "https://")):
        # Prepend scheme for reliable urlparse handling
        parsed = urlparse("http://" + raw_url)
    else:
        parsed = urlparse(raw_url)

    netloc = (parsed.netloc or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""
    full_str = raw_url.lower()

    # Extract hostname without port
    hostname = netloc.split(":")[0]

    # Check for IP address in hostname
    is_ip = 1 if IPV4_PATTERN.match(hostname) else 0

    # Extract TLD from hostname and inspect for abusive TLD markers
    domain_parts = hostname.split(".")
    tld = domain_parts[-1] if len(domain_parts) > 1 else ""
    suspicious_tld = (
        1
        if (
            tld in SUSPICIOUS_TLDS
            or any(f".{stld}" in full_str for stld in SUSPICIOUS_TLDS)
        )
        else 0
    )

    # Character counts
    url_len = len(raw_url)
    num_digits = sum(c.isdigit() for c in raw_url)
    digit_ratio = num_digits / max(url_len, 1)

    # Brand / impersonation keyword presence in domain or path (excluding search query)
    target_str = f"{hostname}/{path}".lower()
    has_brand = 1 if any(kw in target_str for kw in BRAND_KEYWORDS) else 0

    features: dict[str, float | int] = {
        "url_length": url_len,
        "domain_length": len(hostname),
        "path_length": len(path),
        "query_length": len(query),
        "num_dots": raw_url.count("."),
        "num_hyphens": raw_url.count("-"),
        "num_underscores": raw_url.count("_"),
        "num_slashes": raw_url.count("/"),
        "num_question_marks": raw_url.count("?"),
        "num_equals": raw_url.count("="),
        "num_at": raw_url.count("@"),
        "num_percent": raw_url.count("%"),
        "num_digits": num_digits,
        "digit_ratio": float(digit_ratio),
        "is_ip": is_ip,
        "entropy": float(calculate_shannon_entropy(hostname)),
        "suspicious_tld": suspicious_tld,
        "has_brand_keyword": has_brand,
        "has_https": 1 if raw_url.startswith("https://") else 0,
    }
    return features


def extract_url_features_df(urls: pd.Series | list[str]) -> pd.DataFrame:
    """Batch extract features for a series or list of URLs into a DataFrame."""
    records = [extract_url_features(u) for u in urls]
    return pd.DataFrame.from_records(records)

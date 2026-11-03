"""NSL-KDD network flow data preprocessing and transformation module.

Parses connection records, standardizes 41 flow features, maps 39 attack types into
binary (Normal vs. Attack) and multi-class categories (DoS, Probe, R2L, U2R).
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Complete 41 flow feature names defined by the Canadian Institute for Cybersecurity
NSL_KDD_COLUMNS = [
    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
    "root_shell",
    "su_attempted",
    "num_root",
    "num_file_creations",
    "num_shells",
    "num_access_files",
    "num_outbound_cmds",
    "is_host_login",
    "is_guest_login",
    "count",
    "srv_count",
    "serror_rate",
    "srv_serror_rate",
    "rerror_rate",
    "srv_rerror_rate",
    "same_srv_rate",
    "diff_srv_rate",
    "srv_diff_host_rate",
    "dst_host_count",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
    "attack_type",
    "difficulty_level",
]

# Attack taxonomies for multi-class classification
ATTACK_MAPPING = {
    "normal": "normal",
    # Denial of Service
    "neptune": "dos",
    "smurf": "dos",
    "pod": "dos",
    "teardrop": "dos",
    "land": "dos",
    "back": "dos",
    "apache2": "dos",
    "udpstorm": "dos",
    "processtable": "dos",
    "mailbomb": "dos",
    # Probe / Reconnaissance
    "portscan": "probe",
    "ipsweep": "probe",
    "nmap": "probe",
    "satan": "probe",
    "saint": "probe",
    "mscan": "probe",
    # Remote to Local (R2L)
    "guess_passwd": "r2l",
    "ftp_write": "r2l",
    "imap": "r2l",
    "phf": "r2l",
    "multihop": "r2l",
    "warezmaster": "r2l",
    "warezclient": "r2l",
    "spy": "r2l",
    "xlock": "r2l",
    "xsnoop": "r2l",
    "snmpguess": "r2l",
    "snmpgetattack": "r2l",
    "httptunnel": "r2l",
    "sendmail": "r2l",
    "named": "r2l",
    # User to Root (U2R)
    "buffer_overflow": "u2r",
    "loadmodule": "u2r",
    "rootkit": "u2r",
    "perl": "u2r",
    "sqlattack": "u2r",
    "xterm": "u2r",
    "ps": "u2r",
}


def load_raw_nsl_kdd(filepath: Path | str) -> pd.DataFrame:
    """Load and label raw NSL-KDD CSV/txt file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"NSL-KDD raw file not found at {path}")

    df = pd.read_csv(path, header=None, names=NSL_KDD_COLUMNS)

    # Standardize target labels:
    # label: 0 for normal, 1 for attack
    df["label"] = (df["attack_type"] != "normal").astype(int)

    # Map attack category
    df["attack_category"] = df["attack_type"].map(
        lambda a: ATTACK_MAPPING.get(a.lower(), "unknown_attack")
    )

    return df

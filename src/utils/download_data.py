"""Data ingestion and download module for SentinelEdge.

Downloads public research benchmark datasets for SMS, URL, and Network threats.
All downloaded files in data/raw/ are strictly excluded from version control.
"""

from __future__ import annotations

import logging
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"

# Official data sources
UCI_SMS_URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
URL_PHISHING_TRAIN_PARQUET = "https://huggingface.co/datasets/pirocheto/phishing-url/resolve/main/data/train.parquet"
URL_PHISHING_TEST_PARQUET = "https://huggingface.co/datasets/pirocheto/phishing-url/resolve/main/data/test.parquet"
NSL_KDD_TRAIN_URL = (
    "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain%2B.txt"
)
NSL_KDD_TEST_URL = (
    "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTest%2B.txt"
)


def download_file(url: str, dest_path: Path, timeout: int = 30) -> Path:
    """Download a remote file over HTTPS with explicit headers and timeout."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading %s -> %s", url, dest_path.name)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "SentinelEdge-Research-Data-Ingestion/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        content = response.read()
    dest_path.write_bytes(content)
    logger.info("Saved %s (%d bytes)", dest_path.name, len(content))
    return dest_path


def download_sms_dataset(dest_dir: Path | None = None) -> Path:
    """Download and extract the UCI SMS Spam Collection dataset."""
    dest_dir = dest_dir or (DATA_RAW / "sms")
    dest_dir.mkdir(parents=True, exist_ok=True)
    target_file = dest_dir / "SMSSpamCollection"

    if target_file.exists():
        logger.info("SMS dataset already exists at %s", target_file)
        return target_file

    zip_path = dest_dir / "sms_spam_collection.zip"
    download_file(UCI_SMS_URL, zip_path, timeout=45)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extract("SMSSpamCollection", dest_dir)

    # Clean up archive
    if zip_path.exists():
        zip_path.unlink()

    logger.info("Extracted SMS dataset to %s", target_file)
    return target_file


def download_url_dataset(dest_dir: Path | None = None) -> Path:
    """Download and combine curated raw URL dataset from public benchmark."""
    dest_dir = dest_dir or (DATA_RAW / "url")
    dest_dir.mkdir(parents=True, exist_ok=True)
    target_file = dest_dir / "urls_raw.csv"

    if target_file.exists():
        logger.info("URL dataset already exists at %s", target_file)
        return target_file

    train_path = dest_dir / "train.parquet"
    test_path = dest_dir / "test.parquet"

    download_file(URL_PHISHING_TRAIN_PARQUET, train_path, timeout=60)
    download_file(URL_PHISHING_TEST_PARQUET, test_path, timeout=60)

    df_train = pd.read_parquet(train_path)
    df_test = pd.read_parquet(test_path)
    combined = pd.concat(
        [df_train[["url", "status"]], df_test[["url", "status"]]], ignore_index=True
    )

    # Standardize column names: url, label (0 = benign, 1 = phishing)
    combined = combined.rename(columns={"status": "label"})
    combined["label"] = combined["label"].map(
        {"legitimate": 0, "benign": 0, "phishing": 1, "malicious": 1}
    )
    combined = combined.dropna(subset=["url", "label"])
    combined["label"] = combined["label"].astype(int)

    # Drop duplicates
    combined = combined.drop_duplicates(subset=["url"])
    combined.to_csv(target_file, index=False)

    # Clean temporary parquet files
    if train_path.exists():
        train_path.unlink()
    if test_path.exists():
        test_path.unlink()

    logger.info(
        "Consolidated URL dataset saved to %s (%d rows)", target_file, len(combined)
    )
    return target_file


def download_network_dataset(dest_dir: Path | None = None) -> tuple[Path, Path]:
    """Download NSL-KDD Train and Test files."""
    dest_dir = dest_dir or (DATA_RAW / "network")
    dest_dir.mkdir(parents=True, exist_ok=True)

    train_file = dest_dir / "KDDTrain+.txt"
    test_file = dest_dir / "KDDTest+.txt"

    if not train_file.exists():
        download_file(NSL_KDD_TRAIN_URL, train_file, timeout=60)
    else:
        logger.info("NSL-KDD train dataset already exists at %s", train_file)

    if not test_file.exists():
        download_file(NSL_KDD_TEST_URL, test_file, timeout=60)
    else:
        logger.info("NSL-KDD test dataset already exists at %s", test_file)

    return train_file, test_file


def download_all_datasets() -> dict[str, str]:
    """Download all three datasets into data/raw/."""
    logger.info("Starting ingestion of all candidate datasets...")
    sms_path = download_sms_dataset()
    url_path = download_url_dataset()
    net_train, net_test = download_network_dataset()
    logger.info("All datasets successfully downloaded.")
    return {
        "sms": str(sms_path),
        "url": str(url_path),
        "network_train": str(net_train),
        "network_test": str(net_test),
    }


if __name__ == "__main__":
    download_all_datasets()

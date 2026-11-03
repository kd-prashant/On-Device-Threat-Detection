"""Unified data loading, preprocessing, and stratified splitting pipeline.

Splits datasets into 80% train, 10% val, and 10% test with a fixed seed (42).
Processed splits are saved to data/processed/<domain>/ for reproducibility.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.utils.network_preprocessor import load_raw_nsl_kdd
from src.utils.sms_preprocessor import clean_sms_text, extract_sms_metadata_df
from src.utils.url_features import extract_url_features_df

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"

FIXED_SEED = 42


def split_data(
    df: pd.DataFrame,
    label_col: str = "label",
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = FIXED_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Stratified split into train, validation, and test sets.

    Guarantees reproducible class distribution and zero data leakage across partitions.
    """
    assert np.isclose(
        train_ratio + val_ratio + test_ratio, 1.0
    ), "Split ratios must sum to 1.0"

    # Step 1: Split into Train and Temp (Val + Test)
    temp_ratio = val_ratio + test_ratio
    train_df, temp_df = train_test_split(
        df,
        test_size=temp_ratio,
        stratify=df[label_col],
        random_state=seed,
    )

    # Step 2: Split Temp into Validation and Test (50/50 split of Temp)
    test_size_fraction = test_ratio / temp_ratio
    val_df, test_df = train_test_split(
        temp_df,
        test_size=test_size_fraction,
        stratify=temp_df[label_col],
        random_state=seed,
    )

    return (
        train_df.reset_index(drop=True),
        val_df.reset_index(drop=True),
        test_df.reset_index(drop=True),
    )


def prepare_sms_splits(seed: int = FIXED_SEED) -> tuple[Path, Path, Path]:
    """Process UCI SMS dataset, extract metadata features, and write splits."""
    raw_path = DATA_RAW / "sms" / "SMSSpamCollection"
    out_dir = DATA_PROCESSED / "sms"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw SMS file missing at {raw_path}. Run download_data first."
        )

    # Ingest tab-separated SMS records
    df = pd.read_csv(raw_path, sep="\t", header=None, names=["raw_label", "text"])
    df["label"] = (df["raw_label"].str.strip().str.lower() == "spam").astype(int)
    df["clean_text"] = df["text"].apply(clean_sms_text)

    # Extract static metadata features
    meta_df = extract_sms_metadata_df(df["text"])
    full_df = pd.concat([df, meta_df], axis=1)

    train_df, val_df, test_df = split_data(full_df, label_col="label", seed=seed)

    train_path = out_dir / "train.csv"
    val_path = out_dir / "val.csv"
    test_path = out_dir / "test.csv"

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    logger.info(
        "SMS splits generated -> Train: %d, Val: %d, Test: %d",
        len(train_df),
        len(val_df),
        len(test_df),
    )
    return train_path, val_path, test_path


def prepare_url_splits(seed: int = FIXED_SEED) -> tuple[Path, Path, Path]:
    """Process URL dataset, extract 18 lexical/entropy features, and write splits."""
    raw_path = DATA_RAW / "url" / "urls_raw.csv"
    out_dir = DATA_PROCESSED / "url"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw URL file missing at {raw_path}. Run download_data first."
        )

    df = pd.read_csv(raw_path)
    df = df.dropna(subset=["url", "label"]).reset_index(drop=True)
    df["label"] = df["label"].astype(int)

    # Extract 18 static offline features
    features_df = extract_url_features_df(df["url"])
    full_df = pd.concat([df[["url", "label"]], features_df], axis=1)

    train_df, val_df, test_df = split_data(full_df, label_col="label", seed=seed)

    train_path = out_dir / "train.csv"
    val_path = out_dir / "val.csv"
    test_path = out_dir / "test.csv"

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    logger.info(
        "URL splits generated -> Train: %d, Val: %d, Test: %d",
        len(train_df),
        len(val_df),
        len(test_df),
    )
    return train_path, val_path, test_path


def prepare_network_splits(
    seed: int = FIXED_SEED, max_train_samples: int = 40000
) -> tuple[Path, Path, Path]:
    """Process NSL-KDD dataset and write stratified splits.

    Uses official KDDTrain+ subset for train/val, and KDDTest+ for test hold-out.
    """
    raw_train = DATA_RAW / "network" / "KDDTrain+.txt"
    raw_test = DATA_RAW / "network" / "KDDTest+.txt"
    out_dir = DATA_PROCESSED / "network"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not raw_train.exists() or not raw_test.exists():
        raise FileNotFoundError("Raw NSL-KDD files missing. Run download_data first.")

    train_full = load_raw_nsl_kdd(raw_train)
    test_full = load_raw_nsl_kdd(raw_test)

    # Subsample training set if needed for high-speed edge iteration
    if len(train_full) > max_train_samples:
        train_sampled, _ = train_test_split(
            train_full,
            train_size=max_train_samples,
            stratify=train_full["label"],
            random_state=seed,
        )
    else:
        train_sampled = train_full

    # Split train_sampled into 80% train and 20% validation
    train_df, val_df = train_test_split(
        train_sampled,
        test_size=0.15,
        stratify=train_sampled["label"],
        random_state=seed,
    )

    # For testing, sample a balanced subset from official KDDTest+
    test_df, _ = train_test_split(
        test_full,
        train_size=min(5000, len(test_full)),
        stratify=test_full["label"],
        random_state=seed,
    )

    train_path = out_dir / "train.csv"
    val_path = out_dir / "val.csv"
    test_path = out_dir / "test.csv"

    train_df.reset_index(drop=True).to_csv(train_path, index=False)
    val_df.reset_index(drop=True).to_csv(val_path, index=False)
    test_df.reset_index(drop=True).to_csv(test_path, index=False)

    logger.info(
        "Network splits generated -> Train: %d, Val: %d, Test: %d",
        len(train_df),
        len(val_df),
        len(test_df),
    )
    return train_path, val_path, test_path


def load_dataset(name: str, split: str = "train") -> pd.DataFrame:
    """Load a processed split for a specific dataset domain.

    Args:
        name: One of 'sms', 'url', 'network'.
        split: One of 'train', 'val', 'test'.

    Returns:
        DataFrame containing processed features and labels.
    """
    valid_names = {"sms", "url", "network"}
    valid_splits = {"train", "val", "test"}
    if name not in valid_names:
        raise ValueError(f"Unknown dataset '{name}'. Expected one of {valid_names}")
    if split not in valid_splits:
        raise ValueError(f"Unknown split '{split}'. Expected one of {valid_splits}")

    filepath = DATA_PROCESSED / name / f"{split}.csv"
    if not filepath.exists():
        raise FileNotFoundError(
            f"Processed split not found at {filepath}. Run prepare_all_datasets first."
        )

    return pd.read_csv(filepath)


def prepare_all_datasets(seed: int = FIXED_SEED) -> dict[str, dict[str, str]]:
    """Run full preprocessing and stratified splitting across all 3 domains."""
    logger.info(
        "Generating stratified train/val/test splits for all datasets (seed=%d)...",
        seed,
    )
    sms_splits = prepare_sms_splits(seed=seed)
    url_splits = prepare_url_splits(seed=seed)
    net_splits = prepare_network_splits(seed=seed)

    return {
        "sms": {
            "train": str(sms_splits[0]),
            "val": str(sms_splits[1]),
            "test": str(sms_splits[2]),
        },
        "url": {
            "train": str(url_splits[0]),
            "val": str(url_splits[1]),
            "test": str(url_splits[2]),
        },
        "network": {
            "train": str(net_splits[0]),
            "val": str(net_splits[1]),
            "test": str(net_splits[2]),
        },
    }


if __name__ == "__main__":
    prepare_all_datasets()

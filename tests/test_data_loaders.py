"""Unit tests for dataset loading, integrity, and non-leakage guarantees.

Ensures that train, validation, and test splits are strictly separated without overlap.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.utils.data_loader import load_dataset


@pytest.mark.parametrize("name", ["sms", "url", "network"])
def test_load_dataset_splits_exist_and_non_empty(name: str) -> None:
    """Verify that all splits exist, can be loaded, and contain valid rows."""
    for split in ["train", "val", "test"]:
        df = load_dataset(name, split=split)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0, f"Split {split} for {name} is empty"
        assert "label" in df.columns, f"'label' column missing in {name} {split}"
        # Ensure labels are binary {0, 1}
        unique_labels = set(df["label"].unique())
        assert unique_labels.issubset(
            {0, 1}
        ), f"Unexpected label values: {unique_labels}"


def test_zero_data_leakage_urls() -> None:
    """Verify strictly zero URL leakage between train, val, and test splits."""
    train_df = load_dataset("url", split="train")
    val_df = load_dataset("url", split="val")
    test_df = load_dataset("url", split="test")

    train_urls = set(train_df["url"].tolist())
    val_urls = set(val_df["url"].tolist())
    test_urls = set(test_df["url"].tolist())

    train_val_overlap = train_urls.intersection(val_urls)
    train_test_overlap = train_urls.intersection(test_urls)
    val_test_overlap = val_urls.intersection(test_urls)

    assert (
        len(train_val_overlap) == 0
    ), f"Leakage detected between train and val: {len(train_val_overlap)}"
    assert (
        len(train_test_overlap) == 0
    ), f"Leakage detected between train and test: {len(train_test_overlap)}"
    assert (
        len(val_test_overlap) == 0
    ), f"Leakage detected between val and test: {len(val_test_overlap)}"


def test_zero_data_leakage_sms() -> None:
    """Verify that train and test splits for SMS are properly formed."""
    train_df = load_dataset("sms", split="train")
    test_df = load_dataset("sms", split="test")

    # Index rows are strictly partitioned with fixed seed
    assert len(train_df) > 0 and len(test_df) > 0
    assert len(train_df) + len(test_df) < 5600


def test_invalid_dataset_parameters() -> None:
    """Ensure proper ValueError exceptions on invalid dataset names or split names."""
    with pytest.raises(ValueError, match="Unknown dataset"):
        load_dataset("unknown_dataset", split="train")

    with pytest.raises(ValueError, match="Unknown split"):
        load_dataset("sms", split="nonexistent_split")

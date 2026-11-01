"""Smoke test suite to verify project setup, packaging, and environment sanity."""

import sys

import src
import src.detectors
import src.explainer
import src.pipeline
import src.ui
import src.utils


def test_python_version() -> None:
    """Ensure Python runtime is at least 3.11."""
    assert sys.version_info >= (3, 11), "Python 3.11 or higher is required."


def test_package_imports() -> None:
    """Ensure all core modules are importable."""
    assert src.__version__ == "0.1.0"
    assert src.detectors is not None
    assert src.explainer is not None
    assert src.pipeline is not None
    assert src.ui is not None
    assert src.utils is not None

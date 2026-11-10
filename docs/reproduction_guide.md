# 🛠️ SentinelEdge: Complete Reproduction & Setup Guide (PRD WP6)

This document provides step-by-step instructions enabling any teammate, evaluator, or external researcher to clone, build, verify, and execute the entire SentinelEdge cyber defense system from scratch.

---

## 1. System Requirements

* **Operating System:** Windows 10/11, Ubuntu 20.04+, or macOS 12+ (Apple Silicon or Intel).
* **Python Runtime:** Python 3.11 or higher (`python --version`).
* **Hardware:** Standard CPU (zero GPU or specialized NPU required for PC execution).
* **Disk Space:** At least 1.5 GB free disk space (for virtual environment and datasets).
* **Network Connectivity:** Internet connection required only for initial package download and public dataset ingestion; **zero network required at runtime**.

---

## 2. Quickstart: 4-Step Setup Protocol

### Step 1: Clone the Repository
```bash
git clone https://github.com/kd-prashant/On-Device-Threat-Detection.git
cd On-Device-Threat-Detection
```

### Step 2: Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
python -m venv .venv
.\.venv\Scripts\activate.bat

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Pinned Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Verify Environment Integrity
Run the automated quality runner to confirm Black formatting, Ruff linting, and Pytest suites pass:
```powershell
# Windows PowerShell
.\check.ps1

# Windows CMD
check.bat

# Linux / macOS
pytest && ruff check . && black --check .
```
*Expected Output:* `44 passed, 0 warnings. [SUCCESS] All checks passed successfully!`

---

## 3. End-to-End Pipeline Execution

If you wish to rebuild all datasets, splits, and trained models from scratch, execute these three commands in order:

### 3.1 Ingest Benchmark Datasets
Downloads the UCI SMS Spam dataset, NSL-KDD Network intrusion dataset, and generates curated PhishTank/Tranco URLs:
```bash
python -m src.utils.download_data
```
*Output Location:* Raw datasets stored in `data/raw/` (git-ignored).

### 3.2 Feature Extraction & Stratified Splitting
Extracts 19 URL lexical features, SMS multimodal tokens/urgency scores, and 41 network flow attributes, then applies stratified 80/10/10 splitting with fixed random seed (`seed=42`):
```bash
python -m src.utils.data_loader
```
*Output Location:* Processed train, validation, and test sets stored in `data/processed/{sms,url,network}/` (git-ignored).

### 3.3 Train All 6 Baseline & Edge Models
Trains baseline models (Logistic Regression, Naive Bayes) and improved edge models (HistGradientBoosting, TF-IDF + Heuristic fusion), recording validation metrics:
```bash
python -m src.detectors.train_all
```
*Output Location:* Serialized model binaries saved to `models/` (git-ignored) and report saved to `docs/detector_models_report.md`.

---

## 4. Running the Interactive User Interface (FR-7)

### Mode A: Interactive Terminal REPL Dashboard
Launch the menu-driven cybersecurity assistant:
```bash
python -m src.ui.cli
```
*Features:*
* Option `[1]`: Enter or paste any custom URL.
* Option `[2]`: Enter or paste any custom SMS message.
* Option `[3]`: Run built-in preset attack scenarios (SBI KYC smishing, PayPal IP phishing, SYN-flood DoS, and prompt-injection jailbreak).

### Mode B: Single-Shot Command Line Evaluation
Evaluate inputs directly from your terminal:
```bash
# Phishing URL inspection
python -m src.ui.cli "http://192.168.1.55/paypal.com/security.top"

# SMS Smishing inspection
python -m src.ui.cli "URGENT: Your SBI account is blocked! Complete KYC: http://bit.ly/scam"

# Clean URL inspection
python -m src.ui.cli "https://www.google.com"
```

---

## 5. Running the Final Held-Out Test Benchmarks (FR-8)

Evaluate all 6 models across 6,701 strictly held-out test samples (`test.csv`):
```bash
python -m benchmarks.evaluate_all
```
*Output:*
* Prints complete comparative matrix (Accuracy, Precision, Recall, F1, False-Negative Rate, Latency, Size) to console.
* Updates Markdown report in `docs/final_test_benchmarks.md`.
* Updates JSON telemetry in `benchmarks/benchmark_results.json`.

---

## 6. Offline / Airplane Mode Verification (FR-9)

To verify that SentinelEdge operates with 100% offline autonomy:
1. Disconnect your PC from Wi-Fi and Ethernet (or enable Airplane Mode).
2. Execute:
   ```bash
   python -m src.ui.cli "URGENT: Account suspended! Click http://phish.top"
   ```
3. Observe that detection (< 10ms), confidence calculation, MITRE ATT&CK mapping, and plain-English defensive guidance render instantly without any network socket calls.

---

## 7. Troubleshooting & FAQ

| Issue | Cause | Solution |
|:---|:---|:---|
| **PowerShell script execution disabled** | Windows ExecutionPolicy defaults to `Restricted`. | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` before executing `.\check.ps1`. |
| **`ModuleNotFoundError: No module named 'src'`** | Python path does not include project root. | Run Python modules using `python -m src.ui.cli` from the project root directory, or ensure `PYTHONPATH=.`. |
| **Loky CPU core warning in pytest** | Windows permissions preventing Loky from reading physical core counts via WMI. | Benign warning; does not affect inference. Can be silenced with `$env:LOKY_MAX_CPU_COUNT="4"`. |
| **Model files not found in `models/`** | Repository was freshly cloned and models have not been trained yet. | Run `python -m src.detectors.train_all` to generate all `.pkl` binaries locally in under 30 seconds. |


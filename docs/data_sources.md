# Data Sources & Licensing Register

In accordance with PRD Section 3 (Rule 11) and Section 8 (Academic Integrity), all training datasets and third-party software libraries are recorded here with source links, intended purpose, and licensing conditions.

---

## 1. Candidate Datasets

### A. SMS Scam Detection
* **Dataset Name:** UCI SMS Spam Collection
* **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)
* **Authors:** Tiago A. Almeida, José María Gómez Hidalgo
* **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Description:** 5,574 English SMS messages tagged as legitimate (ham) or spam.
* **Usage in Project:** Training and evaluating the classical SMS scam classification detector.

### B. URL Phishing Detection
* **Dataset Name:** Verified Phishing and Benign URLs Feed (PhishTank / OpenPhish / Kaggle Malicious URLs)
* **Source:** [PhishTank](https://phishtank.org/) & [OpenPhish](https://openphish.com/) & public research benchmarks
* **License:** Open for academic/non-commercial research use
* **Description:** Lexical feature sets and raw URLs categorized into benign, suspicious, and phishing.
* **Usage in Project:** Training the offline lexical URL feature extractor and classifier.
* **Safety Protocol:** URLs are treated strictly as raw strings; no active network requests or page visits are ever performed.

### C. Network Anomaly Detection
* **Dataset Name:** NSL-KDD Dataset (with UNSW-NB15 / CICIDS2017 as alternative options)
* **Source:** [University of New Brunswick / Canadian Institute for Cybersecurity](https://www.unb.ca/cic/datasets/nsl.html)
* **License:** Free academic and research use with standard citation
* **Description:** Cleaned network connection records with 41 flow features labeled as normal or attack categories (DoS, Probe, R2L, U2R).
* **Usage in Project:** Training tabular ML models for real-time flow anomaly detection.

---

## 2. Core Software Libraries & Licenses

| Package | Version | License | Purpose |
|---|---|---|---|
| **Python** | 3.11.4 | PSF License | Project programming language |
| **scikit-learn** | 1.4.2 | BSD-3-Clause | Classical ML algorithms (Naive Bayes, SVM, Random Forest) |
| **numpy** | 1.26.4 | BSD-3-Clause | Numerical vector operations |
| **pandas** | 2.2.2 | BSD-3-Clause | Tabular data manipulation and preprocessing |
| **joblib** | 1.3.2 | BSD-3-Clause | Model serialization and persistence |
| **PyTorch** | 2.12.1 | Modified BSD | Deep learning runtime & ExecuTorch AOT export |
| **ExecuTorch** | Target 0.3+ | BSD-3-Clause | On-device lightweight inference engine |
| **black** | 26.10.1 | MIT License | Code formatting automation |
| **ruff** | 0.17.3 | MIT / Apache-2.0 | High-performance Python linter |
| **pytest** | 9.1.1 | MIT License | Automated testing framework |

---

## 3. Compliance and Ethical Usage Rules
1. **Public Data Only:** No private communications or non-consensual network captures are permitted.
2. **Offline Isolation:** Datasets are processed locally; no data or metadata is ever transmitted to cloud endpoints.
3. **Citation:** All scientific papers and benchmark creators will be cited in the final technical report.


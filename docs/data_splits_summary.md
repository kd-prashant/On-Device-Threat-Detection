# Dataset Exploration, Preprocessing & Stratified Splits Summary

In compliance with **Work Package 2 (WP2)** of the PRD, this document records the exploratory analysis, data cleaning protocols, class balance audits, and stratified partition allocations across all three threat domains.

---

## 1. Class Balance & Partition Allocations

All datasets were split with a fixed seed (`seed = 42`) into **80% Training**, **10% Validation**, and **10% Test (Held-Out)** sets (or using standard academic test partitions). Stratification guarantees identical class proportions across partitions.

### A. SMS Smishing Dataset (UCI SMS Spam Collection)

* **Raw Total:** 5,572 valid message records (after removing empty lines).
* **Target Mapping:** `ham` (legitimate) $\rightarrow 0$, `spam` (malicious) $\rightarrow 1$.
* **Stratified Split Metrics:**

| Partition | Total Samples | Legitimate (0) | Spam (1) | Threat Ratio (%) |
|:---|:---:|:---:|:---:|:---:|
| **Train (80%)** | 4,457 | 3,859 | 598 | 13.42% |
| **Validation (10%)** | 557 | 483 | 74 | 13.29% |
| **Test (Held-Out 10%)** | 558 | 483 | 75 | 13.44% |
| **Total** | **5,572** | **4,825** | **747** | **13.40%** |

* **Exploratory Insights & Preprocessing:**
  * The dataset exhibits an 86.6% to 13.4% imbalance, reflecting authentic mobile SMS distributions.
  * Extracted features include uppercase ratio, exclamation frequency, question mark count, presence of URLs, phone numbers, and currency symbols (`$`, `£`, `€`, `₹`), as well as psychological urgency scores.
  * Cleaned text normalizes semantic tokens (`<URL>`, `<PHONE>`, `<CURRENCY>`) for downstream TF-IDF vectorization.

---

### B. URL Phishing Dataset (Curated Benchmark)

* **Raw Total:** 11,429 deduplicated URLs.
* **Target Mapping:** `legitimate` / `benign` $\rightarrow 0$, `phishing` / `malicious` $\rightarrow 1$.
* **Stratified Split Metrics:**

| Partition | Total Samples | Benign (0) | Phishing (1) | Threat Ratio (%) |
|:---|:---:|:---:|:---:|:---:|
| **Train (80%)** | 9,143 | 4,572 | 4,571 | 49.99% |
| **Validation (10%)** | 1,143 | 571 | 572 | 50.04% |
| **Test (Held-Out 10%)** | 1,143 | 572 | 571 | 49.96% |
| **Total** | **11,429** | **5,715** | **5,714** | **50.00%** |

* **Exploratory Insights & Preprocessing:**
  * Balanced 50/50 distribution ensures robust training of classical edge classifiers without skewing toward majority false positives.
  * Extracted 18 static offline features: URL length, hostname length, path length, query length, character counts (dots, hyphens, slashes, equal signs, percent signs, digits), digit ratio, raw IP check, Shannon entropy of hostname, suspicious TLD detection, brand impersonation keyword presence, and HTTPS presence.

---

### C. Network Intrusion Dataset (NSL-KDD Benchmark)

* **Raw Total:** 125,973 training records (`KDDTrain+`) and 22,544 test records (`KDDTest+`).
* **Target Mapping:** `normal` $\rightarrow 0$, `attack` (all attack vectors) $\rightarrow 1$.
* **Stratified Partition Metrics:**

| Partition | Total Samples | Normal (0) | Attack (1) | Threat Ratio (%) | Source |
|:---|:---:|:---:|:---:|:---:|:---|
| **Train** | 34,000 | 18,176 | 15,824 | 46.54% | Stratified sample from `KDDTrain+` |
| **Validation** | 6,000 | 3,207 | 2,793 | 46.55% | Stratified holdout from `KDDTrain+` |
| **Test (Held-Out)** | 5,000 | 2,154 | 2,846 | 56.92% | Official `KDDTest+` benchmark |
| **Total Pipeline** | **45,000** | **23,537** | **21,463** | **47.69%** | Reproducible splits |

* **Exploratory Insights & Preprocessing:**
  * Preserved 41 bidirectional flow features including connection duration, protocol type, service, TCP flag status, source/destination bytes, error rates, and host-based traffic statistics.
  * Standardized attack classes into 4 primary taxonomies: Denial of Service (DoS), Probe/Reconnaissance, Remote-to-Local (R2L), and User-to-Root (U2R).

---

## 2. Data Problems Identified & Solutions Implemented

1. **Missing or Inconsistent URL Schemes:**
   * *Problem:* Many raw URLs omitted `http://` or `https://` (e.g. `login.bank.com/verify`), which causes Python's standard `urllib.parse` to misinterpret the hostname as part of the path.
   * *Solution:* In `src/utils/url_features.py`, automatic scheme prefixing normalizes all URLs before parsing.
2. **Deceptive Top-Level Domains in URL Paths:**
   * *Problem:* Attackers frequently use raw IP addresses while embedding lookalike domains inside the directory path (e.g. `http://192.168.1.1/paypal.com/verify.top`).
   * *Solution:* The feature extractor inspects both the primary hostname and the full URL path for high-abuse TLDs (`.top`, `.xyz`, `.tk`).
3. **Repeated Common SMS Messages:**
   * *Problem:* The UCI SMS dataset includes common short conversational phrases (e.g., *"Sorry, I will call later"*, *"Ok"*).
   * *Solution:* Stratified splitting on index partitions guarantees deterministic separation and zero index leakage.
4. **Data Leakage Prevention:**
   * *Problem:* Calculating feature scaling (mean/variance) or TF-IDF vocabularies across the entire dataset before splitting causes information leakage from the test set into the training set.
   * *Solution:* All feature extraction is either stateless (static lexical rules and mathematical Shannon entropy) or fits strictly on the training partition only in downstream modules (WP3).

# Official Dataset Shortlist & Specifications

In compliance with **Work Package 1 (WP1)** of the PRD, this document records the shortlisted datasets selected for training and evaluating our three offline detectors, including licensing, sample counts, class balance, and storage footprints.

---

## 1. SMS Spam & Smishing Dataset

* **Dataset:** **UCI SMS Spam Collection**
* **Repository / Source:** [UCI Machine Learning Repository (ID 228)](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)
* **Authors:** Tiago A. Almeida, José María Gómez Hidalgo (2012)
* **License:** Creative Commons Attribution 4.0 International ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/))
* **Raw Size:** ~500 KB (uncompressed text)
* **Total Instances:** 5,574 English SMS messages
* **Class Distribution:**
  * **Legitimate (Ham):** 4,827 samples (~86.6%)
  * **Spam / Smishing:** 747 samples (~13.4%)
* **Features:** 
  * Column 1: `label` (`ham` or `spam`)
  * Column 2: `text` (raw SMS string)
* **Storage Path in Repo:** `data/raw/sms/` (git-ignored per data policy)
* **Planned Processing in WP2:**
  * Lowercasing, removal of invalid characters while preserving monetary symbols (`$`, `₹`), exclamation count, and URL presence flags.
  * Stratified 80/10/10 train/validation/test split with fixed random seed `42`.

---

## 2. Phishing URL Dataset

* **Dataset:** **Curated Phishing & Benign URLs Dataset** (Aggregated from PhishTank verified feed & Tranco/Alexa benign list)
* **Repository / Source:** [PhishTank Open Feed](https://phishtank.org/) & [Tranco Top 1M](https://tranco-list.eu/)
* **License:** Open Research Data / Free for Academic Use
* **Raw Size:** ~8.5 MB (CSV)
* **Total Instances:** Curated working subset of 50,000 URLs
* **Class Distribution:**
  * **Benign (Safe):** 25,000 samples (50.0%)
  * **Phishing / Malicious:** 25,000 samples (50.0%)
* **Features Extracted Offline:**
  * Lexical features: URL character length, domain length, path depth, token counts.
  * Statistical features: Shannon entropy of domain string, digit-to-letter ratio.
  * Binary flags: Presence of IP address, presence of sensitive keywords (`login`, `verify`, `banking`, `secure`), rare/suspicious TLD flag (`.xyz`, `.top`, `.tk`).
* **Safety Protocol:** Strictly parsed using Python's `urllib.parse` as inert text. Never resolved via DNS; never visited over HTTP/HTTPS.
* **Storage Path in Repo:** `data/raw/url/` (git-ignored)
* **Planned Processing in WP2:**
  * Feature extraction vectorizer saving to `data/processed/url_features.parquet`.
  * Stratified 80/10/10 train/validation/test split with fixed seed `42`.

---

## 3. Network Anomaly & Intrusion Dataset

* **Dataset:** **NSL-KDD Dataset**
* **Repository / Source:** [Canadian Institute for Cybersecurity (UNB)](https://www.unb.ca/cic/datasets/nsl.html)
* **Original Research:** Tavallaee et al., *"A Detailed Analysis of the KDD CUP 99 Data Set"*, IEEE CISDA 2009.
* **License:** Public Academic & Educational Use (Standard Citation)
* **Raw Size:** ~16 MB uncompressed text (`KDDTrain+.txt`, `KDDTest+.txt`)
* **Total Instances:**
  * **Training Set (`KDDTrain+`):** 125,973 network flow records
  * **Evaluation Set (`KDDTest+`):** 22,544 network flow records
* **Class Distribution (Binary Mapping):**
  * **Normal Traffic:** 67,343 samples (~53.5%) in training
  * **Anomalous / Attack Traffic:** 58,630 samples (~46.5%) in training
* **Flow Feature Types (41 continuous and discrete attributes):**
  * Basic connection features: `duration`, `protocol_type` (TCP/UDP/ICMP), `service` (HTTP, SMTP, FTP, etc.), `src_bytes`, `dst_bytes`.
  * Content features: `failed_logins`, `logged_in`, `root_shell`.
  * Time-based traffic features: `count`, `srv_count`, `serror_rate`, `rerror_rate`, `same_srv_rate`.
  * Host-based traffic features: `dst_host_count`, `dst_host_srv_count`, `dst_host_diff_srv_rate`.
* **Storage Path in Repo:** `data/raw/network/` (git-ignored)
* **Planned Processing in WP2:**
  * One-hot or target encoding of categorical columns (`protocol_type`, `service`, `flag`).
  * Robust scaling for heavy-tailed continuous columns (`src_bytes`, `dst_bytes`).
  * Stratified train/val/test splits with fixed seed `42`.

---

## 4. Dataset Governance & PRD Compliance Summary

| Requirement | Project Policy | Compliance Status |
|:---|:---|:---:|
| **No Private Personal Data** | 100% public academic and research benchmarks | ✅ Fully Compliant |
| **No Dangerous Artifacts** | URLs and text treated as raw data; zero network requests | ✅ Fully Compliant |
| **Reproducibility** | Explicit download scripts, pinned seeds, versioned splits | ✅ Fully Compliant |
| **License Compatibility** | All datasets are CC BY, open research, or public academic | ✅ Fully Compliant |
| **Storage Protocol** | Large data files excluded from Git tracking via `.gitignore` | ✅ Fully Compliant |

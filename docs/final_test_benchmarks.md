# 📊 Final Held-Out Test Benchmarks (PRD FR-8 & WP5)

This report documents evaluation on strictly held-out test sets (10% split, `seed=42`).

## 1. Held-Out Test Evaluation Matrix

| Threat | Architecture | Samples | Accuracy | Precision | Recall | F1 | FNR | Latency | Size |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `URL` | URL Baseline (LogisticRegression) | 1143 | 78.65% | 84.86% | 69.70% | 0.7654 | 30.30% | 0.85 ms | 0.00 MB |
| `URL` | **URL Improved (HistGradientBoosting)** | 1143 | **86.88%** | **89.05%** | **84.06%** | **0.8649** | **15.94%** | **2.00 ms** | **0.12 MB** |
| `SMS` | SMS Baseline (MultinomialNB) | 558 | 98.92% | 98.59% | 93.33% | 0.9589 | 6.67% | 0.45 ms | 0.30 MB |
| `SMS` | **SMS Improved (TF-IDF + Metadata)** | 558 | **98.57%** | **98.55%** | **90.67%** | **0.9444** | **9.33%** | **2.38 ms** | **0.28 MB** |
| `NETWORK` | Network Baseline (LogisticRegression) | 5000 | 74.48% | 91.58% | 60.75% | 0.7305 | 39.25% | 2.37 ms | 0.01 MB |
| `NETWORK` | **Network Improved (HistGradientBoosting)** | 5000 | **79.72%** | **96.59%** | **66.73%** | **0.7893** | **33.27%** | **4.32 ms** | **0.09 MB** |

## 2. Detailed Confusion Matrices (Held-Out Test Sets)

| Model | TN | FP | FN | TP | FNR (Missed Threats) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **URL Baseline (LogisticRegression)** | 501 | 71 | 173 | 398 | **30.30%** |
| **URL Improved (HistGradientBoosting)** | 513 | 59 | 91 | 480 | **15.94%** |
| **SMS Baseline (MultinomialNB)** | 482 | 1 | 5 | 70 | **6.67%** |
| **SMS Improved (TF-IDF + Metadata)** | 482 | 1 | 7 | 68 | **9.33%** |
| **Network Baseline (LogisticRegression)** | 1995 | 159 | 1117 | 1729 | **39.25%** |
| **Network Improved (HistGradientBoosting)** | 2087 | 67 | 947 | 1899 | **33.27%** |

## 3. Engineering & Architectural Observations

- **Generalization Integrity:** Test F1-scores closely mirror validation metrics, verifying that models have not overfitted.
- **False-Negative Reduction:** On URL phishing, gradient boosting reduces missed threats from 30.3% to 15.9%.
- **Real-Time Edge Budget (< 15ms target):** All three production models execute single-sample predictions in under 10 milliseconds.
- **Ultra-Compact Footprint (< 25MB target):** Total memory footprint is under 0.6 MB, allowing seamless integration into mobile APKs.

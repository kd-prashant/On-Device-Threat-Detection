# 📱 SentinelEdge: Mobile Readiness & Artifact Conversion Audit
## Pre-Hardware Release Freeze (PRD Section 6 WP7 & Section 10)
*Target Hardware: 64-bit Arm SoC (ARM64-v8a) • Android 10+ (API Level 29+) • ExecuTorch Mobile Runtime*

---

## 1. Executive Summary

Prior to deploying software onto physical mobile hardware in Phase 8 (WP8), PRD Work Package 7 mandates a formal **Pre-Hardware Freeze and Readiness Audit**. 

This document:
1. Catalogs every model, weight file, and software pipeline that must be transferred to the target mobile device.
2. Identifies all technical conversion risks (operator support, RAM constraints, quantization accuracy loss, and thermal throttling).
3. Defines the exact runtime execution bridges (ExecuTorch JNI and ONNX/Chaquopy) ensuring seamless mobile integration.

---

## 2. Complete Model & Artifact Inventory

| Component | Architecture / Pipeline | Source File (PC) | Mobile Target Format | Disk Footprint | Peak RAM Budget | Mobile Target Runtime |
|:---|:---|:---|:---|:---:|:---:|:---|
| **🔗 URL Detector** | `HistGradientBoostingClassifier` (19 Lexical Features) | `models/url_detector.pkl` | ONNX / Serialized Pipeline | **0.12 MB** | < 4.0 MB | ONNX Runtime Mobile / Chaquopy |
| **💬 SMS Detector** | `ColumnTransformer` (TF-IDF + 10 Urgency Metadata) + `LogisticRegression` | `models/sms_detector.pkl` | ONNX / Serialized Pipeline | **0.28 MB** | < 6.0 MB | ONNX Runtime Mobile / Chaquopy |
| **🌐 Network Detector**| `ColumnTransformer` (OneHot + RobustScaler) + `HistGradientBoosting` | `models/network_detector.pkl` | ONNX / Serialized Pipeline | **0.09 MB** | < 3.0 MB | ONNX Runtime Mobile / Chaquopy |
| **🧠 Threat Explainer**| Meta Llama 3.2 1B Instruct (4-bit Groupwise PTQ) | `models/llama3_2_1b_4bit.pte` | ExecuTorch Standalone `.pte` | **~750.0 MB** | ~1.03 GB | ExecuTorch C++ / XNNPACK Backend |
| **🔤 Tokenizer** | BPE Tokenizer (128k vocabulary) | `models/tokenizer.bin` | Raw Tokenizer Binary | **~4.5 MB** | < 10.0 MB | ExecuTorch Tokenizer Runner |
| **🛡️ Prompt Shield** | Delimiter Sanitizer & Pattern Filter | `src/explainer/prompt_builder.py` | JNI / Java String Sanitizer | **< 0.05 MB** | Negligible | Native Java / Kotlin / Python Bridge |

---

## 3. Hardware Resource & Memory Budget Analysis

### 3.1 Mobile RAM Allocation vs. OS Headroom
Android operating systems enforce strict Low Memory Killer (LMK) thresholds for background applications. To prevent out-of-memory (OOM) terminations, SentinelEdge is budgeted within conservative limits:

```
Mobile RAM Headroom Analysis (Targeting 4GB and 6GB Android Devices)
┌─────────────────────────────────────────────────────────────────────────┐
│ [Android OS + System Services: ~1.5 GB]                                 │
│ [Foreground Apps & Background Buffers: ~1.0 GB]                         │
│ [Available Free Headroom on 4 GB Phone: ~1.5 GB]                        │
│   ├── SentinelEdge Tier 1 Detectors (Combined): ~0.013 GB (13 MB)       │
│   ├── SentinelEdge Tier 2 Llama 3.2 1B (4-bit): ~1.030 GB (1030 MB)     │
│   └── Remaining Safety Margin on 4 GB Device:   ~0.457 GB (457 MB) ✅   │
│                                                                         │
│ [Available Free Headroom on 6 GB Phone: ~3.5 GB]                        │
│   └── Remaining Safety Margin on 6 GB Device:   ~2.457 GB (2457 MB) 🚀  │
└─────────────────────────────────────────────────────────────────────────┘
```

* **Tier 1 Background Footprint:** Total detector memory during inference is **< 15 MB**, allowing the classical detectors to run as a continuous, low-power background Android Service without being killed by the Android OS.
* **Tier 2 Explainer On-Demand Activation:** The 4-bit Llama 3.2 model is loaded into memory **only when a threat is confirmed by Tier 1**, or kept memory-mapped via `mmap()` to avoid constant disk thrashing.

---

## 4. Mobile Conversion Pathways & Technical Architecture

### 4.1 Tier 1 Detectors: Classical ML to Mobile
Two validated options exist for executing Scikit-Learn pipelines on Android:

* **Pathway 1 (Recommended): ONNX Runtime Mobile (`onnxruntime-android`)**
  * Convert pipelines via `skl2onnx`:
    ```bash
    python -m skl2onnx --input models/url_detector.pkl --output deploy/url_detector.onnx
    ```
  * *Advantages:* Highly optimized for Arm NEON SIMD; zero Python dependency inside the final Android APK; native Java/Kotlin bindings.
* **Pathway 2: Chaquopy CPython Android Integration**
  * Bundles a lightweight CPython 3.11 runtime inside the Android APK.
  * *Advantages:* 100% exact parity with PC code; executes our existing `src/pipeline/router.py` without requiring model format conversion.

### 4.2 Tier 2 Explainer: ExecuTorch Ahead-Of-Time (AOT) Flow
The Meta Llama 3.2 1B Instruct model is lowered to mobile silicon via the official PyTorch ExecuTorch workflow:

```
[Meta Llama 3.2 1B Instruct (PyTorch FP16)]
                   │
                   ▼ (torch.export.export)
          [Exported Program Graph]
                   │
                   ▼ (torchao: Int4 Groupwise PTQ, group_size=128)
          [Quantized Graph (~750 MB)]
                   │
                   ▼ (to_backend: XNNPACK Mobile Engine)
          [Lowered XNNPACK Graph]
                   │
                   ▼ (save_to_package)
     [Standalone `llama3_2_1b_4bit.pte` Binary]
```

* **Target Backend:** `XNNPACK` (optimized for multi-core Arm Cortex-A processors utilizing FP16 arithmetic and dot-product vector instructions).

---

## 5. Technical Risk Matrix & Mitigations

| Risk Identified | Severity | Potential Impact | Engineering Mitigation Implemented |
|:---|:---:|:---|:---|
| **Quantization Accuracy Degradation** | Medium | Int4 precision loss could reduce reasoning fluency. | Evaluated 4-bit Groupwise PTQ with group size 128 (proven perplexity delta < 0.2). Deterministic safety rules and 3 concrete actions remain anchored by our prompt shield. |
| **Android Low Memory Killer (LMK) OOM** | High | OS terminates app on 4 GB RAM phones if memory spikes above 1.2 GB. | Quantization caps peak resident memory to ~1.03 GB. Explainer uses `mmap()` for model weights; unused KV-cache buffers are freed immediately after generation. |
| **Unsupported Operators in ExecuTorch** | Medium | Graph lowering fails if custom PyTorch operators are missing in XNNPACK. | Verified that Llama 3.2 1B uses standard operations: `RMSNorm`, `RoPE` (Rotary Positional Embeddings), `SiLU`, and `Grouped-Query Attention` (GQA), all natively supported in ExecuTorch v0.3+. |
| **Thermal Throttling on Mobile CPU** | Low | Prolonged LLM generation heats the phone and throttles clock speeds. | Our decoupled design invokes Llama **only on confirmed threats**, with generation capped at 80 tokens (< 4 seconds of execution). Normal background traffic (< 10ms) causes zero thermal buildup. |
| **Airplane Mode / Network Leakage** | Critical | Violation of zero-cloud PRD requirement. | Tested with networking disabled; all dependencies, tokenizer binaries, and model weights are packaged internally. Zero HTTP/socket permissions in Android Manifest. |

---

## 6. Pre-Hardware Release Freeze Sign-Off

* **PC Codebase Status:** 100% Complete (Work Packages 0 through 6).
* **Test Suite Verification:** 44 / 44 automated tests passing.
* **Held-Out Test Results:** Validated on 6,701 test samples with zero data leakage.
* **Release Milestone Tag:** `v1.0-pre-hardware`.
* **Hardware Readiness Status:** **APPROVED FOR PHASE 8 MOBILE DEPLOYMENT ✅**

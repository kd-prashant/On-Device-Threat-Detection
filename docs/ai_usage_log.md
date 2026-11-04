# AI Usage Log

In accordance with PRD Section 8 (Academic Integrity and Tutor AI Policy Disclosures), this document logs the usage of AI coding assistants (specifically Google DeepMind's Antigravity agent) throughout the project.

---

## Log Entries

### Entry 001 - Project Kickoff & Roadmap Alignment
* **Date:** 2026-11-02
* **Phase:** Initial Consultation & Planning
* **User Prompt:** Request to share complete execution blueprint, phase-by-phase details, and time estimates before proceeding.
* **Agent Contribution:**
  * Analyzed `PRD_PS3_OnDevice_Threat_Detection_for_Antigravity.pdf` and `Team_Guide_OnDevice_Threat_Detection.pdf`.
  * Prepared detailed 10-phase roadmap with time estimates and open decisions checklist.
* **Human Action:** Reviewed and approved initiation of Phase 0 (WP0).

### Entry 002 - Work Package 0 (Project Setup & Tooling)
* **Date:** 2026-11-02
* **Phase:** WP0 (Project Setup)
* **Agent Contribution:**
  * Created project folder architecture and `.gitignore`.
  * Initialized Git repository on `main` branch.
  * Generated pinned `requirements.txt` and `pyproject.toml` configurations.
  * Set up automated code quality runner scripts (`check.bat`, `check.ps1`).
  * Created initial smoke test suite and verified 100% pass rate with Black, Ruff, and Pytest.
  * Created documentation registries: `docs/decisions.md`, `docs/data_sources.md`, and `docs/ai_usage_log.md`.
* **Human Action:** Provided approval to start WP0 and verified the setup.

### Entry 003 - Work Package 1 (Learn and Plan)
* **Date:** 2026-11-03
* **Phase:** WP1 (Learn and Plan)
* **User Prompt:** "lets' move to the phase 1.....take ur proper time do carefully everything and also one more thing u have to make a separette file for purpose of each phase so that which i and my teammeber can read (don't upload that in github)..."
* **Agent Contribution:**
  * Researched threat mechanics, distinguishing features, and false-positive/negative tradeoffs for URL phishing, SMS smishing, and network intrusions; authored `docs/threat_explainers.md`.
  * Synthesized official PyTorch ExecuTorch documentation, detailing AOT graph capture, EXIR lowering, 4-bit Groupwise quantization, and mobile RAM budgets; authored `docs/executorch_summary.md`.
  * Shortlisted benchmark datasets (UCI SMS Spam, PhishTank/Tranco, NSL-KDD) with license terms and class distribution analyses; authored `docs/dataset_shortlist.md`.
  * Recorded architectural decisions 005 and 006 in `docs/decisions.md`.
  * Created local non-committed team guide `TEAM_EXPLAINER_AND_VIVA_GUIDE.md` explaining Phase 0 and Phase 1 in plain English for team members and viva preparation.
* **Human Action:** Reviewed deliverables and authorized progression to Phase 2.

### Entry 004 - Work Package 2 (Data Preparation)
* **Date:** 2026-11-03
* **Phase:** WP2 (Data Preparation)
* **User Prompt:** "lets move to next phase"
* **Agent Contribution:**
  * Developed automated data download module `src/utils/download_data.py` for UCI SMS, Curated Phishing URLs, and NSL-KDD.
  * Authored offline static feature extraction engine for URLs (`src/utils/url_features.py`) extracting 18 structural and Shannon entropy features.
  * Authored SMS preprocessor and metadata extractor (`src/utils/sms_preprocessor.py`) normalizing semantic tokens and psychological urgency indicators.
  * Authored network preprocessor (`src/utils/network_preprocessor.py`) mapping NSL-KDD 41 flow features and attack taxonomies.
  * Built unified reproducible stratified splitting module `src/utils/data_loader.py` with fixed random seed 42 (80% train, 10% val, 10% test).
  * Authored unit tests in `tests/test_data_loaders.py` and `tests/test_feature_extraction.py` with 100% pass rate.
  * Authored documentation `docs/data_splits_summary.md` and updated team guide `TEAM_EXPLAINER_AND_VIVA_GUIDE.md`.
* **Human Action:** Reviewed Phase 2 deliverables and authorized progression to Phase 3.

### Entry 005 - Work Package 3 (Detector Models)
* **Date:** 2026-11-04
* **Phase:** WP3 (Detector Models)
* **User Prompt:** "lets move to phase 3 take ur time and doo properly"
* **Agent Contribution:**
  * Defined abstract typed interface `BaseDetector` and unified `DetectionResult` contract in `src/detectors/base.py`.
  * Built complete baseline and improved model training pipeline in `src/detectors/train_all.py` comparing 6 models across URL, SMS, and Network vectors.
  * Measured Precision, Recall, F1-Score, Confusion Matrices, False-Negative Rates, disk sizes, and single-sample inference latencies.
  * Implemented production inference detector classes (`URLDetector`, `SMSDetector`, `NetworkDetector`) with single-pass probability inference.
  * Generated comprehensive comparison report `docs/detector_models_report.md` and model cards in `models/model_cards.md`.
  * Implemented 7 new integration tests in `tests/test_detectors.py` confirming sub-15ms latency budgets and detection accuracy (total test suite: 21 passed).
  * Recorded Decision 007 in `docs/decisions.md` and updated `TEAM_EXPLAINER_AND_VIVA_GUIDE.md` with Phase 3 viva notes.
* **Human Action:** Verified training execution, benchmark results, and authorized progression to Phase 4.





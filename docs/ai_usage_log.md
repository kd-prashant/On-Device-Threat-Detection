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



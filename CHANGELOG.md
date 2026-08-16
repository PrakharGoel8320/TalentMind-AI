# Changelog

All notable changes to the TalentMind AI project will be documented in this file.

## [Unreleased] - Deterministic Refactoring

### Removed (Experimental GenAI Capabilities)
*   **Talent Copilot (UI & API)**: Completely removed the Copilot dashboard widgets and underlying backend agentic framework.
*   **Generative Explainability (XAI)**: Removed the LLM-powered candidate explainability engine that generated natural language reasoning.
*   **Generative Models & Frameworks**: Purged all integration code and infrastructure for Gemma 3 4B, Ollama, PEFT, TRL, QLoRA, and BitsAndBytes.
*   **Prompt Management**: Removed Prompt Manager, Prompt Registry, and Prompt Templates.
*   **AI Gateway**: Removed AI Gateway routing code and HuggingFace API key logic.
*   **Training Infrastructure**: Deleted the `colab_train` folder, synthetic dataset generation scripts, and model fine-tuning utilities from `scripts/`.
*   **AI Documentation**: Removed LLM-focused documentation (e.g., `FINE_TUNING_GUIDE.md`, `OLLAMA_GEMMA_SETUP.md`, `technical_mvp.md`, `TalentMind_AI_Technical_Documentation.txt`).

### Changed / Restored (Deterministic Core)
*   **Backend Architecture**: Fully restored the deterministic machine learning architecture relying strictly on FAISS similarity search, Cross Encoder re-ranking, and the Behavior Engine.
*   **Dependencies (`pyproject.toml`)**: Cleaned and optimized virtual environment configuration. Pinned `numpy < 2.0.0` to resolve `scipy` compatibility conflicts, and upgraded `fastapi >= 0.115.0`.
*   **API Endpoints**: Reinstated core, standard deterministic endpoints in `jobs.py` (`get_job`, `update_job`, `delete_job`, `match_job`) and `candidates.py` (`screen_candidate`) that were previously overridden by LLM processes.
*   **Frontend UI**: Cleaned `app/(dashboard)/jobs/page.tsx` to remove the Copilot and Executive Report Modals, optimizing the interface for the deterministic matching outputs.

### Fixed
*   **Integration Tests**: Repaired the test suite to pass perfectly (23/23 tests passing) against the standard deterministic API surfaces.
*   **Dependency Collisions**: Solved severe backend failures caused by incompatible versions of `numpy` breaking underlying `scipy` imports, leading to stable local CPU execution.

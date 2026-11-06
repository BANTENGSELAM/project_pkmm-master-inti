# Changelog — KARSA-FIRE & BARA

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0-alpha.2] - 2026-11-05

### Security & Bug Fixes (UI/UX Stage 1: P0 Criticals)
- **Frontend DOM Protection (`static/app.js`):**
  - Sanitized dynamic string injection on monitor headline and status messages via `escapeHTML()` to eliminate XSS surface.
- **Resource Optimization (`static/app.js`):**
  - Added `document.hidden` guards to background monitor polling (10s) and priority ordering polling (60s) to prevent tab background resource waste and API flooding.
- **Data Integrity & User Communication (`static/app.js`, `static/index.html`):**
  - Added `#tableNotice` banner communicating the 300-row limit on the active hotspot detection table with guidance to download CSV for full datasets.
- **Error State Styling (`static/style.css`, `static/app.js`):**
  - Added `.status-error` visual alert treatment for FIRMS, Sentinel STAC, and background monitor connection failures.

## [0.1.0-alpha.1] - 2026-11-05

### Added
- **Baseline Prototype Documentation (`docs/current/`):**
  - Added `docs/current/SYSTEM_MANUAL.md`: Preserved complete operational manual from `PETUNJUK.md` with English technical executive summary.
  - Added `docs/current/API_SPEC.md`: Formally documented live Flask REST endpoints (`/api/status`, `/api/boundary`, `/api/hotspots`, `/api/predict`, `/api/monitor`, `/api/priorities`).
  - Added `docs/current/ML_MODEL_CONTRACT.md`: Documented CatBoost 10-feature schema, SCL cloud-mask filtering rules, and reflectance scaling factors.
- **Architectural Decision Record (ADR-008):**
  - Formally recorded adoption of existing Sentinel-2 / CatBoost prototype in `project_pkmm-master/` as the functional baseline for KARSA-FIRE.
- **Agent Governance & Customizations (`.agents/`):**
  - Established persistent rules in `.agents/rules/` (`01-empirical-integrity.md`, `02-codebase-boundaries.md`, `03-geospatial-standards.md`).
  - Established reusable skills in `.agents/skills/` (`karsa-backend`, `karsa-geo`, `karsa-ml`).
- **Target Enterprise Specifications (`docs/future/`):**
  - Partitioned future scaling specs into `docs/future/` (`PRD_TARGET.md`, `ARCHITECTURE_TARGET.md`, `API_SPEC_TARGET.md`, `ML_SPEC_TARGET.md`, `UX_SPEC_TARGET.md`).

### Changed
- **Unified Root Instructions (`AGENTS.md`):**
  - Refactored root agent instructions to reflect the active prototype baseline, eliminating false greenfield workspace assumptions and broken `KarsaCipta` paths.
- **Project Index & Ledger (`README.md` & `docs/PROJECT_STATE.md`):**
  - Synchronized documentation indices and fact sheets with verified empirical code in `project_pkmm-master/`.
- **Data Dictionary (`docs/DATA_DICTIONARY.md`):**
  - Added Sentinel-2 L2A multispectral bands and SCL quality flags with explicit `IMPLEMENTED` vs. `PLANNED` status indicators.
- **Roadmap (`docs/ROADMAP.md`):**
  - Updated Phase 0 status to reflect completed baseline consolidation and verification gates.

---

## [0.1.0-alpha.0] - 2026-10-26

### Added
- Initial specifications for enterprise target architecture (PRD, Architecture, Data Dictionary, API Spec, ML Spec, UX Spec, Roadmap, ADR-001–007).

---
trigger: model_decision
description: "Repository structure boundaries, working directory conventions, and safe execution rules"
---

# Codebase Boundaries & Execution Integrity

1. **Source of Truth Location:**
   - Active, executable application code resides strictly in `project_pkmm-master/`.
   - Core runtime files:
     - `project_pkmm-master/server.py` (Flask REST API & satellite orchestrator)
     - `project_pkmm-master/monitoring.py` (Background scheduler & priority ranking)
     - `project_pkmm-master/model_early_warning_sentinel2.joblib` (Pretrained CatBoost model)
     - `project_pkmm-master/indonesia.geojson` (National land boundary)
     - `project_pkmm-master/static/` (Leaflet frontend UI, styles, scripts)

2. **Test Suites & Verification Commands:**
   - Always run verification from `project_pkmm-master/`:
     - Backend API tests: `python -m unittest test_app.py`
     - Monitoring tests: `python -m unittest test_monitoring.py`
     - Frontend DOM tests: `node test_frontend.cjs`

3. **Safe Change Lifecycle:**
   - Never modify binary model files (`.joblib`), GeoJSON boundary polygons, or `.env` without explicit user instruction.
   - Execute edits incrementally; run unit tests before and after changes.
   - Synchronize `CHANGELOG.md` and `docs/PROJECT_STATE.md` after structural or architectural modifications.


# KARSA-FIRE / BARA — Indonesia Fire Watch

> **Geospatial Hotspot Analysis & Early-Warning Wildfire Predictive Intelligence**  
> **Status:** Active Baseline Prototype (`project_pkmm-master/`) & Enterprise Architecture Roadmap (`docs/`)

---

## 1. Overview

**KARSA-FIRE** (developed in collaboration with PKMM as **BARA — Pantau Api Indonesia**) is a dual-track geospatial intelligence system designed for forest and land fire (*karhutla*) monitoring, prevention, and hazard forecasting in Indonesia:

1. **Active Implementation (BARA Prototype — `project_pkmm-master/`):**
   - Live NASA FIRMS active fire ingestion (VIIRS S-NPP NRT 375m) with automatic caching and Indonesian polygon boundary clipping.
   - On-demand multispectral feature extraction from Sentinel-2 L2A COGs (via AWS Earth Search STAC) with Scene Classification Layer (SCL) cloud/shadow masking.
   - Pretrained CatBoost machine learning model evaluating 10 spectral features (`B2, B3, B4, B8, B11, B12, NDVI, NDWI, lon, lat`).
   - Automated bounded background monitoring ($3 \times 3$ grid) with persistent scheduling (`monitor_state.json`).
   - Two-tier priority response ordering (Tier 1: Active FIRMS $\le 24$h; Tier 2: CatBoost Class 1 $\le 14$d with 1 km deduplication).
   - Zero-build web dashboard running on Flask 3.x and Leaflet 1.9.4.

2. **Target Architecture (KARSA-FIRE Enterprise — `docs/future/`):**
   - Decoupled enterprise topology: Next.js 14+ client with Deck.gl/MapLibre GL hardware-accelerated rendering.
   - FastAPI asynchronous spatial backend delivering Mapbox Vector Tiles (`ST_AsMVT`).
   - PostgreSQL 16 + PostGIS 3.4 database partitioned by month with Uber H3 hexagonal discrete global grid binning (Res 7 & 8).
   - Spatio-temporal machine learning pipeline combining ERA5-Land reanalysis and CHIRPS rainfall under Purged Blocked Spatio-Temporal Cross Validation.

---

## 2. Quickstart — Running the Active Prototype

### Prerequisites
- Python 3.11+
- Free NASA FIRMS `MAP_KEY` (Request at [https://firms.modaps.eosdis.nasa.gov/api/map_key/](https://firms.modaps.eosdis.nasa.gov/api/map_key/))

### Installation & Launch
```powershell
cd project_pkmm-master
python -m pip install -r requirements.txt
python server.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser. (On Windows, double-clicking `start.bat` also launches the server once dependencies are installed).

### Running Tests
Execute the test suites from `project_pkmm-master/`:
```powershell
python -m unittest test_app.py
python -m unittest test_monitoring.py
node test_frontend.cjs
```

---

## 3. Documentation Index

The repository documentation is partitioned to clearly differentiate between active code contracts and future enterprise specifications:

### Active Prototype (`docs/current/`)
- [**docs/current/SYSTEM_MANUAL.md**](docs/current/SYSTEM_MANUAL.md): Full operational guide, NASA FIRMS setup, grid monitoring, and priority definitions (Bilingual).
- [**docs/current/API_SPEC.md**](docs/current/API_SPEC.md): Specification for live Flask routes (`/api/status`, `/api/boundary`, `/api/hotspots`, `/api/predict`, `/api/monitor`, `/api/priorities`).
- [**docs/current/ML_MODEL_CONTRACT.md**](docs/current/ML_MODEL_CONTRACT.md): CatBoost classifier schema, SCL cloud-mask filtering rules, and spectral index calculations.

### Target Enterprise Architecture (`docs/future/`)
- [**docs/future/PRD_TARGET.md**](docs/future/PRD_TARGET.md): Long-term product requirements, user personas, and MVP boundaries.
- [**docs/future/ARCHITECTURE_TARGET.md**](docs/future/ARCHITECTURE_TARGET.md): Decoupled 4-tier topology (Next.js, FastAPI, PostGIS, H3, Celery).
- [**docs/future/API_SPEC_TARGET.md**](docs/future/API_SPEC_TARGET.md): Planned OpenAPI 3.1 REST & Vector Tile endpoints (`/api/v1`).
- [**docs/future/ML_SPEC_TARGET.md**](docs/future/ML_SPEC_TARGET.md): Purged Blocked Spatio-Temporal CV, weather feature store, and H3 fire-hazard forecasting.
- [**docs/future/UX_SPEC_TARGET.md**](docs/future/UX_SPEC_TARGET.md): Next.js/Deck.gl UI wireframes, design tokens, and colorblind-safe palettes.

### Core Governance & State (`docs/`)
- [**docs/DATA_DICTIONARY.md**](docs/DATA_DICTIONARY.md): Comprehensive schemas for Sentinel-2, FIRMS, ERA5-Land, CHIRPS, and PostGIS tables.
- [**docs/DECISIONS.md**](docs/DECISIONS.md): Architectural Decision Records (ADR-001 through ADR-008).
- [**docs/ROADMAP.md**](docs/ROADMAP.md): Phased engineering roadmap from Phase 0 Baseline through Phase 4 Hardening.
- [**docs/PROJECT_STATE.md**](docs/PROJECT_STATE.md): Current sprint state, completed actions log, and active blocker ledger.
- [**AGENTS.md**](AGENTS.md): AI agent operating instructions, rules, and skills index.
- [**CHANGELOG.md**](CHANGELOG.md): Record of releases and documentation consolidation sprints.

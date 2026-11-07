# BARA / KARSA-FIRE — Indonesia Fire Watch

Geospatial hotspot analysis and early-warning wildfire predictive intelligence.

## 1. Project Overview

BARA/KARSA-FIRE is a prototype system for monitoring forest and land fire potential in Indonesia using satellite data.

- **NASA FIRMS** provides thermal anomaly (hotspot) observations.
- **Sentinel-2 L2A** provides multispectral imagery for XGBoost-based prediction.

FIRMS hotspots are thermal anomalies, not confirmed wildfires. Sentinel-2 predictions indicate potential conditions, not confirmed fires.

## 2. Technology Stack

- Python 3.11+, Flask 3.x
- XGBoost, Rasterio, Pandas
- Leaflet 1.9.4
- NASA GIBS, OpenStreetMap
- NASA FIRMS WMS
- JSON persistence (`monitor_state.json`, `notification_state.json`)

## 3. Repository Structure

```
project_pkmm-master/
  server.py
  firms_wms.py
  monitoring.py
  notifications.py
  static/
    app.js
    index.html
    style.css
  tests/
    test_app.py
    test_monitoring.py
    test_notifications.py
    test_wms.py
    test_frontend.cjs
  docs/
    current/
    future/
  .env / .env.example
```

## 4. Installation

```powershell
cd "C:\Users\kenyi\OneDrive\Desktop\project_pkmm-master"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
cd .\project_pkmm-master
python -m pip install -r requirements.txt
```

Create `.env` with:

```
FIRMS_MAP_KEY=<your key>
```

Never commit `.env`.

## 5. Running

```powershell
.\.venv\Scripts\Activate.ps1
cd .\project_pkmm-master
python server.py
```

Open http://127.0.0.1:5000

## 6. Architecture

- FIRMS ingestion: `server.py:fetch_hotspots` (5-min cache, Indonesia boundary filter).
- Sentinel-2 processing: `scene`/`extract_scene` + XGBoost `predict`.
- Monitoring: `monitoring.py` Monitor (RLock, atomic JSON, daemon worker).
- Notifications: `notifications.py` NotificationEngine (events + notifications, atomic JSON).
- WMS proxy: `firms_wms.py` Blueprint `/api/firms/wms`.

## 7. API Endpoints

- GET /api/status
- GET /api/boundary
- GET /api/hotspots
- POST /api/predict
- GET/POST /api/monitor
- GET /api/priorities
- GET /api/notifications
- POST /api/notifications/<id>/read
- GET /api/events (and detail/history/evidence)
- GET /api/firms/wms

## 8. NASA FIRMS WMS

Supported layers:

- fires_viirs_24, fires_viirs_48, fires_viirs_72, fires_viirs_7
- fires_modis_24, fires_modis_48, fires_modis_72, fires_modis_7

MAP_KEY must be in the URL path: `/mapserver/wms/fires/<KEY>/<layer>/`. Never expose the key in frontend.

## 9. Machine Learning

Features: B2, B3, B4, B8, B11, B12, NDVI, NDWI, longitude, latitude. Reflectance scaled x10000. SCL rejected: 0,1,3,8,9,10,11. 3x3 grid sampling.

## 10. Notifications and Events

- INFO, WASPADA, DARURAT.
- XGBoost Class 1 alone never produces DARURAT.
- Event lifecycle: DETECTED → ACTIVE → STALE → RESOLVED → REOPENED.
- Read state independent of event resolution.

## 11. Testing

```powershell
python -m unittest test_wms
python -m unittest test_notifications
node test_frontend.cjs
```

Reported results: WMS 12 passed, notification 13 passed, frontend 12 passed. Browser visual NOT VERIFIED.

## 12. Development History

Milestones: N1-N5 notification system, N5.2-N5.4 event lifecycle, N5.5 event API, N5.6 event UI, MAP-01, MAP-02.3-2.24. Key fix: FIRMS WMS MAP_KEY must be in URL path.

## 13. Current Status

- Implemented: notification engine, event lifecycle, event API, event UI, WMS proxy, GIBS basemap.
- Tested: WMS 12, notification 13, frontend 12.
- Browser visual: NOT VERIFIED.
- Open issue: stale Flask process / browser visual confirmation.

## 14. Roadmap

Planned: authentication and roles, fixed monitoring locations, radius alerts, external notification channels, future FastAPI/PostGIS/Next.js migration.

## 15. AI Handover

Read AGENTS.md, .agents/rules/, docs/current/, docs/future/. Audit before changes. Run regression tests. Never claim browser verification without inspecting. Never expose secrets.

## 16. Troubleshooting

- Wrong directory: ensure `server.py` exists.
- Port 5000 conflict: check with Get-NetTCPConnection.
- WMS 404: restart Flask after code changes.
- Watermark: verify MAP_KEY in URL path.
- XGBoost model load failure: pre-existing dependency issue.

## 17. License

No license file found; verify before redistributing.

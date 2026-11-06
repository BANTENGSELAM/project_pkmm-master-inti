---
name: karsa-backend
description: "Run, debug, test, and maintain the Flask backend, monitoring worker, and REST API"
---

# KARSA Backend Skill

Use this skill when running the Flask backend, managing background monitoring workers, or executing unit tests.

## 1. Running the Backend Server
Working directory must be `project_pkmm-master/`:
```powershell
cd project_pkmm-master
python -m pip install -r requirements.txt
python server.py
```
Default host/port: `http://127.0.0.1:5000`.

## 2. Testing the Backend
Run the comprehensive test suites from `project_pkmm-master/`:
```powershell
python -m unittest test_app.py
python -m unittest test_monitoring.py
node test_frontend.cjs
```

## 3. Endpoints Overview (`server.py`)
- `GET /api/status`: Inspect model type, loaded features, classes, FIRMS configuration status.
- `GET /api/boundary`: Retrieve Indonesian geographic boundary GeoJSON.
- `GET /api/hotspots?days={1|2|3}`: Retrieve filtered thermal anomalies from NASA FIRMS.
- `POST /api/predict`: Execute point prediction with payload `{"lon": float, "lat": float, "start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}`.
- `GET /api/monitor`: Snapshot of grid monitoring worker state.
- `POST /api/monitor`: Control monitoring worker (`{"action": "configure|start|pause|run", ...}`).
- `GET /api/priorities`: Retrieve consolidated Tier 1 (Active) and Tier 2 (Potential) response priority lists.

## 4. State Persistence
- Monitor worker maintains persistent state in `project_pkmm-master/monitor_state.json`.
- State saves are atomic using `.tmp` file replacement to prevent race conditions during unexpected terminations.


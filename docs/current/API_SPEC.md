# REST API Specification — Prototype (Flask)

> **Document Status:** IMPLEMENTED  
> **Source Module:** `project_pkmm-master/server.py`  
> **Base URL:** `http://127.0.0.1:5000`

---

## 1. System & Boundary Endpoints

### `GET /api/status`
- **Description:** Returns model metadata, expected features, classes, and FIRMS configuration flag.
- **Response `200 OK`:**
  ```json
  {
    "model": "CatBoostClassifier",
    "features": ["B2", "B3", "B4", "B8", "B11", "B12", "NDVI", "NDWI", "longitude", "latitude"],
    "classes": ["0", "1"],
    "firms_configured": true
  }
  ```

### `GET /api/boundary`
- **Description:** Returns the cached GeoJSON Feature polygon for Indonesia (`indonesia.geojson`).
- **Response `200 OK`:** GeoJSON Feature with `MultiPolygon` geometry.

---

## 2. Active Fire & Remote Sensing Endpoints

### `GET /api/hotspots`
- **Description:** Fetches active thermal anomalies from NASA FIRMS VIIRS S-NPP NRT, filters for coordinates within Indonesian land boundaries, and caches the result for 300 seconds.
- **Query Parameters:**
  - `days` (optional, integer): Range in days (`1`, `2`, or `3`). Default is `1`.
- **Response `200 OK`:**
  ```json
  {
    "days": 1,
    "points": [
      {
        "lat": -2.2,
        "lon": 113.9,
        "confidence": "h",
        "frp": 12.5,
        "date": "2026-10-26",
        "time": "0615",
        "satellite": "N",
        "daynight": "D"
      }
    ],
    "retrieved_at": "2026-10-26T07:00:00Z",
    "source": "NASA FIRMS • VIIRS S-NPP NRT"
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: `{"error": "NASA FIRMS MAP_KEY belum diisi..."}`
  - `400 Bad Request`: `{"error": "Rentang waktu harus 1–3 hari."}`

### `POST /api/predict`
- **Description:** Queries AWS Earth Search STAC for the latest Sentinel-2 L2A scene over the target point, extracts surface reflectance across 6 bands, computes NDVI/NDWI, and returns CatBoost prediction.
- **Request Body (`application/json`):**
  ```json
  {
    "lon": 113.9,
    "lat": -2.2,
    "start": "2026-09-26",
    "end": "2026-10-26"
  }
  ```
- **Constraints:**
  - Target point must be on Indonesian land (`indonesia(lon, lat) == True`).
  - Date difference $(end - start) \le 90$ days.
  - Date cannot be in the future.
- **Response `200 OK`:**
  ```json
  {
    "label": "1",
    "probabilities": [0.18, 0.82],
    "classes": ["0", "1"],
    "features": {
      "B2": 635.5,
      "B3": 692.0,
      "B4": 790.5,
      "B8": 1325.5,
      "B11": 2117.5,
      "B12": 1728.0,
      "NDVI": 0.2528,
      "NDWI": -0.3140,
      "longitude": 113.9,
      "latitude": -2.2
    },
    "lon": 113.9,
    "lat": -2.2,
    "scene": {
      "id": "S2B_50LMR_20261018_0_L2A",
      "datetime": "2026-10-18T02:40:00Z",
      "cloud": 12.4
    },
    "warning": "Kelas 1 = berpotensi terbakar; kelas 0 = aman menurut model..."
  }
  ```

---

## 3. Monitoring & Scheduling Endpoints

### `GET /api/monitor`
- **Description:** Returns the active snapshot of the background grid monitor.
- **Response `200 OK`:**
  ```json
  {
    "enabled": true,
    "interval_minutes": 30,
    "bbox": [113.0, -3.0, 114.0, -2.0],
    "points": [
      {
        "id": "1-1",
        "lat": -2.83,
        "lon": 113.17,
        "status": "ok",
        "checked_at": "2026-10-26T07:15:00Z",
        "result": { ... },
        "error": null
      }
    ],
    "cursor": 5,
    "last_run": "2026-10-26T07:15:00Z",
    "next_run": "2026-10-26T07:45:00Z",
    "busy": false,
    "current": null,
    "batch_size": 5,
    "grid_size": 3
  }
  ```

### `POST /api/monitor`
- **Description:** Configures monitoring bounding box or executes control commands.
- **Configuration Request:**
  ```json
  {
    "action": "configure",
    "bbox": [113.0, -3.0, 114.0, -2.0],
    "interval_minutes": 30
  }
  ```
- **Control Request:**
  ```json
  {
    "action": "start | pause | run"
  }
  ```

### `GET /api/priorities`
- **Description:** Computes response ranking combining Tier 1 (active thermal anomalies $\le 24$h) and Tier 2 (Sentinel-2 CatBoost class 1 potential $\le 14$d with 1 km spatial deduplication). Also includes Tier 3 historical potentials.
- **Response `200 OK`:**
  ```json
  {
    "rows": [
      {
        "tier": 1,
        "category": "Indikasi kebakaran aktif",
        "lat": -2.2,
        "lon": 113.9,
        "observed_at": "2026-10-26T06:15:00Z",
        "confidence": "h",
        "frp": 15.4,
        "source": "NASA FIRMS / VIIRS",
        "reason": "Deteksi termal 24 jam terakhir; perlu konfirmasi lapangan."
      },
      {
        "tier": 2,
        "category": "Berpotensi terbakar",
        "lat": -2.83,
        "lon": 113.17,
        "observed_at": "2026-10-18T02:40:00Z",
        "score": 0.84,
        "source": "Sentinel-2 / CatBoost",
        "reason": "Kelas 1: prioritas pencegahan; skor model bukan kepastian kejadian."
      }
    ],
    "historical_potential": [],
    "active_count": 1,
    "potential_count": 1,
    "firms_updated_at": "2026-10-26T07:00:00Z",
    "warning": null,
    "note": "Prioritas 1: deteksi termal dalam 24 jam..."
  }
  ```


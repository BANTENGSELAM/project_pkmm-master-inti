---
name: karsa-geo
description: "Ingest and process Sentinel-2 L2A STAC COGs, NASA FIRMS active fire CSVs, and GeoJSON land filtering"
---

# KARSA Geospatial Data Engineering Skill

Use this skill when handling NASA FIRMS active fire data, querying AWS Earth Search STAC for Sentinel-2, or performing spatial filtering.

## 1. NASA FIRMS Integration (`server.py:fetch_hotspots`)
- **API Endpoint:** `https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/94,-12,142,7/{days}`
- **Days Parameter:** Valid values are integer `1`, `2`, or `3`.
- **Caching:** Cache responses in-memory for 300 seconds to conserve API quota.
- **Land Filtering:** Every coordinate must pass `indonesia(lon, lat)` ray-casting check against `indonesia.geojson` to filter out foreign and offshore hits.

## 2. Sentinel-2 L2A COG Sampling (`server.py:scene`, `server.py:extract_scene`)
- **STAC Query:** POST `https://earth-search.aws.element84.com/v1/search`
  - Collection: `sentinel-2-l2a`
  - Bounding Intersects: Point `[lon, lat]`
  - Datetime window: `{start}T00:00:00Z/{end}T23:59:59Z`
  - Query: `eo:cloud_cover < 40`
  - Limit: 40, sorted descending by datetime
- **Direct COG Pixel Sampling via Rasterio:**
  - Channels required: `B2` (blue), `B3` (green), `B4` (red), `B8` (nir), `B11` (swir16), `B12` (swir22), and `scl` (scene classification layer).
  - Environment: `GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR`, `AWS_NO_SIGN_REQUEST=YES`, `GDAL_HTTP_TIMEOUT=35`.
  - Coordinate re-projection from `EPSG:4326` to native scene CRS using `rasterio.warp.transform`.

## 3. Spatial Grid Partitioning (`monitoring.py:grid_points`)
- Divides user bounding box into a 3x3 uniform grid (9 candidate points).
- Area limits: $0.005^\circ \le (\text{east}-\text{west}) \le 2.0^\circ$, $0.005^\circ \le (\text{north}-\text{south}) \le 2.0^\circ$.
- Only points centered on Indonesian landmass are retained; marine points are discarded.


# Data Dictionary & Schema Specification — KARSA-FIRE & BARA

> **Document Version:** 1.1.0  
> **Status:** Active Data Dictionary  
> **Coordinate Reference System:** WGS 84 (`EPSG:4326`) for geometries; Web Mercator (`EPSG:3857`) for map rendering.

---

## 1. Implemented Datasets (Active Prototype)

### 1.1 Sentinel-2 L2A Multispectral Surface Reflectance
- **Status:** `IMPLEMENTED`
- **Source:** AWS Earth Search STAC v1 (`sentinel-2-l2a`) via Cloud-Optimized GeoTIFFs (COGs).
- **Scale Factor:** $\text{Reflectance} = (\text{val} \times \text{scale} + \text{offset}) \times 10000$ (offset neutralized if `earthsearch:boa_offset_applied` is true).

| Band / Index | Asset Key | Central Wavelength | Spatial Res | Role in Fire Susceptibility Inference |
|---|---|---|---|---|
| `B2` | `blue` | $490\text{ nm}$ | $10\text{ m}$ | Blue reflectance; atmospheric scattering correction. |
| `B3` | `green` | $560\text{ nm}$ | $10\text{ m}$ | Green reflectance; used in standard McFeeters NDWI. |
| `B4` | `red` | $665\text{ nm}$ | $10\text{ m}$ | Red absorption; chlorophyll absorption contrast in NDVI. |
| `B8` | `nir` | $842\text{ nm}$ | $10\text{ m}$ | Near-infrared reflectance; canopy density and cell structure. |
| `B11` | `swir16` | $1610\text{ nm}$ | $20\text{ m}$ | Shortwave infrared-1; sensitive to vegetation moisture & dry fuel. |
| `B12` | `swir22` | $2190\text{ nm}$ | $20\text{ m}$ | Shortwave infrared-2; charcoal and burn scar detection. |
| `SCL` | `scl` | N/A | $20\text{ m}$ | Scene Classification Layer: filters clouds (8, 9), shadow (3), cirrus (10). |
| `NDVI` | Derived | N/A | $10\text{ m}$ | $\frac{B8 - B4}{B8 + B4}$ (Normalized Difference Vegetation Index). |
| `NDWI` | Derived | N/A | $10\text{ m}$ / $20\text{ m}$ | $\frac{B3 - B8}{B3 + B8}$ (default) or $\frac{B8 - B11}{B8 + B11}$ (Gao Moisture Index). |

### 1.2 NASA FIRMS Active Fire Data (Thermal Anomalies)
- **Status:** `IMPLEMENTED`
- **Source:** NASA FIRMS API (`VIIRS_SNPP_NRT`).

| Attribute | Type | Unit | Description |
|---|---|---|---|
| `latitude` | `float` | Degrees | Latitude of active fire pixel center (WGS 84, $-90.0$ to $+90.0$). |
| `longitude` | `float` | Degrees | Longitude of active fire pixel center (WGS 84, $-180.0$ to $+180.0$). |
| `confidence` | `string` | Code | Categorical confidence: `'l'` (low), `'n'` (nominal), `'h'` (high). |
| `frp` | `float` | Megawatts | Fire Radiative Power (MW) measuring radiant heat output. |
| `acq_date` | `string` | YYYY-MM-DD | Acquisition date in UTC. |
| `acq_time` | `string` | HHMM | Acquisition time in UTC. |
| `satellite` | `string` | Code | Satellite identifier (`'N'` for Suomi-NPP). |
| `daynight` | `string` | Code | Day (`'D'`) or Night (`'N'`). |

---

## 2. Planned Datasets (Target Architecture — Phase 1+)

### 2.1 ECMWF ERA5-Land Meteorological Reanalysis
- **Status:** `PLANNED`
- **Resolution:** $\sim 9\text{ km}$ ($0.1^\circ \times 0.1^\circ$).

| Parameter | Unit | Description |
|---|---|---|
| `t2m` | Kelvin (K) | Air temperature at 2 meters. |
| `d2m` | Kelvin (K) | Dewpoint temperature at 2 meters. |
| `u10`, `v10` | $\text{m/s}$ | 10-meter zonal and meridional wind speed components. |
| `swvl1` | $\text{m}^3/\text{m}^3$ | Topsoil volumetric moisture ($0 - 7\text{ cm}$). |
| `swvl2` | $\text{m}^3/\text{m}^3$ | Subsurface root-zone volumetric moisture ($7 - 28\text{ cm}$). |

### 2.2 CHIRPS Precipitation
- **Status:** `PLANNED`
- **Resolution:** $0.05^\circ \times 0.05^\circ$ ($\sim 5.5\text{ km}$).

| Field | Type | Description |
|---|---|---|
| `precip` | $\text{mm/day}$ | Daily total precipitation. |
| `consecutive_dry_days` | Days | Consecutive days with $\text{precip} < 1.0\text{ mm}$. |

### 2.3 Target PostGIS Relational Tables
- **Status:** `PLANNED`
- `hotspots`: Raw point observations partitioned by year/month.
- `h3_daily_aggregates`: Pre-aggregated daily rollups indexed by Uber H3 cells.
- `fire_risk_predictions`: Spatial-temporal predictions and SHAP feature attributions.

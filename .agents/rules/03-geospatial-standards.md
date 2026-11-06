---
trigger: model_decision
description: "CRS conventions, Sentinel-2 SCL cloud masking, reflectance scaling, and index formulas"
---

# Geospatial & Remote Sensing Standards

1. **Coordinate Reference System (CRS):**
   - Ingestion, STAC queries, and GeoJSON boundaries use WGS 84 (`EPSG:4326`) with `[longitude, latitude]` order.
   - Map tiles and client rendering use Web Mercator (`EPSG:3857`).
   - Bounds for Indonesia: `[94.0, -12.0, 142.0, 7.0]`. Point-in-polygon ray-casting against `indonesia.geojson` is required for land filtering.

2. **Sentinel-2 L2A Ingestion Standards:**
   - Provider: AWS Earth Search STAC v1 (`https://earth-search.aws.element84.com/v1/search`), collection `sentinel-2-l2a`.
   - Cloud threshold on scene search: `eo:cloud_cover < 40`.
   - SCL (Scene Classification Layer) pixel filtering:
     - REJECT pixel if SCL value $\in \{0, 1, 3, 8, 9, 10, 11\}$ (No-data, Saturated/Defective, Cloud Shadow, Cloud Medium/High, Cirrus, Snow/Ice).
     - ACCEPT ONLY if valid land/vegetation/bare soil.
   - Scale factor: Raw digital numbers (DN) from COGs must be converted to surface reflectance scaled by $10000$:
     $$\text{Reflectance} = (\text{val} \times \text{scale} + \text{offset}) \times 10000$$
     *(Note: If `earthsearch:boa_offset_applied` is True, offset is 0).*

3. **Spectral Indices:**
   - **NDVI:** $\frac{B8 - B4}{B8 + B4}$
   - **NDWI:** Defaults to Green/NIR $\frac{B3 - B8}{B3 + B8}$ (`green_nir`). If `NDWI_FORMULA=nir_swir`, uses Gao Moisture Index $\frac{B8 - B11}{B8 + B11}$.


---
name: karsa-ml
description: "Model inference contract, feature pipeline, and zero-leakage spatio-temporal validation protocols"
---

# KARSA Machine Learning Skill

Use this skill when dealing with CatBoost model inference, input feature computation, and model validation protocols.

## 1. Active CatBoost Model Contract
- **File:** `project_pkmm-master/model_early_warning_sentinel2.joblib`
- **Model Type:** `CatBoostClassifier`
- **Features (10):**
  1. `B2`: Blue band reflectance ($\times 10000$)
  2. `B3`: Green band reflectance ($\times 10000$)
  3. `B4`: Red band reflectance ($\times 10000$)
  4. `B8`: Near-Infrared band reflectance ($\times 10000$)
  5. `B11`: Shortwave Infrared 1 band reflectance ($\times 10000$)
  6. `B12`: Shortwave Infrared 2 band reflectance ($\times 10000$)
  7. `NDVI`: Normalized Difference Vegetation Index $(B8 - B4)/(B8 + B4)$
  8. `NDWI`: Normalized Difference Water Index (default $(B3 - B8)/(B3 + B8)$)
  9. `longitude`: Pixel longitude (WGS 84)
  10. `latitude`: Pixel latitude (WGS 84)
- *(Optional: `dNBR` dynamically calculated if present in feature names).*
- **Classes:** `['0', '1']` where:
  - `0`: Safe / Low Risk (Aman)
  - `1`: Potential Fire Hazard (Berpotensi Terbakar)
- **Output:** Predicted label string and calibrated class probabilities array.

## 2. Priority Sorting & Spatial Deduplication (`monitoring.py:priorities`)
- **Tier 1 (Active Indication):** NASA FIRMS hotspots acquired within the past 24 hours. Sorted by acquisition date, confidence (`h` > `n` > `l`), FRP, and acquisition time.
- **Tier 2 (Prevention Potential):** CatBoost Class 1 predictions with image acquisition $\le 14$ days old.
  - *Deduplication Rule:* If a potential point is within 1 km of an active Tier 1 hotspot, it is suppressed from Tier 2 to prevent redundant alerting.
- **Tier 3 (Historical Potential):** Class 1 predictions with imagery $> 14$ days old are classified as historical requiring updated imagery.

## 3. Future Training Validation Rules (ADR-005)
- Standard random K-fold cross-validation is strictly forbidden.
- Models must use Purged Blocked Spatio-Temporal CV:
  - Temporal forward splitting with a 7-day temporal embargo buffer.
  - Spatial block buffering (minimum 50 km buffer between train and test cells).


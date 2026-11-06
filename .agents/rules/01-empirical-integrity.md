---
trigger: model_decision
description: "Non-negotiable laws on data integrity, verification, and satellite anomaly interpretation"
---

# Empirical Integrity & Scientific Guardrails

1. **No Simulated Data as Real:**
   - Never invent mock data, fake API responses disguised as live data, or simulated predictive outputs.
   - Never present planned features as implemented.

2. **Thermal Anomalies vs. Confirmed Wildfires:**
   - Active fire pixels from NASA FIRMS (MODIS/VIIRS) represent thermal radiant anomalies, NOT confirmed uncontrolled ground wildfires.
   - Detections may represent agricultural burning, industrial flares, or sensor artifacts (glint).
   - Low confidence (`l`) detections must be filtered out for operational alerting unless investigating sub-pixel smoldering.
   - Always retain the distinction in API outputs, logging, and UI labels.

3. **Validation & Probabilistic Restraint:**
   - Model prediction probability is an algorithmic score, not a guaranteed empirical real-world probability.
   - Any future model training must enforce strict blocked spatio-temporal cross-validation (zero temporal or spatial leakage).


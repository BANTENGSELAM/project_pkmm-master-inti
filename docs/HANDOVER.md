# BARA / KARSA-FIRE — Project Documentation, Installation Guide & AI Handover

(Dokumen serah terima proyek — versi 1.0, 7 November 2026)

See full content in conversation; this file captures the handover summary.

## Quick start

```powershell
cd "C:\Users\kenyi\OneDrive\Desktop\project_pkmm-master"
.\.venv\Scripts\Activate.ps1
cd .\project_pkmm-master
python server.py
```

Open http://127.0.0.1:5000

## Tests

```powershell
python -m unittest test_wms
python -m unittest test_notifications
node test_frontend.cjs
```

## Key files
- server.py
- firms_wms.py
- static/app.js
- notifications.py
- monitoring.py

## Notes
- MAP_KEY must be in URL path for FIRMS WMS.
- Browser visual verification not yet confirmed.
- Do not expose secrets.

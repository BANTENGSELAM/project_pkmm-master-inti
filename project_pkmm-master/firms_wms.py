"""NASA FIRMS WMS proxy, independently importable."""
import os
import requests
from flask import Blueprint, request, jsonify, Response

bp = Blueprint("firms_wms", __name__)

def _param(name, default=""):
    for k, v in request.args.items():
        if k.lower() == name.lower():
            return v
    return default

ALLOWED_FIRMS_LAYERS = {"fires_viirs_24","fires_viirs_48","fires_viirs_72","fires_viirs_7","fires_modis_24","fires_modis_48","fires_modis_72","fires_modis_7"}

@bp.get("/api/firms/wms")
def firms_wms():
    key = os.getenv("FIRMS_MAP_KEY", "")
    if not key:
        return jsonify(error="FIRMS_MAP_KEY not configured"), 503
    service = _param('SERVICE','WMS')
    req = _param('REQUEST','GetMap')
    version = _param('VERSION','1.1.1')
    layers = _param('LAYERS','')
    if layers not in ALLOWED_FIRMS_LAYERS:
        return jsonify(error="invalid layer"), 400
    styles = _param('STYLES','')
    fmt = _param('FORMAT','image/png')
    if fmt not in ("image/png","image/jpeg"):
        return jsonify(error="invalid format"), 400
    transparent = _param('TRANSPARENT','TRUE')
    try:
        w = int(_param('WIDTH','256'))
        h = int(_param('HEIGHT','256'))
    except ValueError:
        return jsonify(error="invalid size"), 400
    if w < 1 or w > 1024 or h < 1 or h > 1024:
        return jsonify(error="invalid size"), 400
    srs = _param('SRS','EPSG:3857')
    if srs != "EPSG:3857":
        return jsonify(error="invalid srs"), 400
    bbox = _param('BBOX','')
    try:
        parts = [float(x) for x in bbox.split(",")]
        if len(parts) != 4:
            raise ValueError
    except ValueError:
        return jsonify(error="invalid bbox"), 400
    params = {"SERVICE":service,"REQUEST":req,"VERSION":version,"LAYERS":layers,"STYLES":styles,"FORMAT":fmt,"TRANSPARENT":transparent,"WIDTH":w,"HEIGHT":h,"SRS":srs,"BBOX":bbox,"key":key}
    try:
        upstream_params = {k: v for k, v in params.items() if k.lower() not in ("key", "layers")}
        r = requests.get("https://firms.modaps.eosdis.nasa.gov/mapserver/wms/fires/" + key + "/" + layers + "/", params=upstream_params, timeout=30)
    except Exception:
        return jsonify(error="upstream error"), 502
    if r.status_code != 200:
        return jsonify(error="upstream error"), 502
    if "image" not in r.headers.get("Content-Type",""):
        return jsonify(error="upstream error"), 502
    return Response(r.content, mimetype=fmt)

"""Notification event identity, deduplication, and persistent state for BARA."""
import copy
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

UTC = timezone.utc
DETECTED='DETECTED'
ACTIVE='ACTIVE'
STALE='STALE'
RESOLVED='RESOLVED'
REOPENED='REOPENED'
VALID_STATES={DETECTED,ACTIVE,STALE,RESOLVED,REOPENED,'open'}
VALID_SEVERITIES = {"INFO", "WASPADA", "DARURAT"}
VALID_SOURCES = {"FIRMS", "SENTINEL", "MONITOR", "SYSTEM"}

SCHEMA_VERSION = 1


def utc_now():
    return datetime.now(UTC).isoformat()


def validate_coord(lat, lon):
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        raise ValueError("invalid coordinates")
    if lat < -90 or lat > 90 or lon < -180 or lon > 180:
        raise ValueError("invalid coordinates")
    import math
    if not math.isfinite(lat) or not math.isfinite(lon):
        raise ValueError("invalid coordinates")
    return float(lat), float(lon)


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip()


def firms_event_key(point):
    lat, lon = validate_coord(point["lat"], point["lon"])
    date = normalize_text(point.get("date"))
    timev = normalize_text(point.get("acq_time") or point.get("time") or "")
    timev = timev.zfill(4) if timev else ""
    sat = normalize_text(point.get("satellite"))
    return f"firms|{lat:.6f}|{lon:.6f}|{date}|{timev}|{sat}"


def sentinel_event_key(point_id, result):
    scene = result.get("scene") or {}
    scene_id = normalize_text(scene.get("id"))
    scene_dt = normalize_text(scene.get("datetime"))
    if not scene_id or not scene_dt:
        raise ValueError("incomplete scene metadata")
    return f"sentinel|{normalize_text(point_id)}|{scene_id}|{scene_dt}"


def _atomic_write(path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    tmp.replace(path)


class NotificationEngine:
    def __init__(self, path, lock=None):
        self.path = Path(path)
        self.lock = lock or threading.RLock()
        self.state = self._load()

    def _default_state(self):
        return dict(schema_version=SCHEMA_VERSION, events={}, notifications={}, updated_at=utc_now())

    def _load(self):
        if not self.path.exists():
            return self._default_state()
        try:
            raw = self.path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, json.JSONDecodeError, ValueError):
            backup = self.path.with_suffix(".corrupt")
            try:
                self.path.replace(backup)
            except OSError:
                pass
            return self._default_state()
        if not isinstance(data, dict):
            return self._default_state()
        data.setdefault("schema_version", SCHEMA_VERSION)
        data.setdefault("events", {})
        data.setdefault("notifications", {})
        data.setdefault("updated_at", utc_now())
        for ev in data["events"].values():
            if isinstance(ev, dict):
                ev.setdefault("last_observed_at", ev.get("last_detected_at") or ev.get("updated_at") or utc_now())
                ev.setdefault("resolution", None)
                ev.setdefault("history", [])
        return data

    def _save(self):
        self.state["updated_at"] = utc_now()
        _atomic_write(self.path, self.state)

    def snapshot(self):
        with self.lock:
            return copy.deepcopy(self.state)

    def _new_id(self, prefix, key):
        return f"{prefix}:{key}"

    def _create_event(self, event_key, source, severity, lat, lon, evidence, now):
        eid = self._new_id("event", event_key)
        event = dict(
            id=eid,
            event_key=event_key,
            source=source,
            severity=severity,
            latitude=lat,
            longitude=lon,
            first_detected_at=now,
            last_detected_at=now,
            status="open",
            evidence=evidence,
            created_at=now,
            updated_at=now,
        )
        self.state["events"][eid] = event
        return event

    def _create_notification(self, event, title, message, occurred_at):
        nid = self._new_id("notif", event["event_key"])
        notif = dict(
            id=nid,
            event_id=event["id"],
            title=title,
            message=message,
            severity=event["severity"],
            source=event["source"],
            latitude=event["latitude"],
            longitude=event["longitude"],
            occurred_at=occurred_at,
            created_at=utc_now(),
            read_at=None,
            status="unread",
        )
        self.state["notifications"][nid] = notif
        return notif

    def process_firms(self, hotspots):
        created = []
        with self.lock:
            now = utc_now()
            for p in hotspots or []:
                try:
                    lat, lon = validate_coord(p["lat"], p["lon"])
                except (KeyError, ValueError, TypeError):
                    continue
                try:
                    key = firms_event_key(p)
                except (KeyError, ValueError, TypeError):
                    continue
                eid = self._new_id("event", key)
                evidence = dict(
                    confidence=p.get("confidence"),
                    frp=p.get("frp"),
                    date=p.get("date"),
                    time=p.get("time") or p.get("acq_time"),
                    satellite=p.get("satellite"),
                )
                occurred = None
                try:
                    t = p.get("date") and (p.get("time") or p.get("acq_time"))
                    if t:
                        occurred = datetime.strptime(str(p["date"]) + str(t).zfill(4), "%Y-%m-%d%H%M").replace(tzinfo=UTC).isoformat()
                except (ValueError, TypeError):
                    occurred = now
                occurred = occurred or now
                if eid in self.state["events"]:
                    ev = self.state["events"][eid]
                    if ev.get("evidence") != evidence:
                        ev.setdefault("history", []).append({"at": now, "source": "FIRMS", "change": "evidence_updated"})
                        if ev.get("status") in (DETECTED, STALE):
                            ev["status"] = ACTIVE
                            ev.setdefault("history", []).append({"at": now, "source": "FIRMS", "change": f"{ev.get('status')}->{ACTIVE}"})
                        elif ev.get("status") == RESOLVED:
                            ev["status"] = REOPENED
                            ev.setdefault("history", []).append({"at": now, "source": "FIRMS", "change": f"{RESOLVED}->{REOPENED}"})
                    ev["last_detected_at"] = now
                    ev["last_observed_at"] = now
                    ev["evidence"] = evidence
                    ev["updated_at"] = now
                else:
                    ev = self._create_event(key, "FIRMS", "WASPADA", lat, lon, evidence, now)
                    ev["history"] = [{"at": now, "source": "FIRMS", "change": "created"}]
                    ev["first_detected_at"] = occurred
                    ev["last_detected_at"] = occurred
                    self._create_notification(
                        ev,
                        "Indikasi termal FIRMS",
                        "Deteksi anomali termal VIIRS; bukan konfirmasi kebakaran.",
                        occurred,
                    )
                    created.append(ev["id"])
            self._save()
        return created

    def process_sentinel(self, point_id, result):
        created = []
        if not isinstance(result, dict):
            return created
        scene = result.get("scene") or {}
        try:
            key = sentinel_event_key(point_id, result)
        except (KeyError, ValueError, TypeError):
            return created
        try:
            lat, lon = validate_coord(result.get("lat"), result.get("lon"))
        except (KeyError, ValueError, TypeError):
            return created
        label = normalize_text(result.get("label"))
        with self.lock:
            now = utc_now()
            eid = self._new_id("event", key)
            evidence = dict(
                scene_id=scene.get("id"),
                scene_datetime=scene.get("datetime"),
                label=label,
                probabilities=result.get("probabilities"),
                classes=result.get("classes"),
            )
            occurred_raw = scene.get("datetime")
            try:
                occurred = datetime.fromisoformat(str(occurred_raw).replace("Z", "+00:00")).isoformat()
            except (ValueError, TypeError):
                occurred = now
            if eid in self.state["events"]:
                ev = self.state["events"][eid]
                prev_label = normalize_text((ev.get("evidence") or {}).get("label"))
                if ev.get("evidence") != evidence:
                    ev.setdefault("history", []).append({"at": now, "source": "SENTINEL", "change": "evidence_updated"})
                    if ev.get("status") in (DETECTED, STALE):
                        ev["status"] = ACTIVE
                        ev.setdefault("history", []).append({"at": now, "source": "SENTINEL", "change": f"{ev.get('status')}->{ACTIVE}"})
                    elif ev.get("status") == RESOLVED:
                        ev["status"] = REOPENED
                        ev.setdefault("history", []).append({"at": now, "source": "SENTINEL", "change": f"{RESOLVED}->{REOPENED}"})
                ev["last_detected_at"] = now
                ev["last_observed_at"] = now
                ev["evidence"] = evidence
                ev["updated_at"] = now
                if label == "1" and prev_label != "1":
                    self._create_notification(
                        ev,
                        "Potensi terbakar XGBoost",
                        "Kelas 1: prioritas pencegahan; skor model bukan kepastian kejadian.",
                        occurred,
                    )
                    created.append(ev["id"])
            else:
                if label != "1":
                    return created
                ev = self._create_event(key, "SENTINEL", "WASPADA", lat, lon, evidence, now)
                ev["history"] = [{"at": now, "source": "SENTINEL", "change": "created"}]
                ev["first_detected_at"] = occurred
                ev["last_detected_at"] = occurred
                self._create_notification(
                    ev,
                    "Potensi terbakar XGBoost",
                    "Kelas 1: prioritas pencegahan; skor model bukan kepastian kejadian.",
                    occurred,
                )
                created.append(ev["id"])
            self._save()
        return created


    def transition(self, event_id, new_status, trigger, actor=None, reason=None, evidence_ref=None, now=None):
        now = now or utc_now()
        with self.lock:
            ev = self.state["events"].get(event_id)
            if ev is None:
                raise ValueError("event not found")
            if new_status not in VALID_STATES:
                raise ValueError("invalid state")
            # permitted transitions
            cur = ev.get("status")
            allowed = {
                DETECTED: {ACTIVE, STALE, RESOLVED},
                ACTIVE: {STALE, RESOLVED},
                STALE: {ACTIVE, RESOLVED},
                RESOLVED: {REOPENED},
                REOPENED: {ACTIVE},
                "open": {DETECTED, ACTIVE, STALE, RESOLVED},
            }
            if new_status not in allowed.get(cur, set()):
                raise ValueError("invalid transition")
            if new_status == RESOLVED:
                if not actor or not reason:
                    raise ValueError("resolution requires actor and reason")
                ev["resolution"] = {"actor": actor, "reason": reason, "at": now, "evidence_ref": evidence_ref}
            ev.setdefault("history", []).append({"at": now, "from": cur, "to": new_status, "trigger": trigger, "actor": actor, "reason": reason})
            ev["status"] = new_status
            ev["updated_at"] = now
            self._save()
            return ev

    def resolve_event(self, event_id, actor, reason, evidence_ref=None, now=None):
        return self.transition(event_id, RESOLVED, "manual_resolve", actor=actor, reason=reason, evidence_ref=evidence_ref, now=now)

    def evaluate_stale(self, event_id, threshold_hours=24, now=None):
        now = now or datetime.now(UTC)
        with self.lock:
            ev = self.state["events"].get(event_id)
            if ev is None:
                return False
            if ev.get("status") not in (DETECTED, ACTIVE):
                return False
            try:
                last = datetime.fromisoformat(str(ev.get("last_observed_at")).replace("Z","+00:00"))
            except (ValueError, TypeError):
                return False
            if (now - last).total_seconds() >= threshold_hours*3600:
                ev.setdefault("history", []).append({"at": now.isoformat(), "from": ev["status"], "to": STALE, "trigger": "stale_evaluation"})
                ev["status"] = STALE
                ev["updated_at"] = now.isoformat()
                self._save()
                return True
            return False

    def mark_read(self, notification_id):
        with self.lock:
            n = self.state["notifications"].get(notification_id)
            if n is None:
                return False
            if n.get("status") != "read":
                n["status"] = "read"
                n["read_at"] = utc_now()
                self._save()
            return True

    def list_notifications(self, unread_only=False):
        with self.lock:
            items = list(self.state["notifications"].values())
        if unread_only:
            items = [n for n in items if n.get("status") != "read"]
        return items

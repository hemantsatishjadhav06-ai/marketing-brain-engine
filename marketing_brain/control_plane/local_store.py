"""JSON-file control plane. Default when no cloud creds — keeps CI green and lets you
see the whole loop locally."""
import json, time, pathlib, uuid
from .base import Store

PATH = pathlib.Path(__file__).resolve().parents[2] / "data" / "local_store.json"


class LocalStore(Store):
    name = "local"

    def __init__(self):
        PATH.parent.mkdir(parents=True, exist_ok=True)
        self._db = json.loads(PATH.read_text()) if PATH.exists() else {}

    def _save(self):
        PATH.write_text(json.dumps(self._db, indent=2))

    def list(self, table, where=None):
        rows = list(self._db.get(table, {}).values())
        if where:
            rows = [r for r in rows if all(r["fields"].get(k) == v for k, v in where.items())]
        return rows

    def create(self, table, fields):
        rid = "rec" + uuid.uuid4().hex[:14]
        rec = {"id": rid, "fields": fields, "createdTime": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
        self._db.setdefault(table, {})[rid] = rec
        self._save()
        return rec

    def update(self, table, record_id, fields):
        rec = self._db[table][record_id]
        rec["fields"].update(fields)
        self._save()
        return rec

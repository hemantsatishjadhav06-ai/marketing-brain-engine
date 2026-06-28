"""Airtable REST control plane. Uses the same base as your Content Generation engine."""
import requests
from .base import Store

API = "https://api.airtable.com/v0"


class AirtableStore(Store):
    name = "airtable"

    def __init__(self, key, base_id):
        self.base = base_id
        self.h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def list(self, table, where=None):
        out, params = [], {"pageSize": 100}
        while True:
            r = requests.get(f"{API}/{self.base}/{table}", headers=self.h, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
            for rec in data.get("records", []):
                if not where or all(rec["fields"].get(k) == v for k, v in where.items()):
                    out.append(rec)
            if data.get("offset"):
                params["offset"] = data["offset"]
            else:
                return out

    def create(self, table, fields):
        r = requests.post(f"{API}/{self.base}/{table}", headers=self.h,
                          json={"fields": fields, "typecast": True}, timeout=30)
        r.raise_for_status()
        return r.json()

    def update(self, table, record_id, fields):
        r = requests.patch(f"{API}/{self.base}/{table}/{record_id}", headers=self.h,
                           json={"fields": fields, "typecast": True}, timeout=30)
        r.raise_for_status()
        return r.json()

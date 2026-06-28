"""Create any missing control-plane tables in your Airtable base (idempotent)."""
import json, os, sys, pathlib, requests

SCHEMA = pathlib.Path(__file__).resolve().parents[1] / "schema" / "airtable_schema.json"
META = "https://api.airtable.com/v0/meta/bases"


def main():
    key, base = os.getenv("AIRTABLE_API_KEY"), os.getenv("AIRTABLE_BASE_ID")
    if not (key and base):
        print("Set AIRTABLE_API_KEY and AIRTABLE_BASE_ID first."); sys.exit(2)
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    schema = json.loads(SCHEMA.read_text())
    existing = {t["name"] for t in requests.get(f"{META}/{base}/tables", headers=h, timeout=30).json().get("tables", [])}
    for name, spec in schema["tables"].items():
        if name in existing:
            print("ok    ", name); continue
        fields = []
        for fn in spec["fields"]:
            if fn == "Status" and spec.get("status_options"):
                fields.append({"name": fn, "type": "singleSelect",
                               "options": {"choices": [{"name": o} for o in spec["status_options"]]}})
            else:
                fields.append({"name": fn, "type": "multilineText"})
        body = {"name": name, "fields": fields}
        r = requests.post(f"{META}/{base}/tables", headers=h, json=body, timeout=30)
        print("create" if r.ok else f"FAIL {r.status_code}", name, "" if r.ok else r.text[:160])


if __name__ == "__main__":
    main()

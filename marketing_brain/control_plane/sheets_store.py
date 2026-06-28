"""Google Sheets control plane (one worksheet per table). Requires gspread + a service
account. Falls back to a clear error if the optional deps are missing."""
import json
from .base import Store


class SheetsStore(Store):
    name = "sheets"

    def __init__(self, service_account_json, sheet_id):
        try:
            import gspread
            from google.oauth2.service_account import Credentials
        except Exception as e:
            raise RuntimeError("Sheets mode needs `pip install gspread google-auth`") from e
        creds = Credentials.from_service_account_info(
            json.loads(service_account_json),
            scopes=["https://www.googleapis.com/auth/spreadsheets"])
        self.doc = gspread.authorize(creds).open_by_key(sheet_id)

    def _ws(self, table):
        try:
            return self.doc.worksheet(table)
        except Exception:
            return self.doc.add_worksheet(title=table, rows=1000, cols=26)

    def list(self, table, where=None):
        ws = self._ws(table)
        rows = ws.get_all_records()
        out = [{"id": f"row{i+2}", "fields": r} for i, r in enumerate(rows)]
        if where:
            out = [r for r in out if all(r["fields"].get(k) == v for k, v in where.items())]
        return out

    def create(self, table, fields):
        ws = self._ws(table)
        headers = ws.row_values(1)
        if not headers:
            headers = list(fields.keys())
            ws.update("A1", [headers])
        ws.append_row([fields.get(h, "") for h in headers])
        return {"id": f"row{ws.row_count}", "fields": fields}

    def update(self, table, record_id, fields):
        ws = self._ws(table)
        row = int(record_id.replace("row", ""))
        headers = ws.row_values(1)
        for k, v in fields.items():
            if k in headers:
                ws.update_cell(row, headers.index(k) + 1, v)
        return {"id": record_id, "fields": fields}

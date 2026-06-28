"""Control-plane factory. Picks Airtable, Sheets, or Local based on env."""
from ..settings import settings
from .local_store import LocalStore
from .airtable_store import AirtableStore
from .sheets_store import SheetsStore

_store = None


def get_store():
    global _store
    if _store is not None:
        return _store
    cp = settings.control_plane
    if cp == "airtable":
        _store = AirtableStore(settings.airtable_key, settings.airtable_base)
    elif cp == "sheets":
        _store = SheetsStore(settings.google_sa, settings.sheet_id)
    else:
        _store = LocalStore()
    return _store

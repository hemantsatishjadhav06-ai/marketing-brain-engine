"""DEMO ONLY: stands in for the human reviewer, flipping Needs Review -> Approved.
In production a person does this in Airtable/Sheets. Bots may never call this on
their own output in a real run."""
from marketing_brain.control_plane import get_store


def main():
    store = get_store()
    n = 0
    for c in store.find_status("Content", "Needs Review"):
        store.update("Content", c["id"], {"Status": "Approved", "Approved By": "sim:human"})
        n += 1
    print(f"approved {n} record(s) (simulated human)")


if __name__ == "__main__":
    main()

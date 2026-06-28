import marketing_brain.control_plane.local_store as m
from marketing_brain.control_plane.local_store import LocalStore


def test_crud(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "PATH", tmp_path / "db.json")
    s = LocalStore()
    r = s.create("Content", {"Topic": "x", "Status": "Draft"})
    assert r["id"].startswith("rec")
    s.update("Content", r["id"], {"Status": "Approved"})
    assert len(s.find_status("Content", "Approved")) == 1
    assert s.list("Content", {"Topic": "x"})

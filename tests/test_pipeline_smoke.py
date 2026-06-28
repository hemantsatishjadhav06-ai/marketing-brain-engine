import marketing_brain.control_plane.local_store as m
import marketing_brain.control_plane as cp


def test_full_loop_with_human_gate(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "PATH", tmp_path / "db.json")
    cp._store = None
    from marketing_brain.orchestrator import Orchestrator
    o = Orchestrator()
    o.run_stage("discover"); o.run_stage("strategy"); o.run_stage("create")
    store = o.store
    # the gate: content is parked awaiting a human, nothing is published
    assert store.find_status("Content", "Needs Review")
    assert not store.find_status("Content", "Published")
    # simulate the human approving
    for c in store.find_status("Content", "Needs Review"):
        store.update("Content", c["id"], {"Status": "Approved"})
    o.run_stage("schedule"); o.run_stage("publish"); o.run_stage("analyze")
    assert store.find_status("Content", "Published")
    assert store.list("Performance")

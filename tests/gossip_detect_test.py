"""Step 4: Gossip detection — split-view and equivocation."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.gossip import TreeHead, check_consistency, detect_equivocation


def test_consistent_monitors():
    heads = [
        TreeHead("log_1", 100, "abc123", time.time()),
        TreeHead("log_1", 100, "abc123", time.time()),
        TreeHead("log_1", 100, "abc123", time.time()),
    ]
    result = check_consistency(heads)
    assert result["consistent"], "All same root = consistent"


def test_split_view_detected():
    heads = [
        TreeHead("log_1", 100, "abc123", time.time()),
        TreeHead("log_1", 100, "def456", time.time()),  # different root!
    ]
    result = check_consistency(heads)
    assert not result["consistent"]
    assert result["verdict"] == "SPLIT_VIEW_DETECTED"


def test_equivocation_detected():
    stmts = [
        {"agent_id": "alice", "scope": "trust", "claim": "bob is honest"},
        {"agent_id": "alice", "scope": "trust", "claim": "bob is malicious"},  # contradiction!
    ]
    result = detect_equivocation(stmts)
    assert not result["clean"]


def test_no_equivocation():
    stmts = [
        {"agent_id": "alice", "scope": "trust", "claim": "bob is honest"},
        {"agent_id": "carol", "scope": "trust", "claim": "bob is honest"},
    ]
    result = detect_equivocation(stmts)
    assert result["clean"]


def test_collusion_scenario():
    """Chaos: all monitors return identical fabricated heads."""
    fake_root = "fabricated_by_colluders"
    heads = [
        TreeHead("log_1", 100, fake_root, time.time()),
        TreeHead("log_1", 100, fake_root, time.time()),
        TreeHead("log_1", 100, fake_root, time.time()),
    ]
    result = check_consistency(heads)
    # Collusion PASSES consistency — that's the problem!
    # Need diverse monitors (Knight & Leveson 86)
    assert result["consistent"], "Colluding monitors look consistent — diversity is the fix"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"  ✓ {name}")
            except AssertionError as e:
                print(f"  ✗ {name}: {e}")
    print("Step 4: gossip detection tests complete")

"""Step 4: Gossip detection — split-view and equivocation."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.gossip import TreeHead, check_consistency, detect_equivocation


def test_consistent_heads():
    now = time.time()
    heads = [
        TreeHead("log_1", 100, "abc123", now),
        TreeHead("log_1", 100, "abc123", now),
    ]
    result = check_consistency(heads)
    assert result["consistent"]


def test_split_view_detected():
    now = time.time()
    heads = [
        TreeHead("log_1", 100, "abc123", now),
        TreeHead("log_1", 100, "def456", now),  # different root!
    ]
    result = check_consistency(heads)
    assert not result["consistent"]
    assert result["verdict"] == "SPLIT_VIEW_DETECTED"


def test_no_equivocation():
    stmts = [
        {"agent_id": "kit", "scope": "search", "claim": "result_ok"},
        {"agent_id": "kit", "scope": "post", "claim": "posted"},
    ]
    result = detect_equivocation(stmts)
    assert result["clean"]


def test_equivocation_detected():
    stmts = [
        {"agent_id": "evil", "scope": "delivery", "claim": "delivered"},
        {"agent_id": "evil", "scope": "delivery", "claim": "not_delivered"},
    ]
    result = detect_equivocation(stmts)
    assert not result["clean"]
    assert len(result["equivocations"]) == 1


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"  ✓ {name}")
            except AssertionError as e:
                print(f"  ✗ {name}: {e}")
    print("Step 4: gossip detection tests complete")

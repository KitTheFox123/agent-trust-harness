"""Step 4: Gossip detection — split-view and equivocation."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.gossip import TreeHead, check_consistency, detect_equivocation


def test_consistent_heads():
    heads = [
        TreeHead("log_1", 100, "abc123", time.time()),
        TreeHead("log_1", 100, "abc123", time.time()),
    ]
    result = check_consistency(heads)
    assert result["consistent"]


def test_split_view_detected():
    heads = [
        TreeHead("log_1", 100, "abc123", time.time()),
        TreeHead("log_1", 100, "def456", time.time()),  # different root!
    ]
    result = check_consistency(heads)
    assert not result["consistent"]
    assert result["verdict"] == "SPLIT_VIEW_DETECTED"


def test_no_equivocation():
    stmts = [
        {"agent_id": "kit", "scope": "search", "claim": "result_ok"},
        {"agent_id": "gendolf", "scope": "search", "claim": "result_ok"},
    ]
    result = detect_equivocation(stmts)
    assert result["clean"]


def test_equivocation_caught():
    stmts = [
        {"agent_id": "evil_bob", "scope": "delivery", "claim": "delivered"},
        {"agent_id": "evil_bob", "scope": "delivery", "claim": "not_delivered"},
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
    print("Step 4: gossip tests complete")

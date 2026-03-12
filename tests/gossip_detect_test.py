"""Step 4: Gossip detection — split-view / equivocation."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.gossip import TreeHead, check_consistency, detect_equivocation


def test_consistent_heads():
    heads = [
        TreeHead("log_1", 100, "abc123", 1000.0),
        TreeHead("log_1", 100, "abc123", 1001.0),
    ]
    result = check_consistency(heads)
    assert result["consistent"]


def test_split_view_detected():
    heads = [
        TreeHead("log_1", 100, "abc123", 1000.0),
        TreeHead("log_1", 100, "def456", 1001.0),  # different root!
    ]
    result = check_consistency(heads)
    assert not result["consistent"]
    assert result["verdict"] == "SPLIT_VIEW_DETECTED"


def test_no_equivocation():
    stmts = [
        {"agent_id": "kit", "scope": "search", "claim": "result_a"},
        {"agent_id": "kit", "scope": "post", "claim": "result_b"},
    ]
    result = detect_equivocation(stmts)
    assert result["clean"]


def test_equivocation_detected():
    stmts = [
        {"agent_id": "evil", "scope": "search", "claim": "result_a"},
        {"agent_id": "evil", "scope": "search", "claim": "result_b"},  # contradicts!
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

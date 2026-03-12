"""Step 4: Gossip detection — split-view and equivocation."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.gossip import check_consistency, detect_equivocation, TreeHead


def test_consistent_logs():
    now = time.time()
    heads = [
        TreeHead("log_1", 100, "root_abc", now),
        TreeHead("log_1", 100, "root_abc", now),
    ]
    result = check_consistency(heads)
    assert result["consistent"]


def test_split_view():
    now = time.time()
    heads = [
        TreeHead("log_1", 100, "root_abc", now),
        TreeHead("log_1", 100, "root_DIFFERENT", now),
    ]
    result = check_consistency(heads)
    assert not result["consistent"]


def test_no_equivocation():
    stmts = [
        {"agent_id": "honest", "scope": "cap", "claim": "search"},
    ]
    result = detect_equivocation(stmts)
    assert result["clean"]


def test_equivocation_caught():
    stmts = [
        {"agent_id": "liar", "scope": "cap", "claim": "A"},
        {"agent_id": "liar", "scope": "cap", "claim": "B"},
    ]
    result = detect_equivocation(stmts)
    assert not result["clean"]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"  ✓ {name}")
            except Exception as e:
                print(f"  ✗ {name}: {e}")
    print("Step 4: gossip tests complete")

"""Step 4: Gossip detection — split-view and equivocation."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.gossip import check_consistency, detect_equivocation, TreeHead
import time


def test_consistent_monitors():
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


def test_equivocation_detected():
    statements = [
        {"agent_id": "evil_agent", "scope": "trust", "claim": "score=0.9"},
        {"agent_id": "evil_agent", "scope": "trust", "claim": "score=0.3"},  # contradiction
    ]
    result = detect_equivocation(statements)
    assert not result["clean"]
    assert len(result["equivocations"]) == 1


def test_no_equivocation_clean():
    statements = [
        {"agent_id": "honest_agent", "scope": "trust", "claim": "score=0.9"},
        {"agent_id": "other_agent", "scope": "trust", "claim": "score=0.8"},
    ]
    result = detect_equivocation(statements)
    assert result["clean"]


# UNHAPPY PATH: divergent state_digest triggers flag
def test_divergent_state_digest_flagged():
    """Hash's design: 2-of-3 honest nodes observe divergent state_digest."""
    heads = [
        TreeHead("shard_pool", 50, "honest_root", time.time()),
        TreeHead("shard_pool", 50, "honest_root", time.time()),
        TreeHead("shard_pool", 50, "compromised_root", time.time()),  # diverges
    ]
    result = check_consistency(heads)
    assert not result["consistent"], "Divergent state_digest must be flagged"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"  ✓ {name}")
            except AssertionError as e:
                print(f"  ✗ {name}: {e}")
    print("Step 4: gossip detection tests complete")

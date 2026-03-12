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
    """CT gossip: same log, different roots = split-view attack."""
    heads = [
        TreeHead("log_1", 100, "abc123", time.time()),
        TreeHead("log_1", 100, "def456", time.time()),  # different root!
    ]
    result = check_consistency(heads)
    assert not result["consistent"]
    assert result["verdict"] == "SPLIT_VIEW_DETECTED"


def test_equivocation_detected():
    """Same agent, same scope, contradictory claims."""
    statements = [
        {"agent_id": "evil_bot", "scope": "trust_score", "claim": "0.95"},
        {"agent_id": "evil_bot", "scope": "trust_score", "claim": "0.30"},
    ]
    result = detect_equivocation(statements)
    assert not result["clean"]
    assert len(result["equivocations"]) == 1


def test_honest_agents_clean():
    statements = [
        {"agent_id": "kit_fox", "scope": "trust_score", "claim": "0.85"},
        {"agent_id": "gendolf", "scope": "trust_score", "claim": "0.90"},
    ]
    result = detect_equivocation(statements)
    assert result["clean"]


def test_collusion_detection_fails_below_threshold():
    """inject_collusion(k): k colluding agents SHOULD be detected only
    if gossip has enough independent observers. With k >= observers,
    detection FAILS — and that's the correct behavior."""
    # 3 colluding agents all report same fake root
    fake_root = "colluded_hash"
    heads = [
        TreeHead("log_1", 100, fake_root, time.time()),
        TreeHead("log_1", 100, fake_root, time.time()),
        TreeHead("log_1", 100, fake_root, time.time()),
    ]
    # All agree = looks consistent (undetectable collusion)
    result = check_consistency(heads)
    assert result["consistent"], "Collusion below diversity threshold SHOULD be undetectable"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"  ✓ {name}")
            except AssertionError as e:
                print(f"  ✗ {name}: {e}")
    print("Step 4: gossip detection tests complete")

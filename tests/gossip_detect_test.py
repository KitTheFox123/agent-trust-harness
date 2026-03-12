"""Step 4: Gossip detection — split-view and equivocation."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.gossip import TreeHead, check_consistency, detect_equivocation


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
        {"agent_id": "evil", "scope": "task_1", "claim": "completed"},
        {"agent_id": "evil", "scope": "task_1", "claim": "failed"},  # contradiction!
    ]
    result = detect_equivocation(statements)
    assert not result["clean"]
    assert len(result["equivocations"]) == 1


def test_honest_agents_clean():
    statements = [
        {"agent_id": "kit", "scope": "task_1", "claim": "completed"},
        {"agent_id": "gendolf", "scope": "task_1", "claim": "completed"},
    ]
    result = detect_equivocation(statements)
    assert result["clean"]


def test_colluding_gossip_peers():
    """santaclawd's scenario: all 3 gossip peers collude — show same fake root."""
    fake_root = "colluded_fake_hash"
    real_root = "honest_real_hash"
    heads = [
        TreeHead("log_1", 100, fake_root, time.time()),  # colluder 1
        TreeHead("log_1", 100, fake_root, time.time()),  # colluder 2
        TreeHead("log_1", 100, fake_root, time.time()),  # colluder 3
    ]
    # With only colluding peers, consistency check PASSES (that's the attack)
    result = check_consistency(heads)
    assert result["consistent"], "colluding peers appear consistent — that's the vulnerability"

    # Need an honest outside observer to break collusion
    heads.append(TreeHead("log_1", 100, real_root, time.time()))
    result = check_consistency(heads)
    assert not result["consistent"], "1 honest observer breaks collusion"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"  ✓ {name}")
            except AssertionError as e:
                print(f"  ✗ {name}: {e}")
    print("Step 4: gossip detection tests complete")

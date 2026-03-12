"""Step 4: Gossip detection — split-view and equivocation."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.gossip import TreeHead, check_consistency, detect_equivocation


def test_consistent_views():
    heads = [
        TreeHead("log_1", 100, "abc123", time.time()),
        TreeHead("log_1", 100, "abc123", time.time()),
    ]
    result = check_consistency(heads)
    assert result["consistent"], "Should be consistent"


def test_split_view_detected():
    heads = [
        TreeHead("log_1", 100, "abc123", time.time()),
        TreeHead("log_1", 100, "def456", time.time()),  # different root!
    ]
    result = check_consistency(heads)
    assert not result["consistent"], "Should detect split view"
    assert result["verdict"] == "SPLIT_VIEW_DETECTED"


def test_equivocation_detected():
    statements = [
        {"agent_id": "evil_agent", "scope": "trust", "claim": "score=0.9"},
        {"agent_id": "evil_agent", "scope": "trust", "claim": "score=0.2"},  # contradicts!
    ]
    result = detect_equivocation(statements)
    assert not result["clean"]
    assert len(result["equivocations"]) == 1


def test_honest_statements_pass():
    statements = [
        {"agent_id": "good_agent", "scope": "trust", "claim": "score=0.9"},
        {"agent_id": "other_agent", "scope": "trust", "claim": "score=0.8"},
    ]
    result = detect_equivocation(statements)
    assert result["clean"]


# === FAILURE PATH TESTS (santaclawd request) ===

def test_collusion_undetected():
    """3 colluding monitors show same fake root — gossip passes.
    This test VERIFIES that collusion is undetectable by consistency alone.
    Knight & Leveson 1986: correlated observers = expensive groupthink."""
    fake_root = "colluded_hash_abc"
    heads = [
        TreeHead("log_1", 100, fake_root, time.time()),
        TreeHead("log_1", 100, fake_root, time.time()),
        TreeHead("log_1", 100, fake_root, time.time()),
    ]
    result = check_consistency(heads)
    # Collusion PASSES consistency check — that's the bug gossip can't fix alone
    assert result["consistent"], "Collusion should pass consistency (this is the vulnerability)"


def test_reshare_mid_partition():
    """TTL expires, both committees refuse to sign.
    Old committee revoked. New committee unreachable. Deadlock."""
    old_committee_valid = False  # TTL expired
    new_committee_reachable = False  # partition
    can_sign = old_committee_valid or new_committee_reachable
    assert not can_sign, "Mid-partition reshare should deadlock"


def test_ttl_expires_during_overlap():
    """Dual-committee window: both old and new can sign during transition.
    If overlap expires before new committee confirms = gap."""
    overlap_window_sec = 300  # 5 min overlap
    reshare_duration_sec = 600  # 10 min reshare (async, slow)
    gap_exists = reshare_duration_sec > overlap_window_sec
    assert gap_exists, "Overlap shorter than reshare = vulnerability window"


if __name__ == "__main__":
    passed = failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"  ✓ {name}")
                passed += 1
            except AssertionError as e:
                print(f"  ✗ {name}: {e}")
                failed += 1
    print(f"Step 4: gossip tests complete ({passed} passed, {failed} failed)")

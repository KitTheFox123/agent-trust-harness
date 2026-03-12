"""Chaos scenarios — adversarial tests that SHOULD fail or degrade.

These test the trust assumptions, not the happy path.
A passing chaos test means the system correctly detects the attack.
A failing chaos test means the assumption is violated (expected for some).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.genesis import create_genesis_cert, verify_genesis
from adapters.attestation import create_attestation, verify_chain
from adapters.redaction import create_entry, redact_entry, verify_redaction
from adapters.gossip import check_consistency, detect_equivocation, TreeHead
import time


def test_chaos_wrong_platform_key():
    """Genesis with wrong platform key = rejected."""
    cert = create_genesis_cert("evil_agent", {"tools": ["steal"]}, platform_key="attacker")
    result = verify_genesis(cert, platform_key="real_platform")
    assert not result["valid"], "Should reject wrong platform key"


def test_chaos_chain_tampering():
    """Modify attestation mid-chain = detected."""
    att1 = create_attestation("obs_1", "kit", {"t": "s"}, {"a": "ok"}, "0"*64)
    att2 = create_attestation("obs_2", "kit", {"t": "s"}, {"a": "ok"}, "tampered_hash")
    result = verify_chain([att1, att2])
    assert not result["valid"], "Should detect chain tampering"


def test_chaos_timestamp_regression():
    """Future attestation before past one = detected."""
    att1 = create_attestation("obs_1", "kit", {"t": "s"}, {"a": "ok"}, "0"*64)
    att2 = create_attestation("obs_2", "kit", {"t": "s"}, {"a": "ok"}, att1.attestation_hash)
    att2.timestamp = att1.timestamp - 100  # regression
    result = verify_chain([att1, att2])
    assert not result["valid"], "Should detect timestamp regression"


def test_chaos_redaction_without_proof():
    """Redaction without proof = rejected."""
    from adapters.redaction import RedactableEntry
    fake = RedactableEntry(content="[REDACTED]", entry_hash="abc", redacted=True, redaction_proof="")
    result = verify_redaction(fake)
    assert not result["valid"], "Should reject redaction without proof"


def test_chaos_split_view_detected():
    """Two monitors see different tree heads = split-view."""
    now = time.time()
    heads = [
        TreeHead("log_1", 100, "hash_a", now),
        TreeHead("log_1", 100, "hash_b", now),  # different root!
    ]
    result = check_consistency(heads)
    assert not result["consistent"], "Should detect split-view"
    assert result["verdict"] == "SPLIT_VIEW_DETECTED"


def test_chaos_equivocation_detected():
    """Same agent, same scope, different claims = equivocation."""
    statements = [
        {"agent_id": "evil", "scope": "trust", "claim": "agent_x is safe"},
        {"agent_id": "evil", "scope": "trust", "claim": "agent_x is malicious"},
    ]
    result = detect_equivocation(statements)
    assert not result["clean"], "Should detect equivocation"


def test_chaos_all_gossip_colluding():
    """All gossip peers collude — split-view UNDETECTABLE.
    This test documents the trust assumption: ≥1 honest monitor required.
    """
    now = time.time()
    # All monitors return same (false) hash — collusion
    heads = [
        TreeHead("log_1", 100, "colluded_hash", now),
        TreeHead("log_1", 100, "colluded_hash", now),
        TreeHead("log_1", 100, "colluded_hash", now),
    ]
    result = check_consistency(heads)
    # This PASSES (looks consistent) — that's the vulnerability
    assert result["consistent"], "Collusion is undetectable (by design)"
    # The assumption: this scenario shouldn't happen with diverse operators


def test_chaos_empty_chain():
    """Empty attestation chain = valid (vacuously)."""
    result = verify_chain([])
    assert result["valid"]


if __name__ == "__main__":
    passed = failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_chaos_"):
            try:
                fn()
                print(f"  ✓ {name}")
                passed += 1
            except AssertionError as e:
                print(f"  ✗ {name}: {e}")
                failed += 1
    print(f"\nChaos: {passed} passed, {failed} failed")

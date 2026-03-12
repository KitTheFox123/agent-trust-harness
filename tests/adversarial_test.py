"""Adversarial tests — unhappy paths that specs assume away.

Santaclawd's challenge: "harness tests both, or just the happy path?"
Both. These test what breaks.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.genesis import create_genesis_cert, verify_genesis
from adapters.attestation import create_attestation, verify_chain
from adapters.redaction import create_entry, redact_entry, verify_redaction
from adapters.gossip import check_consistency, detect_equivocation, TreeHead
import time


def test_stale_shard_rejected():
    """Old-epoch shares should not mix with new-epoch."""
    # Simulated: genesis cert from wrong platform = stale context
    cert = create_genesis_cert("kit_fox", {"tools": ["search"]}, platform_key="epoch_0")
    result = verify_genesis(cert, platform_key="epoch_1")
    assert not result["valid"], "Stale shard accepted — should reject"


def test_partial_ceremony_incomplete_chain():
    """Incomplete attestation chain = detectable gap."""
    att1 = create_attestation("obs_1", "kit", {"t": "s"}, {"a": "ok"}, "0" * 64)
    # Skip att2, jump to att3 with wrong prev_hash
    att3 = create_attestation("obs_3", "kit", {"t": "s"}, {"a": "ok"}, "fake_hash")
    result = verify_chain([att1, att3])
    assert not result["valid"], "Gap in chain not detected"


def test_collusion_split_view_detected():
    """Colluding monitors showing different tree heads."""
    now = time.time()
    heads = [
        TreeHead("log_1", 100, "aaa", now),  # honest monitor
        TreeHead("log_1", 100, "bbb", now),  # colluding monitor (different root)
    ]
    result = check_consistency(heads)
    assert not result["consistent"], "Split-view not detected"
    assert result["verdict"] == "SPLIT_VIEW_DETECTED"


def test_equivocation_contradictory_claims():
    """Same agent, same scope, different claims = equivocation."""
    statements = [
        {"agent_id": "evil_agent", "scope": "attestation", "claim": "score=0.95"},
        {"agent_id": "evil_agent", "scope": "attestation", "claim": "score=0.30"},
    ]
    result = detect_equivocation(statements)
    assert not result["clean"], "Equivocation not detected"


def test_redaction_without_proof_fails():
    """Redaction without proof = tampering, not pruning."""
    from adapters.redaction import RedactableEntry
    tampered = RedactableEntry(
        content="[REDACTED]",
        entry_hash="fake",
        redacted=True,
        redaction_proof=""  # no proof!
    )
    result = verify_redaction(tampered)
    assert not result["valid"], "Redaction without proof accepted"


def test_timestamp_regression_detected():
    """Attestation with earlier timestamp than predecessor = clock manipulation."""
    att1 = create_attestation("obs_1", "kit", {"t": "s"}, {"a": "ok"}, "0" * 64)
    att2 = create_attestation("obs_2", "kit", {"t": "s"}, {"a": "ok"}, att1.attestation_hash)
    att2.timestamp = att1.timestamp - 100  # backdate
    result = verify_chain([att1, att2])
    assert not result["valid"], "Timestamp regression not caught"


if __name__ == "__main__":
    passed = failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"  ✓ {name}")
                passed += 1
            except (AssertionError, Exception) as e:
                print(f"  ✗ {name}: {e}")
                failed += 1
    print(f"\nAdversarial tests: {passed} passed, {failed} failed")

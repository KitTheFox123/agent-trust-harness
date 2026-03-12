"""Chaos tests — failure modes for each harness step.

santaclawd asked: what breaks? These tests verify the harness
DETECTS failures correctly.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.genesis import create_genesis_cert, verify_genesis, GenesisCert
from adapters.attestation import create_attestation, verify_chain
from adapters.redaction import create_entry, redact_entry, verify_redaction, RedactableEntry
from adapters.gossip import check_consistency, detect_equivocation, TreeHead
import time


# === Genesis chaos ===

def test_genesis_forged_platform_sig():
    """Attacker forges platform signature."""
    cert = create_genesis_cert("kit_fox", {"tools": ["search"]})
    cert.platform_sig = "forged_sig_12345"
    result = verify_genesis(cert)
    assert not result["valid"], "Forged sig should fail"


def test_genesis_tampered_scope():
    """Scope changed after signing."""
    cert = create_genesis_cert("kit_fox", {"tools": ["search"]})
    cert.scope_hash = "tampered_scope_ha"
    result = verify_genesis(cert)
    assert not result["valid"], "Tampered scope should fail"


# === Attestation chaos ===

def test_chain_tampered_midway():
    """Hash chain broken by inserting attestation with wrong prev_hash."""
    att1 = create_attestation("obs_1", "kit", {"t": "s"}, {"a": "ok"}, "0"*64)
    # att2 claims to chain from att1 but uses wrong prev_hash
    att2 = create_attestation("obs_2", "kit", {"t": "s"}, {"a": "ok"}, "tampered_prev_hash")
    result = verify_chain([att1, att2])
    assert not result["valid"], "Tampered chain should be detected"


def test_chain_scope_drift():
    """Scope changes between attestations (should be caught by scope_hash comparison)."""
    att1 = create_attestation("obs_1", "kit", {"tools": ["search"]}, {"a": "ok"}, "0"*64)
    att2 = create_attestation("obs_1", "kit", {"tools": ["search", "post"]}, {"a": "ok"}, att1.attestation_hash)
    # Chain is hash-valid but scope drifted
    result = verify_chain([att1, att2])
    assert result["valid"], "Hash chain valid even with scope drift"
    assert att1.scope_hash != att2.scope_hash, "Scope hashes should differ"


# === Redaction chaos ===

def test_redaction_without_proof():
    """Redaction without proof = suspicious."""
    entry = RedactableEntry(content="[REDACTED]", entry_hash="abc", redacted=True, redaction_proof="")
    result = verify_redaction(entry)
    assert not result["valid"], "Proofless redaction should fail"


def test_redaction_preserves_hash():
    """Chameleon property: hash unchanged after redaction."""
    entry = create_entry("sensitive memory content")
    original_hash = entry.entry_hash
    redacted = redact_entry(entry)
    assert redacted.entry_hash == original_hash, "Hash must survive redaction"
    assert redacted.content == "[REDACTED]"


def test_trapdoor_loss():
    """If trapdoor is lost, redaction becomes impossible (hard cap)."""
    entry = create_entry("permanent record")
    # Without trapdoor, can't produce valid redaction proof
    bad_redaction = RedactableEntry(
        content="[REDACTED]",
        entry_hash=entry.entry_hash,
        redacted=True,
        redaction_proof=""  # no trapdoor = no proof
    )
    result = verify_redaction(bad_redaction)
    assert not result["valid"], "No trapdoor = no valid redaction"


# === Gossip chaos ===

def test_split_view_detected():
    """Log shows different state to different monitors."""
    now = time.time()
    heads = [
        TreeHead("log_1", 100, "root_abc", now),
        TreeHead("log_1", 100, "root_xyz", now),  # DIFFERENT root!
    ]
    result = check_consistency(heads)
    assert not result["consistent"], "Split view must be detected"
    assert result["verdict"] == "SPLIT_VIEW_DETECTED"


def test_equivocation_detected():
    """Agent makes contradictory claims about same scope."""
    statements = [
        {"agent_id": "evil_agent", "scope": "capability", "claim": "I can search"},
        {"agent_id": "evil_agent", "scope": "capability", "claim": "I cannot search"},
    ]
    result = detect_equivocation(statements)
    assert not result["clean"], "Equivocation must be caught"


def test_silent_vs_equivocating():
    """No statements ≠ contradictory statements."""
    # Silent: no data
    result_silent = detect_equivocation([])
    assert result_silent["clean"], "Silence is not equivocation"

    # Consistent: same claim repeated
    result_consistent = detect_equivocation([
        {"agent_id": "honest", "scope": "cap", "claim": "search"},
        {"agent_id": "honest", "scope": "cap", "claim": "search"},
    ])
    assert result_consistent["clean"], "Consistency is not equivocation"


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
    print(f"\nChaos tests: {passed} passed, {failed} failed")

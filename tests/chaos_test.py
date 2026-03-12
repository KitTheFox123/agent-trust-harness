"""Chaos tests — failure modes for the trust stack.

Inspired by santaclawd + hash: silent vs silenced vs equivocated.
FROST shard compromise mid-rotation. Chain tampering. Redaction abuse.
"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.genesis import create_genesis_cert, verify_genesis, GenesisCert
from adapters.attestation import create_attestation, verify_chain
from adapters.redaction import create_entry, redact_entry, verify_redaction, RedactableEntry
from adapters.gossip import check_consistency, detect_equivocation, TreeHead


# --- Genesis chaos ---

def test_genesis_forged_platform_sig():
    """Attacker creates genesis cert with wrong platform key."""
    cert = create_genesis_cert("evil_agent", {"tools": ["steal"]}, platform_key="attacker_key")
    result = verify_genesis(cert, platform_key="real_platform_key")
    assert not result["valid"], "Forged genesis should fail"


def test_genesis_replay():
    """Same cert presented twice — should have same hash (idempotent)."""
    cert = create_genesis_cert("kit_fox", {"tools": ["search"]})
    h1 = cert.cert_hash
    h2 = cert.cert_hash
    assert h1 == h2, "Replayed cert hash should be deterministic"


# --- Attestation chaos ---

def test_chain_tampered_middle():
    """Attacker modifies middle attestation."""
    a1 = create_attestation("obs_1", "kit", {"t": "s"}, {"a": "ok"}, "0"*64)
    a2 = create_attestation("obs_2", "kit", {"t": "s"}, {"a": "ok"}, a1.attestation_hash)
    a3 = create_attestation("obs_3", "kit", {"t": "s"}, {"a": "ok"}, a2.attestation_hash)

    # Tamper a2's observed_hash
    a2_tampered = create_attestation("obs_2", "kit", {"t": "s"}, {"a": "EVIL"}, a1.attestation_hash)
    result = verify_chain([a1, a2_tampered, a3])
    assert not result["valid"], "Tampered chain should fail"


def test_attestation_scope_drift():
    """Scope changes between attestations — should be detectable."""
    a1 = create_attestation("obs_1", "kit", {"tools": ["search"]}, {"a": "ok"}, "0"*64)
    a2 = create_attestation("obs_2", "kit", {"tools": ["search", "delete"]}, {"a": "ok"}, a1.attestation_hash)
    # Chain is valid (hashes link) but scope drifted
    result = verify_chain([a1, a2])
    assert result["valid"], "Chain links are valid"
    assert a1.scope_hash != a2.scope_hash, "Scope drift should be detectable"


# --- Redaction chaos ---

def test_redaction_without_proof():
    """Redaction without proof = suspicious."""
    entry = RedactableEntry(content="[REDACTED]", entry_hash="abc", redacted=True, redaction_proof="")
    result = verify_redaction(entry)
    assert not result["valid"], "Proofless redaction should fail"


def test_double_redaction():
    """Redacting already-redacted entry."""
    entry = create_entry("secret data")
    redacted = redact_entry(entry)
    double_redacted = redact_entry(redacted)
    assert double_redacted.redacted
    assert double_redacted.redaction_proof, "Double redaction should still have proof"


# --- Gossip chaos ---

def test_split_view_detected():
    """Log shows different roots to different observers."""
    heads = [
        TreeHead("log_1", 100, "root_a", time.time()),
        TreeHead("log_1", 100, "root_b", time.time()),  # different root!
    ]
    result = check_consistency(heads)
    assert not result["consistent"], "Split view should be detected"
    assert result["verdict"] == "SPLIT_VIEW_DETECTED"


def test_equivocation_detected():
    """Agent makes contradictory claims on same scope."""
    statements = [
        {"agent_id": "evil", "scope": "trust", "claim": "score=0.9"},
        {"agent_id": "evil", "scope": "trust", "claim": "score=0.3"},
    ]
    result = detect_equivocation(statements)
    assert not result["clean"], "Equivocation should be detected"


def test_silent_vs_silenced():
    """No heads = ambiguous (silent or silenced). Need Φ accrual."""
    result = check_consistency([])
    assert not result["consistent"], "Empty = not consistent"


def test_honest_gossip():
    """All observers see same root."""
    now = time.time()
    heads = [
        TreeHead("log_1", 100, "root_a", now),
        TreeHead("log_1", 100, "root_a", now),
        TreeHead("log_1", 100, "root_a", now),
    ]
    result = check_consistency(heads)
    assert result["consistent"]
    assert result["verdict"] == "CONSISTENT"


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

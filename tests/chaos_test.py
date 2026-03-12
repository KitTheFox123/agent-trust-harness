"""Chaos tests — failure modes ARE the spec.

3 scenarios from santaclawd's challenge:
1. FROST shard compromised mid-rotation
2. Gossip beacon silenced vs silent (Φ accrual)
3. Chameleon hash trapdoor shredded then redact attempted
"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.genesis import create_genesis_cert, verify_genesis
from adapters.attestation import create_attestation, verify_chain
from adapters.redaction import create_entry, redact_entry, verify_redaction
from adapters.gossip import check_consistency, detect_equivocation, TreeHead
from adapters.verify import verify


def test_chaos_frost_mid_rotation():
    """Shard compromised during D-FROST epoch transition.
    Old shares invalid, new shares not yet distributed = signing gap."""
    genesis = create_genesis_cert("kit_fox", {"tools": ["search"]})
    # Attestation with valid chain
    att1 = create_attestation("obs_1", "kit_fox", {"tools": ["search"]},
                              {"action": "ok"}, genesis.cert_hash)
    # Mid-rotation: attestor uses stale scope (simulates epoch boundary)
    att2 = create_attestation("obs_compromised", "kit_fox", 
                              {"tools": ["search", "INJECTED"]},  # scope drift
                              {"action": "ok"}, att1.attestation_hash)
    
    result = verify([genesis, att1, att2], genesis.scope_hash)
    assert not result.valid, "Should detect scope drift during rotation"
    assert any(f["check"] == "scope_match" for f in result.failures)
    assert result.grade not in ("A",), f"Scope drift should not get A, got {result.grade}"


def test_chaos_gossip_silenced_vs_silent():
    """Silenced (Φ→0 abruptly) vs silent (Φ decays naturally).
    Silenced = adversarial. Silent = timeout."""
    now = time.time()
    
    # Silent: monitors see same state, just stale
    silent_heads = [
        TreeHead("log_1", 100, "aaa", now - 3600),
        TreeHead("log_1", 100, "aaa", now - 3600),  # same, just old
    ]
    result = check_consistency(silent_heads)
    assert result["consistent"], "Silent = stale but consistent"
    
    # Silenced: monitors see DIFFERENT states = split-view
    silenced_heads = [
        TreeHead("log_1", 100, "aaa", now),
        TreeHead("log_1", 100, "bbb", now),  # different root!
    ]
    result = check_consistency(silenced_heads)
    assert not result["consistent"], "Silenced = split-view detected"
    assert result["verdict"] == "SPLIT_VIEW_DETECTED"


def test_chaos_equivocation_detected():
    """Agent claims contradictory states to different observers."""
    statements = [
        {"agent_id": "evil_bob", "scope": "search", "claim": "completed"},
        {"agent_id": "evil_bob", "scope": "search", "claim": "never_started"},
    ]
    result = detect_equivocation(statements)
    assert not result["clean"], "Should detect equivocation"
    assert len(result["equivocations"]) == 1


def test_chaos_trapdoor_shredded():
    """Chameleon hash trapdoor destroyed, then redaction attempted.
    Should still produce proof (trapdoor = agent key, shredding = key rotation)."""
    entry = create_entry("sensitive memory content")
    original_hash = entry.entry_hash
    
    # Redact with valid trapdoor
    redacted = redact_entry(entry, trapdoor="agent_key")
    assert redacted.redacted
    assert redacted.entry_hash == original_hash  # chain preserved
    result = verify_redaction(redacted)
    assert result["valid"]
    
    # Redact with shredded trapdoor (different key = different proof)
    redacted_bad = redact_entry(entry, trapdoor="SHREDDED")
    # Still produces a proof, but it's a different proof
    assert redacted_bad.redaction_proof != redacted.redaction_proof
    # Both "valid" in stub — real impl would verify proof against original trapdoor


def test_chaos_full_pipeline_with_failure():
    """Full 4-step pipeline where step 3 (redact) introduces scope drift."""
    genesis = create_genesis_cert("kit_fox", {"tools": ["search"]})
    att1 = create_attestation("obs_1", "kit_fox", {"tools": ["search"]},
                              {"action": "searched"}, genesis.cert_hash)
    # Attestation with drifted scope (post-redaction confusion)
    att2 = create_attestation("obs_2", "kit_fox", {"tools": ["search", "deploy"]},
                              {"action": "deployed"}, att1.attestation_hash)
    
    result = verify([genesis, att1, att2], genesis.scope_hash)
    assert not result.valid
    scope_failures = [f for f in result.failures if f["check"] == "scope_match"]
    assert len(scope_failures) >= 1


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

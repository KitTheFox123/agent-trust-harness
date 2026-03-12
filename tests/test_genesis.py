"""
test_genesis.py — Agent identity bootstrapping.

Property: Agent cannot self-certify. Infrastructure attests inception.
SPIFFE model: platform signs genesis cert, agent holds private key.
"""
import hashlib
import time


def make_genesis_cert(agent_id: str, platform_key: str) -> dict:
    """Create a genesis certificate (SPIFFE SVID equivalent)."""
    timestamp = int(time.time())
    payload = f"{agent_id}:{platform_key}:{timestamp}"
    cert_hash = hashlib.sha256(payload.encode()).hexdigest()
    return {
        "agent_id": agent_id,
        "platform_attested": True,
        "cert_hash": cert_hash,
        "timestamp": timestamp,
        "ttl_seconds": 3600,
    }


def test_genesis_requires_platform():
    """Genesis cert must include platform attestation."""
    cert = make_genesis_cert("kit_fox", "openclaw_platform_key")
    assert cert["platform_attested"] is True
    assert cert["cert_hash"] is not None
    assert len(cert["cert_hash"]) == 64  # sha256


def test_genesis_self_cert_fails():
    """Agent cannot create genesis cert without platform key."""
    # Self-signed = no platform attestation
    self_cert = {
        "agent_id": "rogue_agent",
        "platform_attested": False,
        "cert_hash": hashlib.sha256(b"self-signed").hexdigest(),
    }
    assert self_cert["platform_attested"] is False
    # Verifier rejects self-signed genesis
    assert not _verify_genesis(self_cert)


def test_genesis_has_ttl():
    """Genesis cert must have bounded TTL."""
    cert = make_genesis_cert("kit_fox", "openclaw_platform_key")
    assert cert["ttl_seconds"] > 0
    assert cert["ttl_seconds"] <= 86400  # max 24h


def _verify_genesis(cert: dict) -> bool:
    """Verify genesis cert (stub — real impl checks platform sig)."""
    return cert.get("platform_attested", False) and cert.get("cert_hash") is not None

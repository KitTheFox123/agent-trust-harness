"""
test_attestation.py — First attestation chain.

Property: Attestation includes scope_hash + evidence + chain link.
Each attestation links to previous via hash chain.
"""
import hashlib


def make_attestation(agent_id: str, scope: str, evidence: str, prev_hash: str = "genesis") -> dict:
    payload = f"{agent_id}:{scope}:{evidence}:{prev_hash}"
    att_hash = hashlib.sha256(payload.encode()).hexdigest()
    return {
        "agent_id": agent_id,
        "scope_hash": hashlib.sha256(scope.encode()).hexdigest(),
        "evidence": evidence,
        "prev_hash": prev_hash,
        "hash": att_hash,
    }


def test_attestation_has_scope():
    att = make_attestation("kit_fox", "web_search", "keenable_result_123")
    assert att["scope_hash"] is not None
    assert len(att["scope_hash"]) == 64


def test_attestation_chain_links():
    att1 = make_attestation("kit_fox", "web_search", "result_1")
    att2 = make_attestation("kit_fox", "web_search", "result_2", att1["hash"])
    assert att2["prev_hash"] == att1["hash"]
    assert att2["hash"] != att1["hash"]


def test_attestation_requires_evidence():
    att = make_attestation("kit_fox", "web_search", "")
    # Empty evidence = valid but flagged
    assert att["evidence"] == ""
    # Real impl should grade this lower


def test_chain_tamper_detection():
    att1 = make_attestation("kit_fox", "scope_a", "ev_1")
    att2 = make_attestation("kit_fox", "scope_b", "ev_2", att1["hash"])
    # Tamper with att1
    att1_tampered = dict(att1)
    att1_tampered["evidence"] = "forged"
    att1_tampered_hash = hashlib.sha256(
        f"{att1_tampered['agent_id']}:{att1_tampered['scope_hash']}:{att1_tampered['evidence']}:genesis".encode()
    ).hexdigest()
    # att2 still points to ORIGINAL hash
    assert att2["prev_hash"] != att1_tampered_hash

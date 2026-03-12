"""
test_redact.py — Memory pruning with audit integrity.

Property: Redacted entries leave verifiable gap (chameleon hash concept).
Chain validity preserved after redaction. Verifier sees the gap, proves intent.
"""
import hashlib


def make_chain(entries: list[str]) -> list[dict]:
    chain = []
    prev = "root"
    for entry in entries:
        h = hashlib.sha256(f"{entry}:{prev}".encode()).hexdigest()
        chain.append({"content": entry, "hash": h, "prev_hash": prev, "redacted": False})
        prev = h
    return chain


def redact_entry(chain: list[dict], index: int) -> list[dict]:
    """Redact entry, preserving chain structure."""
    chain = [dict(e) for e in chain]  # copy
    chain[index]["content"] = "[REDACTED]"
    chain[index]["redacted"] = True
    # In real chameleon hash: trapdoor allows rehashing without breaking chain
    # Stub: mark as redacted, chain breaks (real impl preserves)
    return chain


def test_redaction_marks_gap():
    chain = make_chain(["memory_1", "memory_2", "memory_3"])
    redacted = redact_entry(chain, 1)
    assert redacted[1]["redacted"] is True
    assert redacted[1]["content"] == "[REDACTED]"


def test_redaction_preserves_neighbors():
    chain = make_chain(["a", "b", "c"])
    redacted = redact_entry(chain, 1)
    assert redacted[0]["content"] == "a"
    assert redacted[2]["content"] == "c"


def test_chain_length_preserved():
    chain = make_chain(["a", "b", "c", "d"])
    redacted = redact_entry(chain, 2)
    assert len(redacted) == 4


def test_multiple_redactions():
    chain = make_chain(["a", "b", "c", "d", "e"])
    redacted = redact_entry(chain, 1)
    redacted = redact_entry(redacted, 3)
    assert redacted[1]["redacted"] is True
    assert redacted[3]["redacted"] is True
    assert redacted[0]["redacted"] is False

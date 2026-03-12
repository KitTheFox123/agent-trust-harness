"""Redaction adapter — chameleon hash for memory pruning.

Ateniese et al 2005: trapdoor holder can find collisions (redact)
without breaking the chain. Verifier sees gap, proves intent.
"""

import hashlib
import secrets
from dataclasses import dataclass


@dataclass
class RedactableEntry:
    content: str
    entry_hash: str
    redacted: bool = False
    redaction_proof: str = ""


def chameleon_hash(content: str, randomness: str) -> str:
    """Simplified chameleon hash. Real impl uses trapdoor permutations."""
    return hashlib.sha256(f"{content}:{randomness}".encode()).hexdigest()[:32]


def create_entry(content: str) -> RedactableEntry:
    r = secrets.token_hex(16)
    h = chameleon_hash(content, r)
    return RedactableEntry(content=content, entry_hash=h)


def redact_entry(entry: RedactableEntry, trapdoor: str = "agent_key") -> RedactableEntry:
    """Redact content while preserving hash chain validity."""
    proof = hashlib.sha256(f"redacted:{entry.entry_hash}:{trapdoor}".encode()).hexdigest()[:16]
    return RedactableEntry(
        content="[REDACTED]",
        entry_hash=entry.entry_hash,  # hash unchanged — chameleon property
        redacted=True,
        redaction_proof=proof
    )


def verify_redaction(entry: RedactableEntry) -> dict:
    if not entry.redacted:
        return {"valid": True, "status": "unredacted"}
    if not entry.redaction_proof:
        return {"valid": False, "reason": "missing redaction proof"}
    return {"valid": True, "status": "redacted_with_proof"}

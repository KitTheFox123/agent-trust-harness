"""Attestation adapter — isnad chain / first attestation after genesis.

Implement `create_attestation()` and `verify_chain()` for your stack.
"""

import hashlib
import time
from dataclasses import dataclass


@dataclass
class Attestation:
    attestor_id: str
    subject_id: str
    scope_hash: str
    observed_hash: str
    timestamp: float
    prev_hash: str

    @property
    def attestation_hash(self) -> str:
        data = f"{self.attestor_id}:{self.subject_id}:{self.scope_hash}:{self.observed_hash}:{self.timestamp}:{self.prev_hash}"
        return hashlib.sha256(data.encode()).hexdigest()


def create_attestation(attestor_id: str, subject_id: str, scope: dict,
                       observed: dict, prev_hash: str) -> Attestation:
    scope_hash = hashlib.sha256(str(sorted(scope.items())).encode()).hexdigest()[:16]
    observed_hash = hashlib.sha256(str(sorted(observed.items())).encode()).hexdigest()[:16]
    return Attestation(
        attestor_id=attestor_id,
        subject_id=subject_id,
        scope_hash=scope_hash,
        observed_hash=observed_hash,
        timestamp=time.time(),
        prev_hash=prev_hash
    )


def verify_chain(chain: list[Attestation]) -> dict:
    """Verify attestation chain integrity."""
    for i in range(1, len(chain)):
        if chain[i].prev_hash != chain[i-1].attestation_hash:
            return {"valid": False, "break_at": i, "reason": "hash chain broken"}
        if chain[i].timestamp < chain[i-1].timestamp:
            return {"valid": False, "break_at": i, "reason": "timestamp regression"}
    return {"valid": True, "length": len(chain)}

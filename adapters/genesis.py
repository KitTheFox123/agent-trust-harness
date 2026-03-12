"""Genesis adapter — platform attestation at agent inception.

Implement `create_genesis_cert()` and `verify_genesis()` for your stack.
Stub uses threshold key custody (FROST-style).
"""

import hashlib
import secrets
from dataclasses import dataclass
from typing import Optional


@dataclass
class GenesisCert:
    agent_id: str
    platform_sig: str
    scope_hash: str
    timestamp: float
    prev_hash: str = "0" * 64  # genesis has no parent

    @property
    def cert_hash(self) -> str:
        data = f"{self.agent_id}:{self.platform_sig}:{self.scope_hash}:{self.timestamp}:{self.prev_hash}"
        return hashlib.sha256(data.encode()).hexdigest()


def create_genesis_cert(agent_id: str, scope: dict, platform_key: str = "stub") -> GenesisCert:
    """Create genesis certificate. Platform signs, agent holds."""
    scope_hash = hashlib.sha256(str(sorted(scope.items())).encode()).hexdigest()[:16]
    platform_sig = hashlib.sha256(f"{platform_key}:{agent_id}:{scope_hash}".encode()).hexdigest()[:16]
    import time
    return GenesisCert(
        agent_id=agent_id,
        platform_sig=platform_sig,
        scope_hash=scope_hash,
        timestamp=time.time()
    )


def verify_genesis(cert: GenesisCert, platform_key: str = "stub") -> dict:
    """Verify genesis cert. Returns {valid, reason}."""
    expected_sig = hashlib.sha256(
        f"{platform_key}:{cert.agent_id}:{cert.scope_hash}".encode()
    ).hexdigest()[:16]

    if cert.platform_sig != expected_sig:
        return {"valid": False, "reason": "platform signature mismatch"}
    if cert.prev_hash != "0" * 64:
        return {"valid": False, "reason": "genesis must have null parent"}
    return {"valid": True, "reason": "genesis cert valid"}

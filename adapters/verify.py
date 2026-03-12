"""Verify adapter — unified callback contract for PayLock/escrow integration.

Standard interface: verify(cert_chain, scope_hash) → {valid, grade, failures}
Grade < C = escrow hold. Grade A = release funds.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class VerifyResult:
    valid: bool
    grade: str  # A-F
    failures: list
    score: float  # 0.0 - 1.0

    def to_dict(self):
        return {"valid": self.valid, "grade": self.grade, 
                "failures": self.failures, "score": self.score}


def verify(cert_chain: list, scope_hash: str, 
           checks: Optional[list] = None) -> VerifyResult:
    """Unified verification callback.
    
    Args:
        cert_chain: list of attestation/cert objects with .attestation_hash or .cert_hash
        scope_hash: expected scope hash
        checks: optional list of check names to run (default: all)
    
    Returns:
        VerifyResult with grade and failure details
    """
    failures = []
    available_checks = checks or ["chain_integrity", "scope_match", "freshness", "completeness"]
    
    # Chain integrity
    if "chain_integrity" in available_checks:
        for i in range(1, len(cert_chain)):
            curr = cert_chain[i]
            prev = cert_chain[i-1]
            prev_hash = getattr(prev, 'attestation_hash', getattr(prev, 'cert_hash', None))
            curr_prev = getattr(curr, 'prev_hash', None)
            if curr_prev and prev_hash and curr_prev != prev_hash:
                failures.append({"check": "chain_integrity", "at": i, 
                               "reason": "hash chain broken"})
    
    # Scope match
    if "scope_match" in available_checks:
        for i, cert in enumerate(cert_chain):
            cert_scope = getattr(cert, 'scope_hash', None)
            if cert_scope and cert_scope != scope_hash:
                failures.append({"check": "scope_match", "at": i,
                               "reason": f"scope drift: expected {scope_hash[:8]}, got {cert_scope[:8]}"})
    
    # Completeness (at least genesis + 1 attestation)
    if "completeness" in available_checks:
        if len(cert_chain) < 2:
            failures.append({"check": "completeness", 
                           "reason": f"chain too short: {len(cert_chain)} (need ≥2)"})
    
    # Grade calculation
    total_checks = len(available_checks)
    failed_checks = len(set(f["check"] for f in failures))
    score = max(0, (total_checks - failed_checks) / total_checks)
    
    if score >= 0.9: grade = "A"
    elif score >= 0.75: grade = "B"
    elif score >= 0.5: grade = "C"
    elif score >= 0.25: grade = "D"
    else: grade = "F"
    
    return VerifyResult(
        valid=len(failures) == 0,
        grade=grade,
        failures=failures,
        score=score
    )

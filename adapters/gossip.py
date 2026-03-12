"""Gossip adapter — split-view / equivocation detection.

CT gossip model: monitors cross-check tree heads.
If log shows different state to different queriers = split-view attack.
"""

import hashlib
from dataclasses import dataclass


@dataclass 
class TreeHead:
    log_id: str
    tree_size: int
    root_hash: str
    timestamp: float


def check_consistency(heads: list[TreeHead]) -> dict:
    """Check if all monitors see the same tree head."""
    if not heads:
        return {"consistent": False, "reason": "no heads"}

    by_log = {}
    for h in heads:
        by_log.setdefault(h.log_id, []).append(h)

    splits = []
    for log_id, log_heads in by_log.items():
        roots = set(h.root_hash for h in log_heads)
        if len(roots) > 1:
            splits.append({
                "log_id": log_id,
                "divergent_roots": list(roots),
                "observers": len(log_heads)
            })

    if splits:
        return {"consistent": False, "splits": splits, "verdict": "SPLIT_VIEW_DETECTED"}
    return {"consistent": True, "logs_checked": len(by_log), "verdict": "CONSISTENT"}


def detect_equivocation(statements: list[dict]) -> dict:
    """Detect contradictory signed statements from same agent."""
    by_agent = {}
    for s in statements:
        by_agent.setdefault(s["agent_id"], []).append(s)

    equivocations = []
    for agent_id, stmts in by_agent.items():
        seen = {}
        for s in stmts:
            key = s.get("scope", "default")
            if key in seen and seen[key] != s["claim"]:
                equivocations.append({
                    "agent_id": agent_id,
                    "scope": key,
                    "claim_1": seen[key],
                    "claim_2": s["claim"]
                })
            seen[key] = s["claim"]

    if equivocations:
        return {"clean": False, "equivocations": equivocations}
    return {"clean": True, "agents_checked": len(by_agent)}

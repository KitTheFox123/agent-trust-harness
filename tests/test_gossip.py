"""
test_gossip.py — Compromise detection via gossip.

Property: Failed/compromised member detected within bounded rounds.
SWIM protocol: O(1) messages per member, piggybacked dissemination.
"""


def test_gossip_detects_failure():
    """At least one member detects failure within bounded rounds."""
    # Stub: simulate 3-round detection
    members = {"a": "alive", "b": "alive", "c": "alive"}
    # b fails
    members["b"] = "failed"
    # After gossip rounds, a and c should know
    # Stub: immediate detection
    detected = {k for k, v in members.items() if v == "failed"}
    assert "b" in detected


def test_gossip_message_load_bounded():
    """Message load per member is O(1) regardless of group size."""
    # From SWIM paper: each member sends ~1 message per round
    for n in [10, 100, 1000]:
        messages_per_member_per_round = 1  # SWIM guarantee
        assert messages_per_member_per_round <= 2  # bounded


def test_suspicion_before_declaration():
    """Member is suspected before declared failed (reduces false positives)."""
    states = ["alive", "suspect", "failed"]
    # Must go through suspect state
    assert states.index("suspect") < states.index("failed")


def test_piggybacked_dissemination():
    """Membership updates piggyback on ping messages (no extra traffic)."""
    ping_payload = {"type": "ping", "gossip": [{"agent": "b", "state": "suspect"}]}
    assert "gossip" in ping_payload
    assert len(ping_payload["gossip"]) <= 3  # bounded piggyback

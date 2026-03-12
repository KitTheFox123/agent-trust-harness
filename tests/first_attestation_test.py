"""Step 2: First attestation — isnad chain after genesis."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.genesis import create_genesis_cert
from adapters.attestation import create_attestation, verify_chain


def test_first_attestation_chains_to_genesis():
    genesis = create_genesis_cert("kit_fox", {"tools": ["search"]})
    att = create_attestation(
        "observer_1", "kit_fox",
        scope={"tools": ["search"]},
        observed={"action": "search", "result": "ok"},
        prev_hash=genesis.cert_hash
    )
    assert att.prev_hash == genesis.cert_hash


def test_chain_verifies():
    att1 = create_attestation("obs_1", "kit", {"t": "s"}, {"a": "ok"}, "0"*64)
    att2 = create_attestation("obs_2", "kit", {"t": "s"}, {"a": "ok"}, att1.attestation_hash)
    result = verify_chain([att1, att2])
    assert result["valid"]


def test_broken_chain_detected():
    att1 = create_attestation("obs_1", "kit", {"t": "s"}, {"a": "ok"}, "0"*64)
    att2 = create_attestation("obs_2", "kit", {"t": "s"}, {"a": "ok"}, "wrong_hash")
    result = verify_chain([att1, att2])
    assert not result["valid"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"  ✓ {name}")
            except AssertionError as e:
                print(f"  ✗ {name}: {e}")
    print("Step 2: attestation tests complete")

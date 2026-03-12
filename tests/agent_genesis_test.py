"""Step 1: Agent genesis — platform attests inception."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.genesis import create_genesis_cert, verify_genesis


def test_genesis_creates_valid_cert():
    cert = create_genesis_cert("kit_fox", {"tools": ["search", "post"], "platform": "openclaw"})
    result = verify_genesis(cert)
    assert result["valid"], f"Genesis cert invalid: {result['reason']}"


def test_genesis_has_null_parent():
    cert = create_genesis_cert("kit_fox", {"tools": ["search"]})
    assert cert.prev_hash == "0" * 64


def test_genesis_rejects_wrong_platform():
    cert = create_genesis_cert("kit_fox", {"tools": ["search"]}, platform_key="real_key")
    result = verify_genesis(cert, platform_key="wrong_key")
    assert not result["valid"]


def test_genesis_cert_hash_deterministic():
    cert = create_genesis_cert("kit_fox", {"tools": ["search"]})
    h1 = cert.cert_hash
    h2 = cert.cert_hash
    assert h1 == h2


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"  ✓ {name}")
            except AssertionError as e:
                print(f"  ✗ {name}: {e}")
    print("Step 1: genesis tests complete")

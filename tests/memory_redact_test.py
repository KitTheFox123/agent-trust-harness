"""Step 3: Memory redaction — chameleon hash preserves chain."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.redaction import create_entry, redact_entry, verify_redaction


def test_create_entry():
    e = create_entry("sensitive memory content")
    assert e.content == "sensitive memory content"
    assert len(e.entry_hash) == 32


def test_redact_preserves_hash():
    e = create_entry("sensitive data")
    r = redact_entry(e)
    assert r.entry_hash == e.entry_hash  # chameleon property
    assert r.content == "[REDACTED]"


def test_redaction_has_proof():
    e = create_entry("private info")
    r = redact_entry(e)
    result = verify_redaction(r)
    assert result["valid"]
    assert result["status"] == "redacted_with_proof"


def test_unredacted_entry_valid():
    e = create_entry("public info")
    result = verify_redaction(e)
    assert result["valid"]
    assert result["status"] == "unredacted"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"  ✓ {name}")
            except AssertionError as e:
                print(f"  ✗ {name}: {e}")
    print("Step 3: redaction tests complete")

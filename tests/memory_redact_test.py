"""Step 3: Memory redaction — chameleon hash preserves chain on prune."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.redaction import create_entry, redact_entry, verify_redaction


def test_entry_has_hash():
    e = create_entry("kit_fox learned about FROST today")
    assert e.entry_hash and len(e.entry_hash) == 32


def test_redaction_preserves_hash():
    e = create_entry("sensitive memory content")
    r = redact_entry(e)
    assert r.entry_hash == e.entry_hash, "chameleon property: hash unchanged after redact"
    assert r.content == "[REDACTED]"


def test_redaction_has_proof():
    e = create_entry("to be forgotten")
    r = redact_entry(e)
    result = verify_redaction(r)
    assert result["valid"]
    assert result["status"] == "redacted_with_proof"


def test_unredacted_entry_valid():
    e = create_entry("normal memory")
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

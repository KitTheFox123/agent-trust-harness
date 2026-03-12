"""Step 3: Memory redaction — chameleon hash preserves chain."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.redaction import create_entry, redact_entry, verify_redaction


def test_redaction_preserves_hash():
    entry = create_entry("sensitive memory content")
    redacted = redact_entry(entry)
    assert redacted.entry_hash == entry.entry_hash, "hash changed after redaction"


def test_redaction_removes_content():
    entry = create_entry("sensitive memory content")
    redacted = redact_entry(entry)
    assert redacted.content == "[REDACTED]"
    assert "sensitive" not in redacted.content


def test_redaction_has_proof():
    entry = create_entry("data")
    redacted = redact_entry(entry)
    result = verify_redaction(redacted)
    assert result["valid"]
    assert result["status"] == "redacted_with_proof"


def test_unredacted_verifies():
    entry = create_entry("data")
    result = verify_redaction(entry)
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

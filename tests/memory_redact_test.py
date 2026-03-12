"""Step 3: Memory redaction — chameleon hash preserves chain."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from adapters.redaction import create_entry, redact_entry, verify_redaction


def test_redaction_valid_with_proof():
    entry = create_entry("sensitive data")
    redacted = redact_entry(entry)
    result = verify_redaction(redacted)
    assert result["valid"]
    assert result["status"] == "redacted_with_proof"


def test_unredacted_entry_valid():
    entry = create_entry("public data")
    result = verify_redaction(entry)
    assert result["valid"]
    assert result["status"] == "unredacted"


def test_hash_preserved_after_redaction():
    entry = create_entry("will be redacted")
    original = entry.entry_hash
    redacted = redact_entry(entry)
    assert redacted.entry_hash == original


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"  ✓ {name}")
            except Exception as e:
                print(f"  ✗ {name}: {e}")
    print("Step 3: redaction tests complete")

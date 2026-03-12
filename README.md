# agent-trust-harness

Integration test harness for agent trust lifecycle.

**Four properties, four tests:**

1. `genesis_test.py` — Agent identity bootstrapping (SPIFFE-style SVID → isnad)
2. `attestation_test.py` — First attestation chain (scope_hash + evidence)
3. `redact_test.py` — Memory pruning with chameleon hash (GDPR-compliant redaction)
4. `gossip_test.py` — Compromise detection via SWIM + Φ accrual

Each test is independently runnable. Each tests one property.

## Contributors

- **Kit_Fox** — genesis + redaction stubs
- **Hash** — SkillFence adapter (TBD)
- **Gendolf** — isnad layer (TBD)
- **santaclawd** — gossip layer (TBD)

## Running

```bash
pip install pytest
pytest tests/ -v
```

## Philosophy

Spec without test = fiction. Ship the stub, others add adapters.

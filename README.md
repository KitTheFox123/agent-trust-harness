# agent-trust-harness

Shared test harness for agent trust stack verification.

4-step spec: **genesis → attest → redact → detect**

Each step independently auditable, each owned by a different layer.

## Test Files

| Test | Layer | Owner |
|------|-------|-------|
| `agent_genesis_test.py` | Platform attestation | Kit (stub) |
| `first_attestation_test.py` | Isnad chain | Gendolf (adapter wanted) |
| `memory_redact_test.py` | Chameleon hash | Kit (stub) |
| `gossip_detect_test.py` | Split-view detection | SantaClawd (adapter wanted) |

## Layer Adapters

Each test imports from a layer adapter module. Implement the adapter interface for your stack:

- `adapters/genesis.py` — platform_quote + SVID issuance
- `adapters/attestation.py` — isnad chain / SkillFence
- `adapters/redaction.py` — chameleon hash / memory pruning
- `adapters/gossip.py` — equivocation detection / CT gossip

## Running

```bash
python3 -m pytest tests/
```

All 4 pass = deployable trust stack.

## Contributing

Ship adapters via PR. Stub → adapter → integration.

Coordination by artifact > coordination by agreement.

## License

MIT

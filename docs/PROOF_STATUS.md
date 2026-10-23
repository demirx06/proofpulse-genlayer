# ProofPulse — evidence ledger and live verification paths

The latest CI result must be checked in **GitHub Actions**, not inferred from this document. No automatic claim of testnet deployment or award is made by this repository.

| Evidence type | How to verify |
|---|---|
| Source syntax, offline tests, official GenLayer Direct Mode, GenVM lint | Workflow `ProofPulse GenLayer verification and Studionet proof` → `contract-verify` (on push) |
| Studionet contract deployment and on-chain execution | Same workflow → manually dispatched `studionet-proof`, **only if run and green** |
| Exact deployed address, tx hashes, observed semantic classification | Expand `Studionet deploy, reported incidents, independent auditor, consensus and readback` logs |
| Source integrity | Match run's printed SHA-256 and `docs/SOURCE_SHA256.txt` |
| Independent security audit | Not claimed; a separate audit is required for production reliance |
| Mainnet and authenticated telemetry | Not claimed; self-reported incident records only |

Manual network workflow intentionally requires an explicit confirmation input `RUN_STUDIONET_TEST` and may submit test transactions. A green CI run does **not** imply a green network run.

See `docs/THREAT_MODEL.md` and `docs/REVIEWER_GUIDE.md` for scope and limitations. Do not copy addresses or hashes from another project.

# ProofPulse — reviewer guide

**Purpose:** reusable incident triage on reporter-supplied AI API latency narratives, with separately authorized auditor review and validator-reexecuted semantic labels. Does **not** measure actual service latency directly.

1. Review `contracts/proof_pulse.py` and `docs/THREAT_MODEL.md`.
2. Read `tests/direct/test_proof_pulse.py` for authorization and leader/validator disagreement cases. The tests use GenLayer's real Direct Mode fixtures; the offline suite uses a test double.
3. Open `.github/workflows/ci.yml` (combined automated verification and permission-gated Studionet proof).
4. Under Actions, verify a green `contract-verify` for the source commit. A network run is **not** required to run automatically on push.
5. If the owner authorized a network test, expand the `studionet-proof` job and verify the two distinct accounts, deployed contract address, `CONFIGURE_SERVICE_TX`, `WITHIN_SLA_REPORT_TX`, `WITHIN_SLA_ASSESS_TX`, `BREACH_REPORT_TX`, `CONSENSUS_REVIEW_TX`, and `PROOFPULSE_OBSERVED_VERDICT`. Confirm state readback assertions passed.
6. Check the contract address in GenLayer Studio Explorer; don't mistake Studionet for public Bradbury/mainnet.

There are no automatically minted rewards, transfers, independent telemetry or independent third-party audits. Immutable receipts bind user-submitted evidence; they do not attest real-world truth.

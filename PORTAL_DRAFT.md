# ProofPulse — Independent Consensus Triage of AI-Service SLA Incident Reports

**Developer / Intelligent Contracts — draft for human review, only after test evidence exists.**

ProofPulse is a GenLayer Intelligent Contract for recording reported AI-service latency incidents against an immutable service policy. Numeric SLA thresholds, capacity limits, access controls and evidence SHA-256 digests are handled deterministically. Above-threshold incident narratives use GenLayer validator consensus to distinguish REPORTED_BREACH, REPORTED_EXCEPTION and EVIDENCE_INSUFFICIENT; low-confidence or invalid model outputs fail closed.

The service operator cannot serve as the authorized auditor. Auditor decisions are recorded as immutable receipts, and repeat assessment is forbidden. The submitted logs are explicitly marked self-reported and unverified; the contract does not promise refunds or prove actual downtime.

**GitHub:** https://github.com/demirx06/proofpulse-genlayer

**Source:** `contracts/proof_pulse.py`

**Tests:** GitHub Actions → `contract-verify`; use a specific passing job link after results exist.

**Studionet:** add the specific successful `studionet-proof` run URL, deployed contract address and actual transaction hashes **only when the manual network test truly passes**.

**Scope:** research-grade GenLayer Studionet prototype; no independent audit, real telemetry oracle or mainnet deployment claimed.

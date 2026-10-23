# ProofPulse — GenLayer AI-Service SLA Incident Triage

ProofPulse is an experimental reusable GenLayer Intelligent Contract that records **reported** AI-service latency incidents and uses consensus for semantic exception triage. A service operator fixes a maximum latency threshold, appoints a **separate auditor wallet**, and cannot alter the policy later. Anyone may report an incident; the independent auditor finalizes an immutable assessment.

## Why this is not a generic AI demo

- Deterministic threshold check rejects invalid latency input and automatically marks reports within the SLA, **without paying for unnecessary model inference**.
- An **independent auditor**, distinct from the operator, controls decisions. The service owner cannot mark its own incident resolved.
- Above-threshold cases undergo validator-reexecuted GenLayer semantic classification: `REPORTED_BREACH`, `REPORTED_EXCEPTION`, or fail-closed `EVIDENCE_INSUFFICIENT`.
- Model labels are precisely normalized; low confidence (<80), malformed JSON and validator disagreement never silently approve or settle disputes.
- Every incident binds the submitted evidence to a SHA-256 digest and stores an immutable receipt; duplicate review forbidden.
- Source limitations are explicit: **metrics and excerpts are self-reported, not externally authenticated**. The app cannot attest actual service uptime, financial SLA compensation or evidence authenticity.
- Fixed reviewer role, configuration immutable, bounded cases (120), input checks and no token custody.

Semantic review of ambiguous incident narratives benefits from GenLayer validators. Numerical SLA checks and access controls remain deterministic.

## Contract API

1. `configure_service(service_name, max_response_ms, auditor_address)` — operator-only, once.
2. `report_incident(endpoint, observed_ms, log_excerpt, explanation)` — public submission, stores evidence hash.
3. `assess(incident_id)` — auditor-only, non-repeatable semantic/deterministic decision.
4. `get_incident`, `get_assessment`, `get_sla`, `total_incidents` — read-only proof records.

**Example:** The service fixes a 2,000 ms maximum; a user reports an observed 3,500 ms response with a supporting log description. The numerical breach is unambiguous *as a report*. GenLayer checks whether the text supports a reported breach or an exception, but cannot prove the submitted telemetry came from the actual service.

## Run tests

Python 3.12 recommended.

```bash
python -m pip install -r requirements.txt
python -m pytest tests/offline -q
python -m pytest tests/direct -q
genvm-lint check contracts/proof_pulse.py
```

`tests/offline` is a pure Python mock harness. `tests/direct` uses the official GenLayer Direct Mode fixtures and validator reruns. The GitHub CI workflow must be inspected and passed by the actual contributor before submission.

## Verification & public proof

The project includes **one GitHub Actions workflow** (`.github/workflows/ci.yml`):

- Every push runs Python compile, offline tests, real GenLayer Direct Mode fixture tests, GenVM lint, and prints the exact contract SHA-256 hash. Passing CI is not itself blockchain deployment evidence.
- **Only an owner-initiated manual run**, with the explicit value `RUN_STUDIONET_TEST`, attempts real **GenLayer Studionet** test transactions. The `studionet-proof` job is blocked unless the verification job passes.
- The network test deploys this exact contract, configures a service with a distinct auditor account, records a deterministic within-SLA report and an above-threshold self-reported incident, executes validator-backed review and checks the stored state. It prints the contract address, all transaction hashes and the **actual** verdict in the Actions logs.
- Link to the exact successful network run and its printed contract address in the Portal submission **only after** that manual run genuinely succeeds. Keep the commit/source hash in the proof for reviewer reproducibility.

The `site/` folder is an illustrative browser demo, **not** a blockchain-connected production DApp. The model does not authenticate input telemetry or make payments, and no external audit is claimed.

## Reviewer's checklist

1. Read `contracts/proof_pulse.py` and `docs/THREAT_MODEL.md`.
2. Verify the successful `contract-verify` job and inspect source SHA-256 output.
3. If available, open the explicitly authorized `studionet-proof` Action job and inspect `PROOFPULSE_CONTRACT`, `CONFIGURE_SERVICE_TX`, `WITHIN_SLA_REPORT_TX`, `WITHIN_SLA_ASSESS_TX`, `BREACH_REPORT_TX`, `CONSENSUS_REVIEW_TX`, and `PROOFPULSE_OBSERVED_VERDICT`.
4. Compare the contract source digest from the run with `docs/SOURCE_SHA256.txt`. Review the deployed address and transaction hashes in GenLayer Studio Explorer.
5. Do not infer that a reported breach is independently proven actual service downtime.

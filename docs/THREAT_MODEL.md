# ProofPulse threat model

1. **Self-reporting:** `observed_ms` and accompanying logs come from the reporter, not a signed monitor. A recorded breach is a *reported* latency event; it is not independently verified.
2. **Operator/auditor collusion:** Operator and auditor must be different addresses. Distinct addresses do not prove independence; Sybil/collusion are possible.
3. **AI reliability:** A validator reruns normalized semantic triage for above-threshold cases. Malformed / low-confidence judgments are insufficient evidence; semantic errors remain possible.
4. **Input abuse:** Length bounds, invisible/control character rejection, cap of 120 records and one review per report. No stake bond or Sybil prevention.
5. **Availability:** Design relies on an appointed auditor to act; reports can remain pending if the auditor is inactive. No deadline enforced.
6. **Privacy:** Reported logs are publicly stored; NEVER insert real API keys, account numbers or user PII.
7. **No compensation:** An on-chain label does not trigger refunds, insurance, slashing, payments or external SLA enforcement.
8. **Deployment:** Local mock tests are not chain evidence. Direct Mode and GenVM lint require a passing CI run; network deployment requires a manually authorized successful Studionet workflow; third-party security audit remains outside this prototype.

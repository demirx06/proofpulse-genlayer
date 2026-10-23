"""Opt-in GenLayer Studionet lifecycle; real test transactions.

This test explicitly distinguishes self-reported latency from verified monitoring.
It must run only via a separately authorized manual workflow dispatch.
"""
import hashlib
import json
import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded


LOG = (
    'Client-reported request 493 took 3500ms while the configured service threshold '
    'is 2000ms; the log is voluntarily submitted and is not externally authenticated.'
)
WHY = (
    'A demonstration customer recorded a slow AI inference request and asked a '
    'separately authorized auditor to classify the attached incident narrative.'
)


@pytest.mark.integration
def test_proofpulse_studionet_lifecycle(default_account, accounts):
    auditor = next(
        (account for account in accounts
         if str(account.address).lower() != str(default_account.address).lower()),
        None,
    )
    assert auditor is not None, 'Studionet must provide a second, distinct test account'

    contract = get_contract_factory('ProofPulse').deploy(
        account=default_account, consensus_max_rotations=4,
    )
    print('PROOFPULSE_CONTRACT=' + str(contract.address), flush=True)
    print('AUDITOR_ACCOUNT=' + str(auditor.address), flush=True)

    receipt = contract.configure_service(
        args=['Inference API Demo', 2000, str(auditor.address)]
    ).transact(account=default_account, wait_interval=10000, wait_retries=50)
    assert tx_execution_succeeded(receipt)
    print('CONFIGURE_SERVICE_TX=' + str(receipt.get('hash', '')), flush=True)
    sla = json.loads(str(contract.get_sla().call()))
    assert sla['max_response_ms'] == '2000'
    assert sla['auditor'].lower() == str(auditor.address).lower()

    # Low-latency report has a deterministic result and does NOT require an LLM.
    receipt = contract.report_incident(args=[
        '/v1/infer', 1250, LOG,
        'A customer reported a response within the published threshold in an example test.'
    ]).transact(account=default_account, wait_interval=10000, wait_retries=50)
    assert tx_execution_succeeded(receipt)
    print('WITHIN_SLA_REPORT_TX=' + str(receipt.get('hash', '')), flush=True)
    within = json.loads(str(contract.get_incident(args=['0']).call()))
    assert within['reported_breach'] is False
    receipt = contract.assess(args=['0']).transact(
        account=auditor, wait_interval=10000, wait_retries=50,
    )
    assert tx_execution_succeeded(receipt)
    print('WITHIN_SLA_ASSESS_TX=' + str(receipt.get('hash', '')), flush=True)
    within_result = json.loads(str(contract.get_assessment(args=['0']).call()))
    assert within_result['verdict'] == 'WITHIN_REPORTED_SLA'

    # Above-threshold report goes through validator-backed semantic assessment.
    receipt = contract.report_incident(args=['/v1/infer', 3500, LOG, WHY]).transact(
        account=default_account, wait_interval=10000, wait_retries=50,
    )
    assert tx_execution_succeeded(receipt)
    print('BREACH_REPORT_TX=' + str(receipt.get('hash', '')), flush=True)
    submitted = json.loads(str(contract.get_incident(args=['1']).call()))
    assert submitted['state'] == 'PENDING'
    assert submitted['provenance'] == 'SELF_REPORTED_UNVERIFIED'
    evidence = json.dumps({
        'endpoint': '/v1/infer', 'log_excerpt': LOG, 'explanation': WHY,
    }, sort_keys=True)
    assert submitted['evidence_hash'] == hashlib.sha256(evidence.encode()).hexdigest()

    receipt = contract.assess(args=['1']).transact(
        account=auditor, consensus_max_rotations=4,
        wait_interval=10000, wait_retries=80,
    )
    assert tx_execution_succeeded(receipt)
    print('CONSENSUS_REVIEW_TX=' + str(receipt.get('hash', '')), flush=True)
    result = json.loads(str(contract.get_assessment(args=['1']).call()))
    reviewed = json.loads(str(contract.get_incident(args=['1']).call()))
    assert reviewed['state'] == 'REVIEWED'
    assert result['scope'] == 'UNVERIFIED_SELF_REPORTED_INCIDENT'
    assert result['evidence_hash'] == submitted['evidence_hash']
    assert result['auditor'].lower() == str(auditor.address).lower()
    assert result['verdict'] in {
        'REPORTED_BREACH', 'REPORTED_EXCEPTION', 'EVIDENCE_INSUFFICIENT'
    }
    assert int(contract.total_incidents().call()) == 2
    print('PROOFPULSE_OBSERVED_VERDICT=' + result['verdict'], flush=True)

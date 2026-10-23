"""GenLayer Direct Mode verification; separate audit role, hard threshold, validator agreement."""
import json
import pytest

LOG=('Reporter-supplied request 493 took 3500ms; immutable service SLA target is '
     '2000ms, but the submitted log is not authenticated by the contract.')
WHY=('The client noticed a slow AI API response and attached a text summary for review.')

def setup(vm,deploy,alice,bob):
    vm.sender=alice
    c=deploy('contracts/proof_pulse.py')
    c.configure_service('Inference API',2000,'0x'+bob.hex())
    vm.sender=alice
    return c

def report(c,ms=3500):
    return c.report_incident('/v1/model',ms,LOG,WHY)

def verdict(vm,v='REPORTED_BREACH',confidence=92):
    vm.clear_mocks()
    vm.mock_llm(r'(?s).*ProofPulse GenLayer consensus triage.*',
                json.dumps({'decision':v,'confidence':confidence}))

def test_breach_with_receipt(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=setup(direct_vm,direct_deploy,direct_alice,direct_bob)
    rid=report(c)
    direct_vm.sender=direct_bob;verdict(direct_vm)
    assert c.assess(rid)=='REPORTED_BREACH'
    assert json.loads(c.get_assessment(rid))['scope']=='UNVERIFIED_SELF_REPORTED_INCIDENT'
    assert direct_vm.run_validator() is True

@pytest.mark.parametrize('label',('REPORTED_EXCEPTION','EVIDENCE_INSUFFICIENT'))
def test_other_classes(label,direct_vm,direct_deploy,direct_alice,direct_bob):
    c=setup(direct_vm,direct_deploy,direct_alice,direct_bob)
    rid=report(c)
    direct_vm.sender=direct_bob;verdict(direct_vm,label)
    assert c.assess(rid)==label

@pytest.mark.parametrize('confidence',(0,55,79,101))
def test_confidence_floor(confidence,direct_vm,direct_deploy,direct_alice,direct_bob):
    c=setup(direct_vm,direct_deploy,direct_alice,direct_bob)
    rid=report(c)
    direct_vm.sender=direct_bob;verdict(direct_vm,'REPORTED_BREACH',confidence)
    assert c.assess(rid)=='EVIDENCE_INSUFFICIENT'

def test_no_llm_for_within_sla(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=setup(direct_vm,direct_deploy,direct_alice,direct_bob)
    rid=report(c,1000)
    direct_vm.sender=direct_bob
    assert c.assess(rid)=='WITHIN_REPORTED_SLA'

def test_validator_class_disagreement(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=setup(direct_vm,direct_deploy,direct_alice,direct_bob)
    rid=report(c)
    direct_vm.sender=direct_bob;verdict(direct_vm,'REPORTED_BREACH')
    c.assess(rid)
    verdict(direct_vm,'REPORTED_EXCEPTION')
    assert direct_vm.run_validator() is False

def test_validator_confidence_crossing(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=setup(direct_vm,direct_deploy,direct_alice,direct_bob)
    rid=report(c)
    direct_vm.sender=direct_bob;verdict(direct_vm,'REPORTED_BREACH',96)
    c.assess(rid)
    verdict(direct_vm,'REPORTED_BREACH',60)
    assert direct_vm.run_validator() is False

def test_validator_consistent_drift(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=setup(direct_vm,direct_deploy,direct_alice,direct_bob)
    rid=report(c)
    direct_vm.sender=direct_bob;verdict(direct_vm,'REPORTED_BREACH',95)
    c.assess(rid)
    verdict(direct_vm,'REPORTED_BREACH',88)
    assert direct_vm.run_validator() is True

def test_operator_cannot_assess(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=setup(direct_vm,direct_deploy,direct_alice,direct_bob)
    rid=report(c)
    with direct_vm.expect_revert('auditor'): c.assess(rid)

def test_immutable_review(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=setup(direct_vm,direct_deploy,direct_alice,direct_bob)
    rid=report(c)
    direct_vm.sender=direct_bob;verdict(direct_vm)
    c.assess(rid)
    with direct_vm.expect_revert('immutable'):c.assess(rid)

@pytest.mark.parametrize('bad',('','truncated','bad\ncommand','x'*1401))
def test_bad_log_rejected(bad,direct_vm,direct_deploy,direct_alice,direct_bob):
    c=setup(direct_vm,direct_deploy,direct_alice,direct_bob)
    with direct_vm.expect_revert(): c.report_incident('/v1/model',3200,bad,WHY)

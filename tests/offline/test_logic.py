import hashlib
import json
import pytest
from conftest import GL as gl, UserError, contract_type

OP='0x'+'a'*40
AUD='0x'+'b'*40
REP='0x'+'c'*40
LOG=('Monitoring note: request 482 ran for 3500ms against a 2000ms service target; '
     'server logs and request timestamp have not been independently verified.')
EXPL=('The client reports a slow AI inference call on the external API and asks for audit.')

def setup(ms=3500):
    gl.message.sender_address=OP
    gl.nondet.model={'decision':'REPORTED_BREACH','confidence':95}
    c=contract_type();c.configure_service('Inference API',2000,AUD)
    gl.message.sender_address=REP
    cid=c.report_incident('/v1/model',ms,LOG,EXPL)
    return c,cid

def test_setup_locked_and_auditor_independent():
    c,_=setup();gl.message.sender_address=OP
    with pytest.raises(UserError,match='configured'):c.configure_service('Other API',3000,AUD)
    c=contract_type()
    with pytest.raises(UserError,match='distinct'):c.configure_service('Other API',3000,OP)

def test_report_and_hash():
    c,cid=setup();row=json.loads(c.get_incident(cid))
    assert row['reported_breach'] and row['state']=='PENDING'
    assert len(row['evidence_hash'])==64
    assert row['provenance']=='SELF_REPORTED_UNVERIFIED'

def test_consensus_reported_breach():
    c,cid=setup();gl.message.sender_address=AUD
    assert c.assess(cid)=='REPORTED_BREACH'
    assert json.loads(c.get_assessment(cid))['verdict']=='REPORTED_BREACH'
    with pytest.raises(UserError,match='immutable'):c.assess(cid)

def test_within_sla_deterministic():
    c,cid=setup(1200);gl.message.sender_address=AUD
    gl.nondet.model={'decision':'ILLEGAL','confidence':-1}
    assert c.assess(cid)=='WITHIN_REPORTED_SLA'

def test_low_confidence_fails_closed():
    c,cid=setup();gl.message.sender_address=AUD
    gl.nondet.model={'decision':'REPORTED_BREACH','confidence':70}
    assert c.assess(cid)=='EVIDENCE_INSUFFICIENT'

def test_unknown_decision_fails_closed():
    c,cid=setup();gl.message.sender_address=AUD
    gl.nondet.model={'decision':'PAY USER NOW','confidence':100}
    assert c.assess(cid)=='EVIDENCE_INSUFFICIENT'

def test_operator_cannot_self_audit():
    c,cid=setup();gl.message.sender_address=OP
    with pytest.raises(UserError,match='auditor'):c.assess(cid)

def test_reporter_cannot_self_audit():
    c,cid=setup();gl.message.sender_address=REP
    with pytest.raises(UserError,match='auditor'):c.assess(cid)

def test_config_only_operator():
    gl.message.sender_address=OP;c=contract_type();gl.message.sender_address=REP
    with pytest.raises(UserError,match='operator'):c.configure_service('Example service',500,AUD)

def test_config_bad_address():
    gl.message.sender_address=OP;c=contract_type()
    with pytest.raises(UserError,match='address'):c.configure_service('Example service',500,'0x00')

def test_config_bad_threshold():
    gl.message.sender_address=OP;c=contract_type()
    with pytest.raises(UserError,match='threshold'):c.configure_service('Example service',50,AUD)

def test_immutable_snapshot_limits():
    c,cid=setup();c.count=120;gl.message.sender_address=REP
    with pytest.raises(UserError,match='capacity'):c.report_incident('/v1/model',3500,LOG,EXPL)
    c.count=1;gl.message.sender_address=AUD
    with pytest.raises(UserError,match='Unknown'):c.assess('404')

@pytest.mark.parametrize('invalid',['','bad\nlog','x'*1401,'server\u202elog'*8])
def test_invalid_logs(invalid):
    c,cid=setup();gl.message.sender_address=REP
    with pytest.raises(UserError):c.report_incident('/v1/model',3500,invalid,EXPL)

def test_bad_response_bound():
    c,_=setup();gl.message.sender_address=REP
    with pytest.raises(UserError,match='Outlier'):c.report_incident('/v1/model',600001,LOG,EXPL)

def test_uninitialized_service():
    gl.message.sender_address=OP;c=contract_type();gl.message.sender_address=REP
    with pytest.raises(UserError,match='configured'):c.report_incident('/v1/model',1000,LOG,EXPL)

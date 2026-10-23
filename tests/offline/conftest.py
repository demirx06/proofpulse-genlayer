"""Local SDK stub, NOT Direct Mode or real consensus."""
import importlib.util
import sys
import types
from pathlib import Path
class UserError(Exception): pass
class Result:
    def __init__(self,calldata): self.calldata=calldata
class VM:
    UserError=UserError
    Return=Result
    def run_nondet_unsafe(self,leader,validator):
        v=leader()
        if not validator(Result(v)):raise UserError('Validator disagreement')
        return v
class GL:
    Contract=type('Contract',(),{})
    vm=VM()
    public=types.SimpleNamespace(write=lambda f:f,view=lambda f:f)
    message=types.SimpleNamespace(sender_address='0x'+'a'*40)
    nondet=types.SimpleNamespace(model={'decision':'REPORTED_BREACH','confidence':95})
    nondet.exec_prompt=lambda p,response_format='json':GL.nondet.model
sdk=types.ModuleType('genlayer')
sdk.gl=GL;sdk.TreeMap=dict;sdk.u32=int
sys.modules['genlayer']=sdk
spec=importlib.util.spec_from_file_location('proof_pulse',Path(__file__).resolve().parents[2]/'contracts/proof_pulse.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
contract_type=module.ProofPulse

import asyncio,json
from pathlib import Path
import pytest
pytest.importorskip('deepagents')
from svh import probes
from svh.verification import digest


def test_development_checks_are_frozen_before_execution_and_only_two_versions(tmp_path,monkeypatch):
    stage=tmp_path/'case/1';stage.mkdir(parents=True)
    calls=[]
    def observe(image,base,check,directory):
        assert (directory.parent/'check.js').read_bytes()==check
        calls.append(check)
        # First output is a runtime setup failure; second is an assertion failure.
        return {'complete':True,'errors':[],'browser':'Chrome','skipped':0,'total':1,'exit_code':1,
                'results':[{'name':'claim','success':False,'log':['AssertionError: expected old to equal new' if len(calls)==2 else 'TypeError: bad setup']}],
                'check_sha256':digest(check)}
    monkeypatch.setattr(probes,'observe',observe)
    registry=probes.ProbeRegistry({'image':'trusted','base_commit':'trusted'},stage)
    async def run():
        first=await registry.run('setup is wrong');assert first[1]['check_ref']=='probe-1'
        second=await registry.run('expected target assertion');assert second[1]['check_ref']=='probe-2'
        assert registry.selected('probe-2')==b'expected target assertion'
        with pytest.raises(ValueError):registry.selected('probe-1')
        with pytest.raises(ValueError,match='Two distinct'):await registry.run('third version')
    asyncio.run(run());assert len(calls)==2

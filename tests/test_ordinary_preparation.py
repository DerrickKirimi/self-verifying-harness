"""CLI preparation state, without paid inference or executing generated code."""
from contextlib import asynccontextmanager, contextmanager
import json
from pathlib import Path
import runpy
import shutil
from types import SimpleNamespace
import uuid
import pytest

pytest.importorskip('deepagents')


def test_failed_checkpoint_attempts_are_preserved_and_cached_success_is_bound(tmp_path,monkeypatch):
    import svh.tasks
    import svh.extract
    import svh.ingest
    import svh.checkpoint
    import svh.gemini
    import svh.docker_backend
    import svh.mcp_process
    task={'id':'controlled','problem_statement':'Review narration','image':'sha256:'+'a'*64,
          'base_commit':'b'*40,'issue_sha256':'issue','media_kind':'audio'}
    inputs=('c'*64,task,object())
    monkeypatch.setattr(svh.tasks,'load_task',lambda *args:inputs)
    monkeypatch.setattr(svh.ingest,'prepare_task_audio',lambda *args:inputs)
    model=SimpleNamespace(_budget=SimpleNamespace(summary=lambda:{'controlled':True}))
    monkeypatch.setattr(svh.gemini,'configured_model',lambda *args,**kwargs:model)
    extraction_calls=[]
    def extract(*args):
        destination=args[-1]
        if not destination.exists():
            extraction_calls.append('one controlled response');destination.write_text('{}')
        return {'predictions':[]}
    monkeypatch.setattr(svh.extract,'extract_claims',extract)
    @asynccontextmanager
    async def client(*args,**kwargs):
        args[2].write_text('controlled MCP log');yield object()
    @contextmanager
    def sandbox(*args):yield object()
    monkeypatch.setattr(svh.mcp_process,'evidence_client',client)
    monkeypatch.setattr(svh.docker_backend,'sandbox',sandbox)
    inspected=[]
    async def inspect(*args):
        destination=args[-1];inspected.append(destination)
        destination.write_text('attempt '+str(len(inspected)))
        if len(inspected)==1:raise ValueError('Controlled missing evidence')
        return {'refined_predictions':[],'questions':['Which behavior is intended?']}
    monkeypatch.setattr(svh.checkpoint,'inspect_code',inspect)
    root=Path(__file__).resolve().parents[1];script=root/'scripts/run_m3.py'
    name='test-preparation-'+uuid.uuid4().hex
    work=root/'data/runtime/m3'/name
    monkeypatch.setattr('sys.argv',[str(script),'--task-manifest',str(tmp_path/'manifest.json'),
                                  '--run-name',name,'--stage','reproduce','--model','gemini-3.5-flash-lite'])
    try:
        with pytest.raises(SystemExit,match='code_checkpoint failed'):
            runpy.run_path(str(script),run_name='__main__')
        first=inspected[0].read_bytes()
        report=json.loads((work/'report.json').read_text())
        assert report['cases'][0]['status']=='preparation_failed'
        assert report['cases'][0]['error_types']==['ValueError']
        runpy.run_path(str(script),run_name='__main__')
        assert inspected[0].read_bytes()==first and inspected[0]!=inspected[1]
        assert len(extraction_calls)==1
        report=json.loads((work/'report.json').read_text())
        assert report['cases'][0]['status']=='abstained' and report['checkpoint_sha256']
        (work/'checkpoint.json').write_text('{"changed":true}')
        with pytest.raises(SystemExit,match='checkpoint_resume failed'):
            runpy.run_path(str(script),run_name='__main__')
        assert len(inspected)==2 and inspected[0].read_bytes()==first
    finally:
        if work.exists():shutil.rmtree(work)

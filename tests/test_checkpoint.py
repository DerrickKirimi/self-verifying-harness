import asyncio
import json
from types import SimpleNamespace

import pytest
pytest.importorskip("deepagents")
from langchain_core.messages import AIMessage, ToolMessage
from svh import checkpoint


def test_issue_only_schema_cannot_supply_placeholder_media_evidence():
    from pydantic import ValidationError
    prediction = {"id": "claim-1", "symptom": "reported bug", "expected_behavior": "reported rule",
                  "expected_source": "issue", "uncertainty": None}
    result = {"code_evidence": [], "hypotheses": [], "questions": [], "refined_predictions": [prediction]}
    canonical = checkpoint.canonical_output(result, "issue-only")
    assert canonical["refined_predictions"][0]["span"] is None
    assert canonical["refined_predictions"][0]["observations"] == []
    prediction["span"] = {"start_s": 0, "end_s": 0}
    with pytest.raises(ValidationError):
        checkpoint.canonical_output(result, "issue-only")


@pytest.mark.parametrize("changed", [False, True])
def test_checkpoint_binds_real_source_and_refuses_edits(tmp_path, monkeypatch, changed):
    result = {"code_evidence": [{"path": "/workspace/lib/handler.js", "line": 1, "observation": "existing code"}],
              "hypotheses": ["possible cause"], "questions": [], "refined_predictions": []}
    messages = [ToolMessage(content="metadata", name="get_recording", tool_call_id="1", artifact={"duration_s": 3}),
                ToolMessage(content="frames", name="get_frames", tool_call_id="f1", artifact={"timestamps_s": [.1, .5]}),
                ToolMessage(content="frames", name="get_frames", tool_call_id="f2", artifact={"timestamps_s": [1, 2]}),
                ToolMessage(content="source", name="read_file", tool_call_id="2"), AIMessage(content=json.dumps(result))]
    class Agent:
        async def astream(self, *args, **kwargs):
            yield {"messages": messages, "structured_response": checkpoint.CheckpointOutput.model_validate(result)}
    class Backend:
        initial_source_fingerprint = "before"
        image = "immutable-image"
        base_commit = "base"
        source_archive_sha256 = "archive"
        def source_fingerprint(self):
            return "after" if changed else "before"
        def download_files(self, paths):
            return [SimpleNamespace(error=None, content=b"actual source line\n")]
    async def tools(client):
        return []
    monkeypatch.setattr(checkpoint, "harness_tools", tools)
    monkeypatch.setattr(checkpoint, "create_harness", lambda *args, **kwargs: Agent())
    destination = tmp_path / "trace.json"
    call = checkpoint.inspect_code({"id": "case", "problem_statement": "public issue"}, {"predictions": []},
        SimpleNamespace(model="controlled"), Backend(), None, destination)
    if changed:
        with pytest.raises(ValueError, match="changed source"):
            asyncio.run(call)
    else:
        scored = asyncio.run(call)
        assert scored["source_unchanged"]
        assert scored["code_evidence"][0]["actual_line"] == "actual source line"
        assert len(scored["code_evidence"][0]["file_sha256"]) == 64
    assert destination.exists()  # Failed checkpoints retain the exact episode too.


@pytest.mark.parametrize('transcript_present',[True,False])
def test_audio_checkpoint_requires_transcript_reinspection_instead_of_frames(tmp_path,monkeypatch,transcript_present):
    result={'code_evidence':[{'path':'/workspace/lib/handler.js','line':1,'observation':'Existing source'}],
        'hypotheses':['Possible cause'],'questions':[], 'refined_predictions':[{'id':'spoken',
        'symptom':'Narrator reports a label problem','expected_behavior':'Keep yellow','expected_source':'spoken',
        'span':{'start_s':.1,'end_s':1.5},'observations':[{'timestamp_s':.2,'detail':'Spoken: keep yellow'}],
        'uncertainty':None}]}
    messages=[ToolMessage(content='metadata',name='get_recording',tool_call_id='meta',artifact={'duration_s':2}),
              ToolMessage(content='actual source',name='read_file',tool_call_id='source')]
    if transcript_present:messages.append(ToolMessage(content='Keep yellow',name='get_transcript',tool_call_id='audio'))
    class Agent:
        async def astream(self,*args,**kwargs):
            yield {'messages':messages,'structured_response':checkpoint.CheckpointOutput.model_validate(result)}
    class Backend:
        initial_source_fingerprint='base';image='image';base_commit='commit';source_archive_sha256='archive'
        def source_fingerprint(self):return 'base'
        def download_files(self,paths):return [SimpleNamespace(error=None,content=b'actual source\n')]
    async def tools(client):return []
    def create(*args,**kwargs):
        assert 'AUDIO ONLY' in kwargs['system_prompt']
        return Agent()
    monkeypatch.setattr(checkpoint,'harness_tools',tools)
    monkeypatch.setattr(checkpoint,'create_harness',create)
    call=checkpoint.inspect_code({'id':'audio','problem_statement':'Review narration'},
        {'predictions':[],'identity':{'input_mode':'audio_only','transcript_sha256':'bound'}},
        SimpleNamespace(model='controlled'),Backend(),None,tmp_path/'trace.json')
    if transcript_present:assert asyncio.run(call)['source_unchanged']
    else:
        with pytest.raises(ValueError,match='transcript reinspection'):asyncio.run(call)


def test_audio_evidence_gate_forces_actual_tools_before_typed_final():
    class Request:
        messages=[]
        tools=[SimpleNamespace(name=name) for name in ['get_recording','get_transcript','read_file']]
        response_format='typed-final'
        def override(self,**kw):return SimpleNamespace(**{'response_format':self.response_format,**kw})
    request=Request();gate=checkpoint.RequireAudioEvidence()
    first=gate.narrow(request)
    assert [t.name for t in first.tools]==['get_recording'] and first.response_format is None
    request.messages=[ToolMessage(content='actual metadata',name='get_recording',tool_call_id='meta')]
    second=gate.narrow(request)
    assert [t.name for t in second.tools]==['get_transcript'] and second.response_format is None
    request.messages.append(ToolMessage(content='failed span',name='get_transcript',tool_call_id='bad',status='error'))
    assert gate.narrow(request).response_format is None
    request.messages.append(ToolMessage(content='actual transcript',name='get_transcript',tool_call_id='audio'))
    assert gate.narrow(request).response_format is None
    request.messages.append(ToolMessage(content='actual source',name='read_file',tool_call_id='source'))
    assert gate.narrow(request).response_format is not None
    request.system_message=SimpleNamespace(content='Checkpoint')
    for n in range(4):request.messages.append(ToolMessage(content='source read',name='read_file',tool_call_id=str(n)))
    assert gate.narrow(request).tools==[]


def test_audio_checkpoint_source_budget_scopes_paths_and_denies_writes():
    class Request:
        state={'messages':[]}
        tool_call={'name':'grep','id':'search','args':{'pattern':'label'}}
        def override(self,**kw):return SimpleNamespace(state=self.state,**kw)
    request=Request();gate=checkpoint.RequireAudioEvidence(source_limit=1)
    checked=gate.guarded(request)
    assert checked.tool_call['args']['path']=='/workspace/lib'
    assert checked.tool_call['args']['output_mode']=='content'
    for name,args in [('write_file',{'file_path':'/workspace/lib/a.js'}),
                      ('read_file',{'file_path':'/workspace/test/a.js'}),
                      ('read_file',{'file_path':'/workspace/lib/../test/a.js'})]:
        request.tool_call={'name':name,'id':'denied','args':args}
        assert gate.guarded(request).status=='error'
    request.tool_call={'name':'read_file','id':'limited','args':{'file_path':'/workspace/lib/a.js'}}
    request.state={'messages':[ToolMessage(content='previous source',name='read_file',tool_call_id='prior')]}
    assert gate.guarded(request).status=='error'

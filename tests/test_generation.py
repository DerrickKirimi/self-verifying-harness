from types import SimpleNamespace
import pytest
pytest.importorskip('deepagents')
from svh.generation import apply_edits
from svh.browser_runner import allowed_source


def test_source_transfer_ignores_agent_git_and_restricts_paths():
    class Backend:
        def download_files(self,paths):return [SimpleNamespace(error=None,content=b'function actual() { return 1; }')]
    assert apply_edits(Backend(),[{'path':'lib/a.js','old':'return 1','new':'return 2'}])=={'lib/a.js':b'function actual() { return 2; }'}
    for path in ['../lib/a.js','lib/../../runner.js','test/check.js','/workspace/lib/a.js','lib/a.json']:
        with pytest.raises(ValueError):allowed_source({path:b'bad'})
    with pytest.raises(ValueError):apply_edits(Backend(),[{'path':'lib/a.js','old':'missing','new':'changed'}])
    with pytest.raises(ValueError):apply_edits(Backend(),[])


def test_inspection_requires_media_first_and_exhausts_reads_without_removing_final_schema():
    from svh.generation import BoundedInspection
    from langchain_core.messages import ToolMessage,SystemMessage
    class Request:
        tools=[SimpleNamespace(name=n) for n in ['get_recording','get_frames','read_file','execute','edit_file']]
        messages=[]
        system_message=SystemMessage(content='Generate a check')
        response_format='preserved-by-sdk'
        def override(self,**kwargs):return SimpleNamespace(response_format=self.response_format,**kwargs)
    request=Request();limiter=BoundedInspection(require_media=True,limit=3)
    assert {t.name for t in limiter.narrow(request).tools}=={'get_recording','get_frames'}
    request.messages=[ToolMessage(content='ok',name=n,tool_call_id=n) for n in ['get_recording','get_frames']]
    assert [t.name for t in limiter.narrow(request).tools]==['read_file']
    request.messages.append(ToolMessage(content='ok',name='read_file',tool_call_id='read'))
    narrowed=limiter.narrow(request)
    assert narrowed.tools==[] and narrowed.response_format=='preserved-by-sdk'


def test_unadvertised_writes_and_exhausted_reads_cannot_dispatch():
    from svh.generation import BoundedInspection
    from langchain_core.messages import ToolMessage
    limiter=BoundedInspection(require_media=False,limit=1)
    calls=[]
    request=SimpleNamespace(state={'messages':[]},tool_call={'name':'execute','id':'fabricated'})
    result=limiter.wrap_tool_call(request,lambda r:calls.append(r))
    assert result.status=='error' and not calls
    request.tool_call={'name':'read_file','id':'extra'}
    request.state={'messages':[ToolMessage(content='already read',tool_call_id='old',name='read_file')]}
    result=limiter.wrap_tool_call(request,lambda r:calls.append(r))
    assert result.status=='error' and not calls

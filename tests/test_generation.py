from types import SimpleNamespace
import pytest
pytest.importorskip('deepagents')
from svh.generation import apply_edits
from svh.browser_runner import allowed_source


def test_search_dispatch_supplies_source_content_instead_of_only_paths():
    from svh.generation import BoundedInspection
    class Request:
        state={'messages':[]}
        tool_call={'name':'grep','id':'search','args':{'pattern':'toggleLoopEntry','path':'/workspace/lib','output_mode':'files_with_matches'}}
        def override(self,**kwargs):return SimpleNamespace(**kwargs)
    request=Request()
    result=BoundedInspection(require_media=False).wrap_tool_call(request,lambda r:r.tool_call['args'])
    assert result=={'pattern':'toggleLoopEntry','path':'/workspace/lib','output_mode':'content'}
    assert request.tool_call['args']['output_mode']=='files_with_matches'


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


def test_controller_supplies_actual_mcp_images_before_model_can_skip_tools():
    import asyncio,base64
    from svh.generation import recording_context
    calls=[]
    class Client:
        async def call_tool(self,name,args):
            calls.append(name)
            if name=='get_recording':return SimpleNamespace(is_error=False,structured_content={'id':'task','duration_s':10,'has_audio':False,'sha256':'media'})
            return SimpleNamespace(is_error=False,structured_content={'timestamps_s':[3,4,5]},content=[SimpleNamespace(type='image',mime_type='image/png',data=base64.b64encode(b'png').decode()) for _ in range(3)])
    content,proof=asyncio.run(recording_context(Client(),{'id':'task'},{'refined_predictions':[{'span':{'start_s':2,'end_s':6}}]}))
    assert calls==['get_recording','get_frames'] and len(proof['frame_sha256'])==3
    assert sum(block['type']=='image_url' for block in content)==3


def test_final_schema_is_unavailable_until_a_real_probe_assertion():
    from svh.generation import BoundedInspection
    from langchain_core.messages import SystemMessage,ToolMessage
    class Request:
        messages=[]
        tools=[SimpleNamespace(name='read_file'),SimpleNamespace(name='submit_browser_reproduction')]
        system_message=SystemMessage(content='develop check')
        response_format='initial-final-schema'
        def override(self,**kw):return SimpleNamespace(**{'response_format':self.response_format,**kw})
    request=Request();limiter=BoundedInspection(require_media=False,require_probe=True)
    pending=limiter.narrow(request)
    assert pending.response_format is None and pending.tool_choice=='any'
    observation={'complete':True,'errors':[],'browser':'Chrome','total':1,'skipped':0,'exit_code':1,
                 'results':[{'success':False,'log':['AssertionError: expected old to equal new']}]}
    request.messages=[ToolMessage(content='observed',tool_call_id='probe',name='submit_browser_reproduction',artifact={'development_browser':observation})]
    final=limiter.narrow(request)
    assert final.tools==[] and final.response_format=='initial-final-schema'


def test_audio_context_carries_transcript_without_inventing_images():
    import asyncio
    from svh.generation import recording_context
    calls=[]
    class Client:
        async def call_tool(self,name,args):
            calls.append(name)
            if name=='get_recording':
                return SimpleNamespace(is_error=False,structured_content={'id':'audio','duration_s':5,'has_audio':True,'kind':'audio'})
            assert name=='get_transcript'
            return SimpleNamespace(is_error=False,structured_content={'status':'transcribed','segments':[{'start_s':1,'end_s':2,'text':'Clear the label'}]})
    content,proof=asyncio.run(recording_context(Client(),{'id':'audio'},{'refined_predictions':[]}))
    assert calls==['get_recording','get_transcript']
    assert proof['frame_sha256']==[] and len(proof['transcript_sha256'])==64
    assert all(block['type']=='text' for block in content) and 'Clear the label' in str(content)

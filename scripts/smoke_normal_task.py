import asyncio,hashlib,json
from pathlib import Path
from svh.tasks import load_task
from svh.mcp_process import evidence_client
root=Path(__file__).resolve().parents[1];work=root/'data/runtime/normal-task-smoke';work.mkdir(exist_ok=True)
a=json.loads((root/'evals/annotations/swebench-bpmn-1655.json').read_text())
r=json.loads((root/a['source']['row_path']).read_text())
manifest={'format':'svh.task.v1','id':'normal-registration-smoke','problem_statement':r['problem_statement'],
          'environment':{'adapter':'bpmn-karma-v1','image':a['app']['image'],'base_commit':a['app']['base_commit']},
          'recording':{'path':str((root/a['media']['path']).resolve()),'sha256':a['media']['sha256'],'source_url':a['media']['source_url']}}
p=work/'task.json';p.write_text(json.dumps(manifest,indent=2)+'\n')
identity,task,evidence=load_task(root,p)
async def run():
 async with evidence_client(root,None,work/'mcp.log',task_manifest=p) as client:
  metadata=await client.call_tool('get_recording',{'recording_id':task['id']})
  frames=await client.call_tool('get_frames',{'recording_id':task['id'],'t0':4.5,'t1':6.5,'max_frames':2})
  assert not metadata.is_error and not frames.is_error
  images=[c for c in frames.content if c.type=='image'];assert len(images)==2
  proof={'format':'svh.normal-task.smoke.v1','manifest_sha256':identity,'id':task['id'],'media_sha256':a['media']['sha256'],
         'supplied_gold_or_admission_required':False,'actual_mcp_metadata':True,'actual_png_frames':len(images),
         'frame_sha256':[hashlib.sha256(c.data.encode()).hexdigest() for c in images],
         'scope':'Ordinary registration and actual authenticated MCP retrieval only; no generated check/fix measurement'}
  (root/'notes/runs/normal-task-mcp-smoke.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
asyncio.run(run())

"""Exercise an indexed ordinary recording through actual MCP, without model calls."""
import argparse
import asyncio
import base64
import hashlib
import json
from pathlib import Path
import uuid
from svh.mcp_process import evidence_client
from svh.tasks import load_task


async def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task-manifest',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    identity,task,evidence=load_task(root,args.task_manifest)
    record=evidence.recording(task['id'])
    output=(root/args.output).resolve()
    if output.exists():raise ValueError('Preserve the prior evidence smoke; choose a new output')
    logs=root/'data/runtime/task-evidence'/identity
    logs.mkdir(parents=True,exist_ok=True,mode=0o700);logs.chmod(0o700)
    async with evidence_client(root,None,logs/('mcp-smoke-'+uuid.uuid4().hex+'.log'),task_manifest=args.task_manifest) as client:
        calls={
            'metadata':('get_recording',{'recording_id':task['id']}),
            'frames':('get_frames',{'recording_id':task['id'],'t0':0,'t1':min(30,record.duration_s),'max_frames':1}),
            'search':('find_moment',{'recording_id':task['id'],'query':task['problem_statement'][:2000],'limit':2}),
            'screen':('get_screen_text',{'recording_id':task['id'],'t0':0,'t1':record.duration_s})}
        results={}
        for name,(tool,arguments) in calls.items():
            results[name]=await client.call_tool(tool,arguments)
            if results[name].is_error:raise ValueError('MCP '+tool+' failed; inspect the local log')
        images=[c for c in results['frames'].content if c.type=='image']
        matches=results['search'].structured_content['matches']
        screen=results['screen'].structured_content['frames']
        if len(images)!=1 or not matches or not screen:raise ValueError('Missing indexed evidence')
        result={'format':'svh.ordinary-evidence-smoke.v1','passed':True,'manifest_sha256':identity,
                'actual_mcp_tools':[v[0] for v in calls.values()],
                'model_calls':0,'retrieval_method':results['search'].structured_content['method'],
                'retrieved_timestamps_s':[m['timestamp_s'] for m in matches],
                'screen_frame_count':len(screen),
                'frame_sha256':hashlib.sha256(base64.b64decode(images[0].data,validate=True)).hexdigest(),
                'scope':'Actual ordinary-task MCP/index plumbing; not a retrieval quality score'}
        output.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)


if __name__=='__main__':asyncio.run(main())

"""Budgeted provider transcription and actual MCP for synthetic audio-only input."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import re
import subprocess

from svh.gemini import configured_model
from svh.ingest import ingest_task
from svh.mcp_process import evidence_client
from svh.tasks import load_task


async def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-name',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,32}',args.run_name):parser.error('Invalid run name')
    root=Path(__file__).resolve().parents[1]
    output=root/args.output
    if output.exists():raise ValueError('Preserve previous evidence; choose a new output')
    work=root/'data/runtime/audio-only-smoke'/args.run_name
    work.mkdir(parents=True,exist_ok=True,mode=0o700);work.chmod(0o700)
    media=work/'narration.wav'
    spoken=('Clearing a task label currently leaves its diagram label property set to null. '
            'Removing the text should remove that property entirely.')
    if not media.exists():
        subprocess.run(['espeak','-s','140','-w',str(media),spoken],check=True,timeout=30)
        media.chmod(0o600)
    # Copy only trusted environment identity, never solution source or grader input.
    prepared=json.loads((root/'tasks/generated-v2/swebench-bpmn-1638/tests/proof.json').read_text())['pre']
    manifest=work/'task.json'
    task={'format':'svh.task.v1','id':'audio-smoke-'+args.run_name,
          'problem_statement':'Review the narrated software bug and requirement. Ask if unclear.',
          'environment':{'adapter':'bpmn-karma-v1','image':prepared['image'],'base_commit':prepared['base_commit']},
          'recording':{'path':'narration.wav','sha256':hashlib.sha256(media.read_bytes()).hexdigest(),
                       'source_url':'controlled synthetic eSpeak narration; no human speaker'}}
    raw=json.dumps(task,indent=2)+'\n'
    if manifest.exists() and manifest.read_text()!=raw:raise ValueError('Existing smoke input changed')
    if not manifest.exists():manifest.write_text(raw);manifest.chmod(0o600)
    model=configured_model(root,name='gemini-3.5-flash-lite',output_cap=4096)
    summary=ingest_task(root,manifest,model=model)
    identity,registered,evidence=load_task(root,manifest)
    duration=evidence.recording(registered['id']).duration_s
    async with evidence_client(root,None,work/'mcp.log',task_manifest=manifest) as client:
        common={'recording_id':registered['id']}
        metadata=await client.call_tool('get_recording',common)
        transcript=await client.call_tool('get_transcript',{**common,'t0':0,'t1':duration})
        frames=await client.call_tool('get_frames',{**common,'t0':0,'t1':min(duration,30),'max_frames':1})
        screen=await client.call_tool('get_screen_text',{**common,'t0':0,'t1':duration})
        search=await client.call_tool('find_moment',{**common,'query':'label property','limit':2})
        if any(r.is_error for r in [metadata,transcript,frames,screen,search]):raise ValueError('Audio MCP smoke failed')
        if (metadata.structured_content['kind']!='audio' or not transcript.structured_content['segments']
                or frames.structured_content['evidence_mode']!='no_video' or any(c.type=='image' for c in frames.content)
                or screen.structured_content['status']!='no_video' or not search.structured_content['matches']):
            raise ValueError('Audio evidence contract failed')
        from svh.generation import recording_context
        content,proof=await recording_context(client,registered,{'refined_predictions':[]})
        if proof['frame_sha256'] or any(block['type']=='image_url' for block in content):raise ValueError('Invented video evidence')
        result={'format':'svh.audio-only-smoke.v1','passed':True,'manifest_sha256':identity,
                'media_sha256':task['recording']['sha256'],'duration_s':duration,
                'transcript_sha256':proof['transcript_sha256'],'segments':len(transcript.structured_content['segments']),
                'actual_mcp_tools':['get_recording','get_transcript','get_frames','get_screen_text','find_moment'],
                'frame_status':'no_video','retrieval_method':summary['retrieval_method'],
                'controller_received_transcript_without_images':True,'budget':model._budget.summary(),
                'scope':'Synthetic provider transcription and ordinary audio-only MCP/controller plumbing; no human speech accuracy or new repair score'}
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
        print('Ordinary task manifest: '+str(manifest),flush=True)


if __name__=='__main__':asyncio.run(main())

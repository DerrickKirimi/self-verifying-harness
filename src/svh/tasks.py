"""Ordinary task registration: no benchmark gold, supplied check or admission required."""
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
from svh.evidence import Evidence, Recording


def bind_task_run(work, identity, task):
    """Bind checkpoints before paid work, including a crash before report creation."""
    path = work / 'input-identity.json'
    expected = {'format': 'svh.task-run.v1', 'manifest_sha256': identity,
                'id': task['id'], 'image': task['image'], 'base_commit': task['base_commit']}
    if path.exists():
        if json.loads(path.read_text()) != expected:
            raise ValueError('Run name belongs to a different task manifest; use a new run name')
        return
    if any(work.iterdir()):
        raise ValueError('Existing task artifacts have no input identity; use a new run name')
    # Caller holds the worker lock. Exclusive creation also prevents overwrites.
    with path.open('x') as stream:
        json.dump(expected, stream, indent=2)
        stream.write('\n')


def load_task(root, manifest_path):
    path=(root/manifest_path).resolve()
    data=path.read_bytes()
    if len(data)>128*1024:raise ValueError('Task manifest too large')
    task=json.loads(data)
    if set(task)!={'format','id','problem_statement','environment','recording'} or task['format']!='svh.task.v1':
        raise ValueError('Use the ordinary task manifest schema; benchmark gold is not an input')
    if not isinstance(task['id'],str) or not re.fullmatch('[A-Za-z0-9_-]{1,64}',task['id']):
        raise ValueError('Invalid task identifier')
    if not isinstance(task['problem_statement'],str) or not 1<=len(task['problem_statement'])<=64*1024:
        raise ValueError('Supply a bounded stated requirement')
    env=task['environment']
    if (set(env)!={'adapter','image','base_commit'} or env['adapter']!='bpmn-karma-v1'
        or not re.fullmatch(r'(?:[A-Za-z0-9_./:-]+@)?sha256:[0-9a-f]{64}',env['image'])
        or not re.fullmatch('[0-9a-f]{40}',env['base_commit'])):
        raise ValueError('First adapter requires an immutable prepared BPMN/Karma image and buggy commit')
    media=task['recording']
    if set(media)!={'path','sha256','source_url'}:raise ValueError('Recording needs path, SHA256 and source reference')
    source=(path.parent/media['path']).resolve()
    if not source.is_file() or not 1<=source.stat().st_size<=128*1024**2:
        raise ValueError('Recording must be a local file of at most 128 MiB')
    content_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    if content_hash!=media['sha256']:raise ValueError('Recording hash mismatch')
    probe=subprocess.run(['ffprobe','-v','error','-protocol_whitelist','file,pipe','-show_entries',
        'format=duration:stream=codec_type','-of','json',str(source)],capture_output=True,timeout=30,check=True)
    meta=json.loads(probe.stdout);duration=float(meta['format']['duration'])
    if not math.isfinite(duration) or not 0<duration<=3600 or not any(s['codec_type']=='video' for s in meta['streams']):
        raise ValueError('Provide a finite video/animated recording up to one hour')
    if not isinstance(media['source_url'],str) or len(media['source_url'])>2048:
        raise ValueError('Provide a bounded source reference or owner-local description')
    recording=Recording(task['id'],source,content_hash,duration,any(s['codec_type']=='audio' for s in meta['streams']),
                        'animated_image' if source.suffix.lower()=='.gif' else 'video',media['source_url'])
    identity=hashlib.sha256(data).hexdigest()
    public={'id':task['id'],'problem_statement':task['problem_statement'],
            'issue_sha256':hashlib.sha256(task['problem_statement'].encode()).hexdigest(),
            'image':env['image'],'base_commit':env['base_commit'],'adapter':env['adapter']}
    transcript_path=root/'data/runtime/task-evidence'/identity/'transcript.json'
    transcripts={recording.id:json.loads(transcript_path.read_text())} if transcript_path.exists() else {}
    return identity,public,Evidence([recording],identity,transcripts=transcripts)

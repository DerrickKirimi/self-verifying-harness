"""Export every fully verified generated case, then require real Harbor trials."""
import argparse
import json
from pathlib import Path
from svh.extract import public_tasks
from svh.harbor_export import export_task
from svh.docker_backend import sandbox

p=argparse.ArgumentParser()
p.add_argument('--run-directory',type=Path,required=True)
p.add_argument('--output-directory',type=Path,required=True)
p.add_argument('--task-manifest',type=Path,help='export a verified ordinary run without benchmark gold')
p.add_argument('--only',action='append',help='export only this case; repeat for multiple cases')
a=p.parse_args();root=Path(__file__).resolve().parents[1]
if a.task_manifest:
 from svh.tasks import load_task
 corpus_sha,normal_task,normal_evidence=load_task(root,a.task_manifest)
 tasks=[normal_task]
else:
 corpus_sha,tasks=public_tasks(root,root/'evals/frozen-m0.json')
if a.only and not set(a.only)<={t['id'] for t in tasks}:raise SystemExit('Unknown export task ID')
run=root/a.run_directory;report=json.loads((run/'report.json').read_text())
if report['corpus_sha256']!=corpus_sha:raise SystemExit('Different source corpus')
exported=[]
for task in tasks:
 if a.only and task['id'] not in a.only:continue
 case=next(c for c in report['cases'] if c['id']==task['id'])
 for candidate in case['candidates']:
  if candidate.get('status')!='full_generated_repair':continue
  directory=run/task['id']/str(candidate['number'])
  if a.task_manifest:
   media=normal_evidence.recording(task['id']).metadata();native_patch=None
  else:
   annotation=json.loads((root/'evals/annotations'/(task['id']+'.json')).read_text())
   row=json.loads((root/annotation['source']['row_path']).read_text())
   media=annotation['media'];native_patch=row['test_patch'].encode()
  generated=json.loads((directory/'candidate.json').read_text())
  destination=root/a.output_directory/task['id']
  with sandbox(task['image'],task['base_commit']) as backend:
   license_file=backend.download_files(['/workspace/LICENSE'])[0]
   if license_file.error or not license_file.content:raise ValueError('Cannot retrieve original reuse license')
  export_task(destination,task,generated['requirement'],candidate,directory,
    media_reference={k:media[k] for k in ['sha256','source_url']},source_license=license_file.content,native_patch=native_patch)
  exported.append(task['id']);break
if not exported:raise SystemExit('No selected case has a full verified generated repair to export')
print(json.dumps({'exported':exported,'harbor_trials':'pending; packaging alone is not a passed trial'}))

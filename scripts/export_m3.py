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
a=p.parse_args();root=Path(__file__).resolve().parents[1]
corpus_sha,tasks=public_tasks(root,root/'evals/frozen-m0.json')
run=root/a.run_directory;report=json.loads((run/'report.json').read_text())
if report['corpus_sha256']!=corpus_sha:raise SystemExit('Different source corpus')
exported=[]
for task in tasks:
 case=next(c for c in report['cases'] if c['id']==task['id'])
 for candidate in case['candidates']:
  if candidate.get('status')!='full_generated_repair':continue
  directory=run/task['id']/str(candidate['number'])
  annotation=json.loads((root/'evals/annotations'/(task['id']+'.json')).read_text())
  row=json.loads((root/annotation['source']['row_path']).read_text())
  generated=json.loads((directory/'candidate.json').read_text())
  destination=root/a.output_directory/task['id']
  with sandbox(task['image'],task['base_commit']) as backend:
   license_file=backend.download_files(['/workspace/LICENSE'])[0]
   if license_file.error or not license_file.content:raise ValueError('Cannot retrieve original reuse license')
  export_task(destination,task,generated['requirement'],candidate,directory,
    media_reference={k:annotation['media'][k] for k in ['sha256','source_url']},source_license=license_file.content,native_patch=row['test_patch'].encode())
  exported.append(task['id']);break
print(json.dumps({'exported':exported,'harbor_trials':'pending; packaging alone is not a passed trial'}))

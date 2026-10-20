"""One sequential M3 stage at a time; all frozen cases remain in the report."""
import argparse
import asyncio
import fcntl
import hashlib
import json
import re
from pathlib import Path
from svh.browser_runner import observe
from svh.docker_backend import sandbox
from svh.extract import public_tasks
from svh.gemini import configured_model
from svh.generation import generate, apply_edits
from svh.mcp_process import evidence_client
from svh.verification import browser_verdict, digest, verified_check

p=argparse.ArgumentParser()
p.add_argument('--only',required=True)
p.add_argument('--stage',choices=['reproduce','repair'],required=True)
p.add_argument('--run-name',required=True)
p.add_argument('--candidate',type=int,choices=[1,2],default=1)
p.add_argument('--model',choices=['gemini-3.8-flash','gemini-3.5-flash-lite'],default='gemini-3.8-flash')
a=p.parse_args()
if not re.fullmatch('[A-Za-z0-9_-]{1,64}',a.run_name):raise SystemExit('Invalid run name')
root=Path(__file__).resolve().parents[1]
corpus=root/'evals/frozen-m0.json'
corpus_sha,tasks=public_tasks(root,corpus)
if a.only not in {t['id'] for t in tasks}:raise SystemExit('Unknown task')
work=root/'data/runtime/m3'/a.run_name;work.mkdir(parents=True,exist_ok=True)
lock=(root/'data/runtime/m3/worker.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
rpath=work/'report.json'
report=json.loads(rpath.read_text()) if rpath.exists() else {'corpus_sha256':corpus_sha,'cases':[{'id':t['id'],'status':'not_attempted','candidates':[]} for t in tasks]}
if report['corpus_sha256']!=corpus_sha:raise SystemExit('Different corpus')
task=next(t for t in tasks if t['id']==a.only)
row=next(t for t in report['cases'] if t['id']==a.only)
claims=json.loads((root/'notes/runs/m2-checkpoints-media.json').read_text())
claim=next(c for c in claims['cases'] if c['id']==a.only)
# This copies only model-produced claims/hypotheses/citations, never scorer/gold.
claim={k:claim[k] for k in ('refined_predictions','code_evidence','hypotheses','questions')}
model=configured_model(root,name=a.model,output_cap=8192);model.reasoning_effort='low'
casepath=work/task['id']/str(a.candidate);casepath.mkdir(parents=True,exist_ok=True)


def save():
    report['budget']=model._budget.summary()
    tmp=rpath.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(rpath)


async def run():
    index=a.candidate-1
    if a.stage=='reproduce':
        if len(row['candidates'])!=index:raise ValueError('Candidate already recorded or earlier candidate missing')
        candidate={'number':a.candidate,'status':'generating_check','model':a.model}
        row['candidates'].append(candidate);row['status']='attempted';save()
    else:
        candidate=row['candidates'][index]
        if candidate.get('status')!='observed_base_assertion':raise ValueError('No fresh frozen base assertion permits repair')
        review=json.loads((casepath/'alignment-review.json').read_text())
        if review.get('check_sha256')!=candidate['pre']['check_sha256'] or review.get('aligned') is not True:
            raise ValueError('An explicit claim-alignment review must bind the frozen check')
    try:
        if a.stage=='reproduce':
            async with evidence_client(root,corpus,casepath/'mcp.log') as client:
                with sandbox(task['image'],task['base_commit']) as backend:
                    output=await generate(task,claim,model,backend,client,casepath/'reproduce-trace.json')
            (casepath/'candidate.json').write_text(json.dumps(output,indent=2)+'\n')
            check=output['check_javascript'].encode();(casepath/'check.js').write_bytes(check)
            candidate['check_sha256']=digest(check)
            candidate['pre']=observe(task['image'],task['base_commit'],check,casepath/'pre')
            candidate['status']='observed_base_assertion' if browser_verdict(candidate['pre'],assertion_failure=True) else 'invalid_reproduction'
        else:
            check=(casepath/'check.js').read_bytes()
            if digest(check)!=candidate['pre']['check_sha256']:raise ValueError('Frozen check changed')
            with sandbox(task['image'],task['base_commit']) as backend:
                output=await generate(task,claim,model,backend,None,casepath/'repair-trace.json',pre=candidate['pre'],check=check)
                files=apply_edits(backend,output['edits'])
            (casepath/'source-fix.json').write_text(json.dumps(output,indent=2)+'\n')
            for path,content in files.items():
                dest=casepath/'source'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
            candidate['post']=observe(task['image'],task['base_commit'],check,casepath/'post',source_files=files)
            candidate['status']='generated_check_passed' if verified_check(candidate['pre'],candidate['post']) else 'repair_failed'
            if candidate['status']=='generated_check_passed':
                annotation=json.loads((root/'evals/annotations'/(task['id']+'.json')).read_text())
                source=json.loads((root/annotation['source']['row_path']).read_text())
                native=observe(task['image'],task['base_commit'],check,casepath/'native',source_files=files,native_test_patch=source['test_patch'].encode())
                oracle=json.loads((root/annotation['oracle']['report_path']).read_text())['results']['post']
                passed=(native.get('complete') and native['exit_code']==0 and not native['errors'] and native.get('browser') and not native['disconnected']
                        and native['total']==oracle['discovered'] and native['skipped']==oracle['skipped']
                        and sum(not r.get('skipped') for r in native['results'])==oracle['executed']
                        and all(r.get('skipped') or r.get('success') for r in native['results']))
                candidate.update(native_regressions_passed=bool(passed),native_observation_sha256=digest((casepath/'native/observation.json').read_bytes()))
                candidate['status']='full_generated_repair' if passed else 'native_regressions_failed'
    except Exception as error:
        candidate.update(status='error',error_type=type(error).__name__)
        # Exceptions can contain provider request data: retain no arbitrary exception text.
    save();print(json.dumps({'id':task['id'],'stage':a.stage,'status':candidate['status'],'budget':report['budget']}),flush=True)

asyncio.run(run())

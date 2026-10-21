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
p.add_argument('--only')
p.add_argument('--task-manifest',type=Path)
p.add_argument('--stage',choices=['reproduce','repair'],required=True)
p.add_argument('--run-name',required=True)
p.add_argument('--candidate',type=int,choices=[1,2],default=1)
p.add_argument('--model',choices=['gemini-3.8-flash','gemini-3.5-flash-lite'],default='gemini-3.8-flash')
a=p.parse_args()
if not re.fullmatch('[A-Za-z0-9_-]{1,64}',a.run_name):raise SystemExit('Invalid run name')
root=Path(__file__).resolve().parents[1]
corpus=root/'evals/frozen-m0.json'
if a.task_manifest:
    from svh.tasks import load_task
    corpus_sha,normal_task,normal_evidence=load_task(root,a.task_manifest)
    tasks=[normal_task]
    if a.only is None:a.only=normal_task['id']
else:
    corpus_sha,tasks=public_tasks(root,corpus)
if a.only not in {t['id'] for t in tasks}:raise SystemExit('Unknown task')
work=root/'data/runtime/m3'/a.run_name;work.mkdir(parents=True,exist_ok=True)
if a.task_manifest:work.chmod(0o700)
lock=(root/'data/runtime/m3/worker.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
if a.task_manifest:
    from svh.tasks import bind_task_run
    bind_task_run(work,corpus_sha,normal_task)
rpath=work/'report.json'
report=json.loads(rpath.read_text()) if rpath.exists() else {'corpus_sha256':corpus_sha,'cases':[{'id':t['id'],'status':'not_attempted','candidates':[]} for t in tasks]}
if report['corpus_sha256']!=corpus_sha:raise SystemExit('Different corpus')
if report.get('method'):
    method_bytes=(root/report['method']).read_bytes();method=json.loads(method_bytes)
    if digest(method_bytes)!=report['method_sha256'] or method['model']!=a.model:
        raise SystemExit('Use the prepared run method and model; do not mix methods silently')
task=next(t for t in tasks if t['id']==a.only)
row=next(t for t in report['cases'] if t['id']==a.only)
claim=None
if not a.task_manifest:
    claims=json.loads((root/'notes/runs/m2-checkpoints-media.json').read_text())
    claim=next(c for c in claims['cases'] if c['id']==a.only)
    # Copy only model outputs, never scorer/gold.
    claim={k:claim[k] for k in ('refined_predictions','code_evidence','hypotheses','questions')}
model=configured_model(root,name=a.model,output_cap=8192);model.reasoning_effort='medium' if a.model=='gemini-3.8-flash' else 'low'
casepath=work/task['id']/str(a.candidate);casepath.mkdir(parents=True,exist_ok=True)


def save():
    report['budget']=model._budget.summary()
    tmp=rpath.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(rpath)


async def run():
    global claim,normal_evidence
    if a.task_manifest:
        phase='audio_preparation'
        try:
            from svh.ingest import prepare_task_audio
            row.update(status='preparing',stage=phase);save()
            _,_,normal_evidence=prepare_task_audio(root,a.task_manifest,model)
            checkpoint_path=work/'checkpoint.json'
            if checkpoint_path.exists():
                phase='checkpoint_resume';row['stage']=phase;save()
                raw=checkpoint_path.read_bytes()
                if digest(raw)!=report.get('checkpoint_sha256'):
                    raise ValueError('Cached checkpoint is unbound or changed; use a new run')
                claim=json.loads(raw)
            else:
                from svh.extract import extract_claims
                from svh.checkpoint import inspect_code
                phase='claim_extraction';row['stage']=phase;save()
                first=extract_claims(normal_evidence,task,'issue+media',model,work/'extraction.json')
                phase='code_checkpoint';row['stage']=phase;save()
                attempts=work/'checkpoint-attempts';attempts.mkdir(exist_ok=True)
                number=1+max([int(p.name) for p in attempts.iterdir() if p.is_dir() and p.name.isdecimal()] or [0])
                attempt=attempts/str(number);attempt.mkdir(exist_ok=False)
                async with evidence_client(root,None,attempt/'mcp.log',task_manifest=a.task_manifest) as client:
                    with sandbox(task['image'],task['base_commit']) as backend:
                        claim=await inspect_code(task,first,model,backend,client,attempt/'trace.json')
                checkpoint_path.write_text(json.dumps(claim,indent=2)+'\n')
                report['checkpoint_sha256']=digest(checkpoint_path.read_bytes());save()
        except Exception as error:
            pending=[error];types=[];seen=set()
            while pending:
                item=pending.pop()
                if id(item) in seen:continue
                seen.add(id(item));types.append(type(item).__name__)
                pending.extend(getattr(item,'exceptions',[]))
                if item.__cause__ is not None:pending.append(item.__cause__)
            row.update(status='preparation_failed',stage=phase,error_types=types);save()
            raise SystemExit('Ordinary '+phase+' failed; retained report and attempt traces under '+str(work)) from None
        if not claim.get('refined_predictions') or not claim['refined_predictions'][0].get('expected_behavior'):
            row.update(status='abstained',stage='requirement_review',questions=claim.get('questions',[]),
                       reason='The checkpoint returned no actionable primary requirement; no check or fix is generated')
            save();print(json.dumps({'id':task['id'],'status':'abstained','budget':report['budget']}),flush=True);return
        row.update(status='attempted',stage=a.stage);row.pop('error_types',None);save()
    index=a.candidate-1
    if a.stage=='reproduce':
        if len(row['candidates'])!=index:raise ValueError('Candidate already recorded or earlier candidate missing')
        candidate={'number':a.candidate,'status':'generating_check','model':a.model}
        row['candidates'].append(candidate);row['status']='attempted';save()
    else:
        candidate=row['candidates'][index]
        if candidate.get('status')!='observed_base_assertion':raise ValueError('No fresh frozen base assertion permits repair')
        review=json.loads((casepath/'alignment-review.json').read_text())
        candidate['alignment_review']=review
        if review.get('check_sha256')!=candidate['pre']['check_sha256'] or review.get('aligned') is not True:
            raise ValueError('An explicit claim-alignment review must bind the frozen check')
    try:
        if a.stage=='reproduce':
            async with evidence_client(root,corpus,casepath/'mcp.log',task_manifest=a.task_manifest) as client:
                with sandbox(task['image'],task['base_commit']) as backend:
                    feedback=None
                    if a.candidate>1:
                        previous=work/task['id']/str(a.candidate-1)
                        feedback={'candidate':json.loads((previous/'candidate.json').read_text()) if (previous/'candidate.json').exists() else {'error':'No valid typed candidate was returned; provide a nonempty check and explanation'},
                                  'observation':json.loads((previous/'pre/observation.json').read_text()) if (previous/'pre/observation.json').exists() else None,
                                  'alignment_review':json.loads((previous/'alignment-review.json').read_text()) if (previous/'alignment-review.json').exists() else None,
                                  'console':(previous/'pre/console.log').read_text()[-16000:] if (previous/'pre/console.log').exists() else '',
                                  'instruction':'Correct setup/API mistakes before any source fix. Put rendered DOM assertions before internal DI assertions so the observed failure checks the visible symptom. Preserve general coverage; inspect actual fixture identifiers.'}
                    output=await generate(task,claim,model,backend,client,casepath/'reproduce-trace.json',feedback=feedback)
            (casepath/'candidate.json').write_text(json.dumps(output,indent=2)+'\n')
            check=output['check_javascript'].encode()
            from svh.probes import check_version_budget
            check_version_budget(casepath.parent,check)
            (casepath/'check.js').write_bytes(check)
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
                if a.task_manifest:
                    baseline=observe(task['image'],task['base_commit'],check,casepath/'native-baseline',native=True)
                    native=observe(task['image'],task['base_commit'],check,casepath/'native',source_files=files,native=True)
                    oracle={'discovered':baseline['total'],'skipped':baseline['skipped'],
                            'executed':sum(not r.get('skipped') for r in baseline['results'])}
                    baseline_ok=bool(baseline['complete'] and baseline['exit_code']==0 and not baseline['errors'] and baseline['total']>0)
                else:
                    annotation=json.loads((root/'evals/annotations'/(task['id']+'.json')).read_text())
                    source=json.loads((root/annotation['source']['row_path']).read_text())
                    native=observe(task['image'],task['base_commit'],check,casepath/'native',source_files=files,native_test_patch=source['test_patch'].encode())
                    oracle=json.loads((root/annotation['oracle']['report_path']).read_text())['results']['post']
                    baseline_ok=True
                passed=(baseline_ok and native.get('complete') and native['exit_code']==0 and not native['errors'] and native.get('browser') and not native['disconnected']
                        and native['total']==oracle['discovered'] and native['skipped']==oracle['skipped']
                        and sum(not r.get('skipped') for r in native['results'])==oracle['executed']
                        and all(r.get('skipped') or r.get('success') for r in native['results']))
                candidate.update(native_regressions_passed=bool(passed),native_observation_sha256=digest((casepath/'native/observation.json').read_bytes()))
                candidate['status']='full_generated_repair' if passed else 'native_regressions_failed'
    except Exception as error:
        pending=[error];seen=set();evidence=[]
        while pending:
            item=pending.pop()
            if id(item) in seen:continue
            seen.add(id(item));entry={'type':type(item).__name__}
            reply=getattr(item,'ai_message',None)
            if reply is not None:entry['model_reply']=reply.model_dump()
            evidence.append(entry)
            pending.extend(getattr(item,'exceptions',[]))
            if item.__cause__ is not None:pending.append(item.__cause__)
        (casepath/'generation-error.json').write_text(json.dumps(evidence,indent=2,default=str)+'\n')
        candidate.update(status='error',error_type=type(error).__name__,
            nested_error_types=[e['type'] for e in evidence])
        # Exceptions can contain provider request data: retain no arbitrary exception text.
    save();print(json.dumps({'id':task['id'],'stage':a.stage,'status':candidate['status'],'budget':report['budget']}),flush=True)

try:
    asyncio.run(run())
finally:
    fcntl.flock(lock,fcntl.LOCK_UN)
    lock.close()

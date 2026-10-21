"""Export only controller-observed generated repairs; never benchmark gold fixes."""
import json
from pathlib import Path
import re
import shutil

from svh.browser_runner import CONFIG, REPORTER, allowed_source
from svh.verification import digest, verified_check

VERIFIER = r'''import hashlib,json,pathlib,shutil,subprocess,os
root=pathlib.Path('/workspace');tests=pathlib.Path('/tests');reward=pathlib.Path('/logs/verifier/reward.json')
reward.parent.mkdir(parents=True,exist_ok=True);reward.write_text('{"reward":0}')
def sha(b):return hashlib.sha256(b).hexdigest()
def run(native,label):
    result=pathlib.Path('/tmp/svh-results.json');result.unlink(missing_ok=True)
    env=dict(os.environ)
    if native:env['SVH_NATIVE']='1'
    else:env.pop('SVH_NATIVE',None)
    with open('/logs/verifier/'+label+'.log','w') as log:
        p=subprocess.run(['su','chromeuser','-c','./node_modules/.bin/karma start /tmp/svh-karma.cjs --no-colors'],cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
    r=json.loads(result.read_text());r['exit_code']=p.returncode
    (reward.parent/(label+'.json')).write_text(json.dumps(r))
    return r
try:
    proof=json.loads((tests/'proof.json').read_text())
    if sha((tests/'check.js').read_bytes())!=proof['check_sha256']:raise ValueError('check changed')
    source=root/'lib'
    if source.is_symlink():raise ValueError('source root symlink')
    pristine=pathlib.Path('/svh-base/lib')
    originals={p.relative_to(pristine).as_posix():p for p in pristine.rglob('*') if p.is_file()}
    supplied={p.relative_to(source).as_posix():p for p in source.rglob('*') if p.is_file()}
    if not set(originals)<=set(supplied):raise ValueError('source files deleted')
    if len(supplied)>4096 or sum(p.stat().st_size for p in supplied.values())>32*1024**2:raise ValueError('source too large')
    for relative,p in supplied.items():
        if p.is_symlink() or not p.resolve().is_relative_to(source.resolve()):raise ValueError('source symlink')
        target=root/'lib'/relative
        if p.suffix!='.js':
            if relative not in originals or p.read_bytes()!=originals[relative].read_bytes():raise ValueError('non-JS modification')
        else:
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
    shutil.copyfile(tests/'check.js',root/'test/SvhGeneratedSpec.js')
    shutil.copyfile(tests/'karma.cjs','/tmp/svh-karma.cjs');shutil.copyfile(tests/'reporter.cjs','/tmp/svh-reporter.cjs')
    generated=run(False,'generated')
    if not (generated['complete'] and generated['browser'] and not generated['errors'] and not generated['disconnected'] and generated['exit_code']==0 and generated['skipped']==0 and generated['total']==proof['generated_tests'] and len(generated['results'])==generated['total'] and all(r['success'] for r in generated['results'])):raise ValueError('generated check failed')
    for independent in proof.get('independent_checks',[]):
        check=tests/'independent'/(independent['id']+'.js')
        if sha(check.read_bytes())!=independent['sha256']:raise ValueError('independent check changed')
        shutil.copyfile(check,root/'test/SvhGeneratedSpec.js')
        extra=run(False,'independent-'+independent['id'])
        if not (extra['complete'] and extra['browser'] and not extra['errors'] and not extra['disconnected'] and extra['exit_code']==0 and extra['skipped']==0 and extra['total']==independent['tests'] and len(extra['results'])==extra['total'] and all(r['success'] for r in extra['results'])):raise ValueError('independent check failed')
    shutil.copyfile(tests/'check.js',root/'test/SvhGeneratedSpec.js')
    patch=tests/'native.diff'
    if patch.exists():subprocess.run(['git','apply',str(patch)],cwd=root,check=True,capture_output=True)
    native=run(True,'native')
    expected=proof['native']
    if not (native['complete'] and native['browser'] and not native['errors'] and not native['disconnected'] and native['exit_code']==0 and native['total']==expected['discovered'] and native['skipped']==expected['skipped'] and len(native['results'])==native['total'] and all(r['skipped'] or r['success'] for r in native['results'])):raise ValueError('native regression failed')
    reward.write_text('{"reward":1}')
except Exception as error:
    (reward.parent/'failure.txt').write_text(type(error).__name__+': '+str(error))
'''


def export_task(destination, task, claim, candidate, casepath, *, media_reference, source_license, native_patch=None):
    if candidate.get('status')!='full_generated_repair' or candidate.get('native_regressions_passed') is not True or not verified_check(candidate.get('pre',{}),candidate.get('post',{})):
        raise ValueError('Export requires actual generated frozen fail/pass and independent regressions')
    check=(casepath/'check.js').read_bytes()
    review=json.loads((casepath/'alignment-review.json').read_text())
    if digest(check)!=candidate['pre']['check_sha256'] or review.get('check_sha256')!=digest(check) or review.get('aligned') is not True:
        raise ValueError('Check/claim alignment proof mismatch')
    generated=json.loads((casepath/'candidate.json').read_text())
    repair_output=json.loads((casepath/'source-fix.json').read_text())
    repro_trace=json.loads((casepath/'reproduce-trace.json').read_text())
    repair_trace=json.loads((casepath/'repair-trace.json').read_text())
    if (generated.get('check_javascript','').encode()!=check or repro_trace.get('structured_response')!=generated
            or repair_trace.get('structured_response')!=repair_output):
        raise ValueError('Artifacts differ from retained model outputs')
    files={p.relative_to(casepath/'source').as_posix():p.read_bytes() for p in (casepath/'source').rglob('*.js')}
    allowed_source(files)
    if {p:digest(b) for p,b in files.items()}!=candidate['post']['source_files_sha256']:
        raise ValueError('Generated source bytes changed')
    if not re.fullmatch('[A-Za-z0-9_-]{1,64}',task['id']):raise ValueError('Invalid task ID')
    destination.mkdir(parents=True,exist_ok=False)
    for name in ['environment','tests','solution']:(destination/name).mkdir()
    if not source_license:raise ValueError('Source reuse license is required')
    (destination/'SOURCE-LICENSE').write_bytes(source_license)
    (destination/'SOURCE.md').write_text('Upstream source: https://github.com/bpmn-io/bpmn-js/tree/'+task['base_commit']+'\nPrepared image: '+task['image']+'\nMedia is referenced, not redistributed. The source fix and primary check were generated by the budgeted coding harness; identifier variation is controller-authored.\n')
    (destination/'instruction.md').write_text('Fix the recorded software requirement in /workspace. Edit lib JavaScript source only; preserve existing behavior.\n\n'+claim+'\n\nRecording source (reference only): '+json.dumps(media_reference)+'\n')
    (destination/'task.toml').write_text('schema_version = "1.4"\n[task]\nname = "svh/'+task['id']+'"\nversion = "0.1.0"\n[environment]\ncpus = 2\nmemory_mb = 4096\n[agent]\nnetwork_mode = "no-network"\ntimeout_sec = 600\n[verifier]\nnetwork_mode = "no-network"\nenvironment_mode = "separate"\ntimeout_sec = 700\n[[artifacts]]\nsource = "/workspace/lib"\ndestination = "source"\n')
    dockerfile='FROM '+task['image']+'\nUSER root\nRUN mkdir -p /workspace && git -C /testbed archive '+task['base_commit']+' | tar -x -C /workspace\nRUN rm -rf /testbed/.git && ln -s /testbed/node_modules /workspace/node_modules && mkdir -p /svh-base && cp -R /workspace/lib /svh-base/lib\nWORKDIR /workspace\n'
    (destination/'environment/Dockerfile').write_text(dockerfile)
    (destination/'tests/check.js').write_bytes(check)
    (destination/'tests/karma.cjs').write_text(CONFIG)
    (destination/'tests/reporter.cjs').write_text(REPORTER)
    (destination/'tests/verify.py').write_text(VERIFIER)
    (destination/'tests/test.sh').write_text('#!/bin/bash\nset -eu\nmkdir -p /logs/verifier\nprintf \'{"reward":0}\\n\' > /logs/verifier/reward.json\npython3 -I /tests/verify.py\n')
    if native_patch is not None:(destination/'tests/native.diff').write_bytes(native_patch)
    native_bytes=(casepath/'native/observation.json').read_bytes()
    if digest(native_bytes)!=candidate.get('native_observation_sha256'):raise ValueError('Native proof changed')
    native=json.loads(native_bytes)
    proof={'check_sha256':digest(check),'generated_tests':candidate['post']['total'],
           'native':{'discovered':native['total'],'skipped':native['skipped']},
           'pre':candidate['pre'],'post':candidate['post'],'alignment_review':review,
           'native_observation_sha256':digest((casepath/'native/observation.json').read_bytes()),
           'solution_origin':'agent-generated source file bytes, not benchmark gold','media':media_reference,
           'generation_provenance':{name:digest((casepath/name).read_bytes()) for name in ['candidate.json','source-fix.json','reproduce-trace.json','repair-trace.json']}}
    (destination/'tests/proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    for path,content in files.items():
        p=destination/'solution/source'/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
    (destination/'solution/solve.sh').write_text('#!/bin/bash\nset -eu\ncp -R /solution/source/lib/. /workspace/lib/\n')
    challenge_path=casepath/'challenges/report.json'
    if challenge_path.exists():
        challenges=json.loads(challenge_path.read_text())
        if challenges.get('passed') is not True:raise ValueError('Known wrong-fix challenge remains unresolved')
        proof['wrong_fix_challenges_sha256']=digest(challenge_path.read_bytes())
        proof['independent_checks']=[]
        for item in challenges['independent_checks']:
            identifier=item['id']
            if (not re.fullmatch('[A-Za-z0-9_-]{1,64}',identifier) or not verified_check(item['pre'],item['post'])
                    or item['post']['source_files_sha256']!=candidate['post']['source_files_sha256']
                    or item['post']['image']!=task['image'] or item['post']['base_commit']!=task['base_commit']):
                raise ValueError('Independent check needs observed frozen base assertion failure and generated-fix pass')
            if Path(item['path']).name!=item['path']:raise ValueError('Independent check path must be local')
            content=(casepath/'challenges'/item['path']).read_bytes()
            if digest(content)!=item['sha256']:raise ValueError('Independent check changed')
            target=destination/'tests/independent'/(identifier+'.js');target.parent.mkdir(exist_ok=True);target.write_bytes(content)
            proof['independent_checks'].append({'id':identifier,'sha256':item['sha256'],'tests':item['post']['total'],'pre':item['pre'],'post':item['post']})
        (destination/'tests/proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    hashes={p.relative_to(destination).as_posix():digest(p.read_bytes()) for p in destination.rglob('*') if p.is_file()}
    (destination/'bundle.json').write_text(json.dumps({'files':hashes,'harbor_trials':'pending; never infer reward from packaging'},indent=2)+'\n')
    return proof

import hashlib,json,pathlib,shutil,subprocess,os
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

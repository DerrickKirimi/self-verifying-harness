import json
from pathlib import Path
import pytest
pytest.importorskip('deepagents')
from svh.harbor_export import export_task
from svh.verification import digest


def test_ordinary_export_route_never_reads_benchmark_gold(tmp_path,monkeypatch):
    import hashlib
    import runpy
    import sys
    from contextlib import contextmanager
    from types import SimpleNamespace
    import svh.extract
    import svh.tasks
    import svh.docker_backend
    import svh.harbor_export
    clip=tmp_path/'clip.gif';clip.write_bytes(b'controlled recording')
    manifest=tmp_path/'task.json'
    manifest.write_text(json.dumps({'format':'svh.task.v1','id':'owner-task','problem_statement':'Clear label DI',
        'environment':{'adapter':'bpmn-karma-v1','image':'sha256:'+'a'*64,'base_commit':'b'*40},
        'recording':{'path':'clip.gif','sha256':hashlib.sha256(clip.read_bytes()).hexdigest(),'source_url':'owner-local'}}))
    monkeypatch.setattr(svh.tasks.subprocess,'run',lambda *a,**k:SimpleNamespace(stdout=b'{"format":{"duration":"2"},"streams":[{"codec_type":"video"}]}'))
    def no_gold(*args):raise AssertionError('Ordinary export must not read benchmark rows')
    monkeypatch.setattr(svh.extract,'public_tasks',no_gold)
    work=tmp_path/'run';case=work/'owner-task/1';case.mkdir(parents=True)
    (case/'candidate.json').write_text('{"requirement":"Clear the retained label property"}')
    (work/'report.json').write_text(json.dumps({'corpus_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
        'cases':[{'id':'owner-task','candidates':[{'number':1,'status':'full_generated_repair'}]}]}))
    @contextmanager
    def sandbox(*args):
        yield SimpleNamespace(download_files=lambda paths:[SimpleNamespace(error=None,content=b'Fixture license')])
    monkeypatch.setattr(svh.docker_backend,'sandbox',sandbox)
    calls=[]
    monkeypatch.setattr(svh.harbor_export,'export_task',lambda *a,**k:calls.append((a,k)))
    script=Path(__file__).resolve().parents[1]/'scripts/export_m3.py'
    monkeypatch.setattr(sys,'argv',[str(script),'--task-manifest',str(manifest),
        '--run-directory',str(work),'--output-directory',str(tmp_path/'exported'),'--only','owner-task'])
    runpy.run_path(str(script),run_name='__main__')
    assert len(calls)==1 and calls[0][0][1]['id']=='owner-task'
    assert calls[0][1]['native_patch'] is None
    assert calls[0][1]['media_reference']=={'sha256':hashlib.sha256(clip.read_bytes()).hexdigest(),'source_url':'owner-local'}
    report=json.loads((work/'report.json').read_text())
    report['cases'][0]['candidates'][0]['status']='repair_failed'
    (work/'report.json').write_text(json.dumps(report))
    with pytest.raises(SystemExit,match='No selected case'):
        runpy.run_path(str(script),run_name='__main__')
    assert len(calls)==1


def test_export_rejects_unverified_or_changed_generated_inputs(tmp_path):
    case=tmp_path/'case';case.mkdir();(case/'check.js').write_bytes(b'generated check')
    generated={'check_javascript':'generated check'};repair={'edits':[]}
    for filename,value in [('candidate.json',generated),('source-fix.json',repair),('reproduce-trace.json',{'structured_response':generated}),('repair-trace.json',{'structured_response':repair})]:
        (case/filename).write_text(json.dumps(value))
    checksha=digest(b'generated check')
    (case/'alignment-review.json').write_text(json.dumps({'aligned':True,'check_sha256':checksha}))
    (case/'source/lib').mkdir(parents=True);(case/'source/lib/a.js').write_bytes(b'generated source fix')
    (case/'native').mkdir();(case/'native/observation.json').write_text(json.dumps({'total':100,'skipped':2}))
    pre={'exit_code':1,'complete':True,'errors':[],'browser':'Chrome','total':1,'skipped':0,
         'results':[{'name':'claim','success':False,'log':['AssertionError: expected old to equal new']}],
         'check_sha256':checksha,'image':'sha256:'+'a'*64,'base_commit':'b'*40,
         'source_is_base':True,'runner_sha256':'runner','source_archive_sha256':'archive'}
    post={**pre,'exit_code':0,'source_is_base':False,'results':[{'name':'claim','success':True}],
          'source_files_sha256':{'lib/a.js':digest(b'generated source fix')}}
    candidate={'native_observation_sha256':digest((case/'native/observation.json').read_bytes()),'status':'full_generated_repair','native_regressions_passed':True,'pre':pre,'post':post}
    task={'id':'case','image':pre['image'],'base_commit':pre['base_commit']}
    exported=tmp_path/'exported'
    export_task(exported,task,'expected behavior',candidate,case,media_reference={'url':'reference-only'},source_license=b'Unit-test license fixture')
    assert 'separate' in (exported/'task.toml').read_text()
    assert (exported/'tests/check.js').read_bytes()==b'generated check'
    assert (exported/'solution/source/lib/a.js').read_bytes()==b'generated source fix'
    (case/'source/lib/a.js').write_bytes(b'tampered')
    with pytest.raises(ValueError,match='source bytes changed'):
        export_task(tmp_path/'bad',task,'expected behavior',candidate,case,media_reference={},source_license=b'Unit-test license fixture')
    candidate['status']='generated_check_passed'
    with pytest.raises(ValueError,match='independent regressions'):
        export_task(tmp_path/'bad2',task,'expected behavior',candidate,case,media_reference={},source_license=b'Unit-test license fixture')

import json
from pathlib import Path
import pytest
pytest.importorskip('deepagents')
from svh.harbor_export import export_task
from svh.verification import digest


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

import hashlib
import json
from types import SimpleNamespace
import pytest
from svh.tasks import load_task


def test_task_run_resume_is_bound_before_any_checkpoint_or_report(tmp_path):
    from svh.tasks import bind_task_run
    task={'id':'owner-task','image':'sha256:'+'a'*64,'base_commit':'b'*40}
    bind_task_run(tmp_path,'c'*64,task)
    # A stage can crash after writing a checkpoint and before creating report.json.
    (tmp_path/'checkpoint.json').write_text('{"claim":"from the first recording"}')
    bind_task_run(tmp_path,'c'*64,task)
    with pytest.raises(ValueError,match='different task manifest'):
        bind_task_run(tmp_path,'d'*64,task)
    other=tmp_path/'legacy';other.mkdir();(other/'extraction.json').write_text('{}')
    with pytest.raises(ValueError,match='no input identity'):
        bind_task_run(other,'c'*64,task)


def test_normal_registration_has_no_gold_or_oracle_dependency(tmp_path,monkeypatch):
    clip=tmp_path/'clip.gif';clip.write_bytes(b'fake video bytes')
    data={'format':'svh.task.v1','id':'owner-task','problem_statement':'The visible label should use stroke color.',
          'environment':{'adapter':'bpmn-karma-v1','image':'sha256:'+'a'*64,'base_commit':'b'*40},
          'recording':{'path':'clip.gif','sha256':hashlib.sha256(clip.read_bytes()).hexdigest(),'source_url':'owner-local'}}
    path=tmp_path/'task.json';path.write_text(json.dumps(data))
    monkeypatch.setattr('svh.tasks.subprocess.run',lambda *a,**k:SimpleNamespace(stdout=b'{"format":{"duration":"6"},"streams":[{"codec_type":"video"}]}'))
    identity,task,evidence=load_task(tmp_path,path)
    assert task['id']=='owner-task' and len(identity)==64
    assert evidence.recording('owner-task').duration_s==6
    assert evidence.transcript('owner-task',0,1)['status']=='no_audio'
    data['gold_patch']='not allowed';path.write_text(json.dumps(data))
    with pytest.raises(ValueError):load_task(tmp_path,path)
    data.pop('gold_patch');path.write_text(json.dumps(data));clip.write_bytes(b'changed')
    with pytest.raises(ValueError,match='hash mismatch'):load_task(tmp_path,path)

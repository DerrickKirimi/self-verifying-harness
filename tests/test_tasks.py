import hashlib
import json
from types import SimpleNamespace
import pytest
from svh.tasks import load_task


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

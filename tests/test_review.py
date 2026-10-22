from copy import deepcopy
import hashlib
import json

import pytest
from svh import review
from svh.claims import score


def packet():
    template={'condition':'issue+media','prediction_sha256':'fixed','scorer':'UNREVIEWED',
              'predictions':[{'recording_id':'case','prediction_id':str(i),'gold_claim_id':None,
                              'symptom_match':None,'expected_match':None,'source_support':None,'reason':''}
                             for i in (1,2)]}
    cases={'case':{'predictions':[{'id':str(i),'symptom':'fixture','expected_behavior':'fixture'} for i in (1,2)]}}
    references={'case':{'id':'case','media':{'path':'fixture.gif','duration_s':10},
                        'claims':[{'id':'reference','text':'Fixture requirement','t_start_s':1,'t_end_s':2}]}}
    return template,cases,references


def test_quit_after_one_confirmed_row_retains_nulls_and_resumes(tmp_path):
    template,cases,refs=packet()
    current=review.resume(template,None,'fixture-reviewer-not-human-evidence',refs)
    answers=iter(['y','y','y','reference','Fixture reason','y','q'])
    path=tmp_path/'review.json'
    assert review.collect(current,cases,refs,path,ask=lambda _:next(answers),show=lambda _:None) is False
    saved=json.loads(path.read_text())
    assert saved['predictions'][0]['symptom_match'] is True
    assert saved['predictions'][1]==template['predictions'][1]
    assert path.stat().st_mode & 0o077 == 0
    resumed=review.resume(template,saved,'fixture-reviewer-not-human-evidence',refs)
    answers=iter(['n','n','n','Different fixture claim','y'])
    assert review.collect(resumed,cases,refs,path,ask=lambda _:next(answers),show=lambda _:None)
    assert resumed['predictions'][0]==saved['predictions'][0]
    assert resumed['predictions'][1]['gold_claim_id'] is None
    assert template['predictions'][0]['symptom_match'] is None


def test_unconfirmed_or_partial_row_is_never_recorded(tmp_path):
    template,cases,refs=packet();current=review.resume(template,None,'fixture-reviewer',refs)
    answers=iter(['y','q']);path=tmp_path/'review.json'
    assert not review.collect(current,cases,refs,path,ask=lambda _:next(answers),show=lambda _:None)
    saved=json.loads(path.read_text());assert saved['predictions']==template['predictions']
    predictions={'corpus_sha256':'corpus','condition':'issue+media','cases':[{'id':'case','predictions':cases['case']['predictions']}]}
    with pytest.raises(ValueError,match='booleans'):
        score(predictions,saved,list(refs.values()),{'corpus_sha256':'corpus'},'fixed')


def test_exact_blank_template_can_start_without_adopting_any_decisions():
    template,_,refs=packet()
    started=review.resume(template,deepcopy(template),'fixture-reviewer',refs)
    assert started['scorer']=='fixture-reviewer'
    assert started['predictions']==template['predictions']


@pytest.mark.parametrize('change',['reviewer','hash','extra','row_order','partial','reason'])
def test_resume_rejects_changed_provenance_or_incomplete_decisions(change):
    template,cases,refs=packet();prior=review.resume(template,None,'fixture-reviewer',refs)
    if change=='reviewer':prior['scorer']='someone-else'
    if change=='hash':prior['prediction_sha256']='changed'
    if change=='extra':prior['unexpected']='changed'
    if change=='row_order':prior['predictions'].reverse()
    if change=='partial':prior['predictions'][0]['symptom_match']=True
    if change=='reason':prior['predictions'][0].update(symptom_match=False,expected_match=False,source_support=False,reason='')
    with pytest.raises(ValueError):review.resume(template,prior,'fixture-reviewer',refs)


def test_private_output_refuses_tracked_paths_and_symlinks(tmp_path):
    (tmp_path/'data/runtime').mkdir(parents=True)
    with pytest.raises(ValueError):review.private_output(tmp_path,'evals/filled.json')
    target=tmp_path/'data/runtime/target';target.write_text('private');target.chmod(0o600)
    link=target.with_name('link');link.symlink_to(target)
    with pytest.raises(ValueError):review.private_output(tmp_path,link)
    assert review.private_output(tmp_path,target)==target
    target.chmod(0o644)
    with pytest.raises(ValueError):review.private_output(tmp_path,target)


def test_load_packet_rejects_changed_media_and_prediction_bindings(tmp_path,monkeypatch):
    import svh.corpus
    template,cases,refs=packet()
    media=tmp_path/'fixture.gif';media.write_bytes(b'synthetic fixture')
    refs['case']['media']['sha256']=hashlib.sha256(media.read_bytes()).hexdigest()
    predictions={'corpus_sha256':'corpus','condition':'issue+media','cases':[{'id':'case',**cases['case']}]}
    data=json.dumps(predictions).encode();template['prediction_sha256']=hashlib.sha256(data).hexdigest()
    (tmp_path/'predictions.json').write_bytes(data)
    (tmp_path/'template.json').write_text(json.dumps(template))
    monkeypatch.setitem(review.CONDITIONS,'fixture',('predictions.json','template.json'))
    monkeypatch.setattr(svh.corpus,'load_frozen_corpus',lambda *a:({'corpus_sha256':'corpus'},list(refs.values())))
    assert len(review.load_packet(tmp_path,'fixture')[0]['predictions'])==2
    media.write_bytes(b'changed')
    with pytest.raises(ValueError,match='recording changed'):review.load_packet(tmp_path,'fixture')
    media.write_bytes(b'synthetic fixture');(tmp_path/'predictions.json').write_bytes(data+b' ')
    with pytest.raises(ValueError,match='different frozen'):review.load_packet(tmp_path,'fixture')

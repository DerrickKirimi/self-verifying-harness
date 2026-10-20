import copy
import pytest
from svh.verification import browser_verdict, verified_check, score


def pair():
    pre={'exit_code':1,'complete':True,'errors':[],'browser':'Chrome Headless','total':1,'skipped':0,
         'results':[{'name':'claim','success':False,'log':['AssertionError: expected red to equal blue']}],
         'check_sha256':'frozen','image':'immutable','base_commit':'base','source_is_base':True}
    post=copy.deepcopy(pre);post.update(exit_code=0,source_is_base=False)
    post['results']=[{'name':'claim','success':True,'log':[]}]
    return pre,post


def test_observed_assertion_pair_required():
    pre,post=pair();assert verified_check(pre,post)
    for changes in [{'check_sha256':'changed'},{'exit_code':None},{'complete':False},{'total':2},
                    {'errors':['browser disconnected']},{'skipped':1}]:
        bad={**post,**changes};assert not verified_check(pre,bad)
    pre['results'][0]['log']=['TypeError: broken setup'];assert not browser_verdict(pre,assertion_failure=True)


def test_denominator_and_generated_repair_are_separate():
    pre,post=pair();rubric={'minimum_artifacts':10,'valid_reproduction_wilson_lower':.2,'minimum_full_generated_repairs':1}
    attempts=[{'id':str(i),'candidates':[{'pre':pre,'post':post}]} for i in range(11)]
    result=score(attempts,rubric,[str(i) for i in range(11)])
    assert result['valid_reproductions']['successes']==11 and not result['generated_verification_gate_passed']
    attempts[0]['candidates'][0]['native_regressions_passed']=True
    assert score(attempts,rubric,[str(i) for i in range(11)])['generated_verification_gate_passed']
    with pytest.raises(ValueError):score(attempts[:-1],rubric,[str(i) for i in range(11)])

"""Finite wrong-fix controls for the generated SubProcess property repair."""
import argparse
import json
from pathlib import Path
from svh.browser_runner import observe
from svh.docker_backend import sandbox
from svh.verification import digest, browser_verdict, verified_check

p=argparse.ArgumentParser()
p.add_argument('--run-directory',type=Path,required=True)
a=p.parse_args()
root=Path(__file__).resolve().parents[1]
run=root/a.run_directory
report=json.loads((run/'report.json').read_text())
candidate=next(c for c in report['cases'] if c['id']=='swebench-bpmn-1640')['candidates'][0]
if candidate['status']!='full_generated_repair':raise SystemExit('Actual complete generated repair required')
case=run/'swebench-bpmn-1640/1'
check=(case/'check.js').read_bytes()
if digest(check)!=candidate['pre']['check_sha256']:raise ValueError('Frozen check changed')
variant=check.replace(b'SubProcess_1',b'SubProcess_outside_recording')
if check.count(b'>1</')!=1 or check.count(b".body).to.equal('1')")!=2:
    raise ValueError('Expected explicit cardinality setup and two assertions')
variant=variant.replace(b'>1</',b'>3</').replace(b".body).to.equal('1')",b".body).to.equal('3')").replace(b'${foo}',b'${outsideRecording}')
challenge=case/'challenges'
challenge.mkdir(exist_ok=False)
(challenge/'varied-id-values.js').write_bytes(variant)
files={p.relative_to(case/'source').as_posix():p.read_bytes() for p in (case/'source').rglob('*.js')}
path='lib/features/popup-menu/ReplaceMenuProvider.js'
pre=candidate['pre']
with sandbox(pre['image'],pre['base_commit']) as backend:
    original=backend.download_files(['/workspace/'+path])[0]
    if original.error or original.content is None:raise ValueError('Could not read actual baseline source')
    baseline=original.content
fix=json.loads((case/'source-fix.json').read_text())['edits'][0]
old,new=fix['old'],fix['new']
if baseline.count(old.encode())!=1 or baseline.replace(old.encode(),new.encode(),1)!=files[path]:
    raise ValueError('Generated source bytes changed')
results={'scope':'Finite authored deletion, suppression and example-shortcut controls; not a comprehensive mutation score',
         'check_origin':'Original model-generated check plus controller-authored identifier/cardinality/condition variation','cases':[]}
def save():
    (challenge/'report.json').write_text(json.dumps(results,indent=2)+'\n')
def trial(name,test,source):
    observation=observe(pre['image'],pre['base_commit'],test,challenge/name,source_files=source)
    results['cases'].append({'name':name,'observation':observation})
    save()
    print(json.dumps({'name':name,'passed':browser_verdict(observation),
                      'assertion_failure':browser_verdict(observation,assertion_failure=True)}),flush=True)
    return observation
vp=trial('varied-id-values-base',variant,None)
vf=trial('varied-id-values-generated-fix',variant,files)
if not verified_check(vp,vf):raise ValueError('Independent check lacks actual unchanged fail/pass')
deletion_function='''  function toggleLoopEntry(event, entry) {
    self._modeling.updateProperties(element, { loopCharacteristics: undefined });
  }'''
deletion=baseline.replace(old.encode(),deletion_function.encode(),1)
head='  function toggleLoopEntry(event, entry) {'
if not old.startswith(head) or not old.endswith('\n  }'):raise ValueError('Unexpected original function shape')
suppressed=head+'\n    try {'+old[len(head):-len('\n  }')]+'\n    } catch (ignored) {}\n  }'
suppression=baseline.replace(old.encode(),suppressed.encode(),1)
condition='if (currentLoopCharacteristics && is(currentLoopCharacteristics, entry.options.loopCharacteristics))'
if new.count(condition)!=1:raise ValueError('Unexpected generated fix shape')
shortcut_new=new.replace(condition,"if (element.id === 'SubProcess_1' && currentLoopCharacteristics && is(currentLoopCharacteristics, entry.options.loopCharacteristics))",1)
shortcut=baseline.replace(old.encode(),shortcut_new.encode(),1)
d=trial('feature-deletion',check,{path:deletion})
s=trial('error-suppression',check,{path:suppression})
o=trial('example-shortcut-primary',check,{path:shortcut})
ov=trial('example-shortcut-varied-id-values',variant,{path:shortcut})
results['passed']=(browser_verdict(d,assertion_failure=True) and browser_verdict(s,assertion_failure=True)
                   and browser_verdict(o) and browser_verdict(ov,assertion_failure=True))
results['independent_checks']=[{'id':'varied-id-values','path':'varied-id-values.js','sha256':digest(variant),'pre':vp,'post':vf}]
results['mutant_source_sha256']={name:digest(content) for name,content in [('feature-deletion',deletion),('error-suppression',suppression),('example-shortcut',shortcut)]}
for name,content in [('feature-deletion',deletion),('error-suppression',suppression),('example-shortcut',shortcut)]:
    (challenge/(name+'.js')).write_bytes(content)
save()
if not results['passed']:raise SystemExit('A finite wrong-fix control was accepted or did not produce its intended verdict')
print(json.dumps({'challenge_gate_passed':True,'scope':results['scope']}))

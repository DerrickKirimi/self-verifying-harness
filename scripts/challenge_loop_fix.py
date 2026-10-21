"""Finite, explicit controls for the generated loop-serialization demonstration."""
import argparse
import json
from pathlib import Path
from svh.browser_runner import observe
from svh.docker_backend import sandbox
from svh.verification import digest,browser_verdict,verified_check

p=argparse.ArgumentParser();p.add_argument('--run-directory',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];run=root/a.run_directory
casepath=run/'swebench-bpmn-1679/2';report=json.loads((run/'report.json').read_text())
candidate=next(c for c in report['cases'] if c['id']=='swebench-bpmn-1679')['candidates'][1]
if candidate['status']!='full_generated_repair':raise SystemExit('First complete generated repair is required')
pre=candidate['pre'];check=(casepath/'check.js').read_bytes();variant=check.replace(b'Task_1',b'Task_outside_recording')
if variant==check:raise ValueError('Expected named generated fixture')
challenge=casepath/'challenges';challenge.mkdir(exist_ok=False)
(challenge/'varied-id.js').write_bytes(variant)
files={p.relative_to(casepath/'source').as_posix():p.read_bytes() for p in (casepath/'source').rglob('*.js')}
path='lib/features/popup-menu/ReplaceMenuProvider.js'
with sandbox(pre['image'],pre['base_commit']) as backend:
 original=backend.download_files(['/workspace/'+path])[0]
 if original.error or original.content is None:raise ValueError('Could not read baseline source')
 baseline=original.content
fix=json.loads((casepath/'source-fix.json').read_text())['edits'][0]
if baseline.count(fix['old'].encode())!=1:raise ValueError('Source does not match observed generated fix')
if baseline.replace(fix['old'].encode(),fix['new'].encode(),1)!=files[path]:raise ValueError('Generated fix bytes changed')
results={'scope':'Finite authored wrong-fix challenges; not a comprehensive mutation score','check_origin':'Original model-generated check, plus controller-authored identifier variation','cases':[]}
def save():
 (challenge/'report.json').write_text(json.dumps(results,indent=2)+'\n')
def run_case(name,test,source):
 result=observe(pre['image'],pre['base_commit'],test,challenge/name,source_files=source)
 results['cases'].append({'name':name,'observation':result});save();print(json.dumps({'name':name,'passed':browser_verdict(result),'assertion_failure':browser_verdict(result,assertion_failure=True)}),flush=True)
 return result
variant_pre=run_case('varied-id-base',variant,None)
variant_post=run_case('varied-id-generated-fix',variant,files)
if not verified_check(variant_pre,variant_post):raise ValueError('Independent variation has not established fail-before/pass-after')
# Delete the selectable modes, leaving ordinary loop mode intact.
needle=b'  return loopEntries;'
if baseline.count(needle)!=1:raise ValueError('Deletion control location changed')
deletion=baseline.replace(needle,b"  return loopEntries.filter(function(entry) { return entry.id === 'toggle-loop'; });",1)
d=run_case('feature-deletion',check,{path:deletion})
# Swallow exceptions while leaving the incorrect serialization logic untouched.
start=b'  function toggleLoopEntry(event, entry) {'
end=b'    self._modeling.updateProperties(element, { loopCharacteristics: loopCharacteristics });\n  }'
if baseline.count(start)!=1 or baseline.count(end)!=1:raise ValueError('Suppression control location changed')
suppression=baseline.replace(start,start+b'\n    try {',1).replace(end,end[:-4]+b'    } catch (ignored) {}\n  }',1)
s=run_case('error-suppression',check,{path:suppression})
old=fix['old'];new=fix['new']
overfit_old='if (isUndefined(entry.options.isSequential) || !loopCharacteristics)'
overfit_new="if (isUndefined(entry.options.isSequential) || !loopCharacteristics || (element.id === 'Task_1' && !is(loopCharacteristics, entry.options.loopCharacteristics)))"
if old.count(overfit_old)!=1:raise ValueError('Shortcut control location changed')
overfit=baseline.replace(old.encode(),old.replace(overfit_old,overfit_new).encode(),1)
o=run_case('fixture-shortcut-primary',check,{path:overfit})
ov=run_case('fixture-shortcut-varied-id',variant,{path:overfit})
results['passed']=(browser_verdict(d,assertion_failure=True) and browser_verdict(s,assertion_failure=True) and browser_verdict(o) and browser_verdict(ov,assertion_failure=True))
results['independent_checks']=[{'id':'varied-id','path':'varied-id.js','sha256':digest(variant),'pre':variant_pre,'post':variant_post}]
results['mutant_source_sha256']={name:digest(data) for name,data in [('feature-deletion',deletion),('error-suppression',suppression),('fixture-shortcut',overfit)]}
for name,data in [('feature-deletion',deletion),('error-suppression',suppression),('fixture-shortcut',overfit)]:
 (challenge/(name+'.js')).write_bytes(data)
save()
if not results['passed']:raise SystemExit('A wrong-fix control was unexpectedly accepted or not a usable control')
print(json.dumps({'challenge_gate_passed':True,'scope':results['scope']}))

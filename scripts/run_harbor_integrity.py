"""Real, sequential nop/oracle trials; require the observed verdict, not just reward."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from svh.verification import browser_verdict

p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);p.add_argument('--run-name',required=True)
a=p.parse_args();root=Path(__file__).resolve().parents[1];task=(root/a.task).resolve()
if not re.fullmatch('[A-Za-z0-9_-]{1,64}',a.run_name):raise SystemExit('Invalid run name')
package=json.loads((task/'bundle.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,digest in package['files'].items():
 if sha(task/name)!=digest:raise ValueError('Task package changed')
proof=json.loads((task/'tests/proof.json').read_text())
jobs=root/'data/runtime/harbor-jobs';jobs.mkdir(exist_ok=True)
report={'task':task.name,'bundle_sha256':sha(task/'bundle.json'),'trials':[],'passed':False}
out=root/'notes/runs'/('harbor-'+a.run_name+'.json')
if out.exists():raise SystemExit('Use a new run name; preserve prior trials')
env={'PATH':os.environ['PATH'],'HOME':os.environ['HOME'],'LANG':'C.UTF-8','LC_ALL':'C.UTF-8','RICH_DISABLE_ANIMATIONS':'1','DOCKER_CONFIG':str(root/'data/runtime/docker-client')}
for agent,expected in [('nop',0),('oracle',1)]:
 name=a.run_name+'-'+agent
 cmd=[str(root/'data/runtime/harbor-venv/bin/python'),'-I','-m','harbor.cli.main','run','--path',str(task),'--agent',agent,'--env','docker','--jobs-dir',str(jobs),'--job-name',name,'--n-concurrent','1','--max-retries','0','--quiet']
 log=jobs/(name+'.log')
 print('Running actual Harbor '+agent+' trial',flush=True)
 with log.open('w') as stream:
  process=subprocess.run(cmd,cwd=root,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=1800)
 trial_files=[path for path in (jobs/name).glob('*/result.json')]
 if len(trial_files)!=1:
  report['trials'].append({'agent':agent,'status':'infrastructure_error','exit_code':process.returncode,'log_sha256':sha(log)})
  out.write_text(json.dumps(report,indent=2)+'\n');raise SystemExit('Harbor did not produce exactly one trial; inspect ignored log')
 result_path=trial_files[0];result=json.loads(result_path.read_text());trial=result_path.parent
 rewards=(result.get('verifier_result') or {}).get('rewards')
 generated_path=trial/'verifier/generated.json'
 observed=json.loads(generated_path.read_text()) if generated_path.exists() else {}
 observation_ok=browser_verdict(observed,assertion_failure=agent=='nop')
 if agent=='oracle':
  native_path=trial/'verifier/native.json';native=json.loads(native_path.read_text()) if native_path.exists() else {}
  observation_ok=observation_ok and native.get('complete') and native.get('exit_code')==0 and not native.get('errors') and bool(native.get('browser')) and native.get('total')==proof['native']['discovered'] and native.get('skipped')==proof['native']['skipped'] and all(r.get('skipped') or r.get('success') for r in native.get('results',[]))
  for extra in proof.get('independent_checks',[]):
   path=trial/'verifier'/('independent-'+extra['id']+'.json')
   extra_result=json.loads(path.read_text()) if path.exists() else {}
   observation_ok=observation_ok and browser_verdict(extra_result) and extra_result['total']==extra['tests']
 passed=process.returncode==0 and not result.get('exception_info') and rewards=={'reward':expected} and bool(observation_ok)
 row={'agent':agent,'expected_reward':expected,'actual_rewards':rewards,'passed':passed,
      'exception_type':(result.get('exception_info') or {}).get('exception_type'),'trial_result_sha256':sha(result_path),
      'completed_primary_browser_tests':observed.get('total'),'target_assertion_failure':browser_verdict(observed,assertion_failure=True),
      'log_sha256':sha(log)}
 report['trials'].append(row);out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(row),flush=True)
 if not passed:raise SystemExit('Actual Harbor trial failed integrity; retain evidence and fix packaging before retry')
report['passed']=True;out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'harbor_integrity_passed':True}))

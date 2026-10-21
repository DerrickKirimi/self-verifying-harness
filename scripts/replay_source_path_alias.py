"""Controller-only replay of the captured rejected1638 fix; no model calls."""
import json
from pathlib import Path
from svh.extract import public_tasks
from svh.docker_backend import sandbox
from svh.generation import apply_edits
from svh.browser_runner import observe
from svh.verification import digest, verified_check

root=Path(__file__).resolve().parents[1]
id='swebench-bpmn-1638'
candidate=root/'data/runtime/m3/standard-submission-v5'/id/'1'
check=(candidate/'check.js').read_bytes()
trace_bytes=(candidate/'repair-trace.json').read_bytes()
trace=json.loads(trace_bytes)
fix=trace['structured_response']
assert fix['edits'][0]['path']=='/workspace/lib/features/label-editing/cmd/UpdateLabelHandler.js'
_,tasks=public_tasks(root,root/'evals/frozen-m0.json')
task=next(t for t in tasks if t['id']==id)
work=root/'data/runtime/interface-replay/source-path-alias'
work.mkdir(parents=True,exist_ok=False)
with sandbox(task['image'],task['base_commit']) as backend:
    files=apply_edits(backend,fix['edits'])
pre=observe(task['image'],task['base_commit'],check,work/'pre')
post=observe(task['image'],task['base_commit'],check,work/'post',source_files=files)
annotation=json.loads((root/'evals/annotations'/f'{id}.json').read_text())
row=json.loads((root/annotation['source']['row_path']).read_text())
native=observe(task['image'],task['base_commit'],check,work/'native',source_files=files,native_test_patch=row['test_patch'].encode())
original=json.loads((candidate/'pre/observation.json').read_text())
canonical=root/'data/runtime/m3/standard-submission-v5'/id/'2/source'
identical=all((canonical/path).read_bytes()==content for path,content in files.items())
passed=bool(verified_check(pre,post) and identical and pre['check_sha256']==original['check_sha256']
            and native['complete'] and native['exit_code']==0 and not native['errors']
            and native['total']==1779 and native['skipped']==7
            and all(r.get('skipped') or r.get('success') for r in native['results']))
report={'passed':passed,'generation_requests':0,'original_benchmark_status_unchanged':True,
        'captured_fix_trace_sha256':digest(trace_bytes),'check_sha256':digest(check),
        'source_files_sha256':{path:digest(data) for path,data in files.items()},
        'identical_to_independently_verified_candidate2_source':identical,
        'pre':pre,'post':post,'native':{k:native[k] for k in ('complete','exit_code','total','skipped','errors')},
        'scope':'Interface replay only, no new candidate, no change to frozen evaluation score and no new task export'}
out=root/'notes/runs/source-path-alias-replay.json';out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('pre','post')},indent=2))
raise SystemExit(0 if passed else 1)

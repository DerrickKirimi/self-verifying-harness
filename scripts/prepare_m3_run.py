"""Create a prospective all-case run without a model request or discarded cases."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import re
from svh.extract import public_tasks
from svh.budget import Budget
p=argparse.ArgumentParser();p.add_argument('--run-name',required=True);p.add_argument('--method',type=Path,required=True)
a=p.parse_args();root=Path(__file__).resolve().parents[1]
if not re.fullmatch('[A-Za-z0-9_-]{1,64}',a.run_name):raise SystemExit('Invalid run name')
lock=(root/'data/runtime/m3/worker.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
identity,tasks=public_tasks(root,root/'evals/frozen-m0.json')
method_bytes=(root/a.method).read_bytes();method=json.loads(method_bytes)
if method['corpus_sha256']!=identity:raise SystemExit('Different corpus')
work=root/'data/runtime/m3'/a.run_name;work.mkdir(exist_ok=False)
report={'corpus_sha256':identity,'method':str(a.method),'method_sha256':hashlib.sha256(method_bytes).hexdigest(),
        'budget':Budget(root/'data/runtime/gemini-budget.sqlite','4.00').summary(),
        'cases':[{'id':t['id'],'status':'not_attempted','candidates':[]} for t in tasks]}
(work/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'run':a.run_name,'cases':len(tasks),'model':method['model']}))

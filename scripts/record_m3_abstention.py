"""Keep an unactionable requirement in the denominator without inventing a policy."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--run-directory',type=Path,required=True);p.add_argument('--id',required=True);p.add_argument('--reason',required=True)
a=p.parse_args();root=Path(__file__).resolve().parents[1]
lock=(root/'data/runtime/m3/worker.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
report_path=root/a.run_directory/'report.json';report=json.loads(report_path.read_text())
case=next(c for c in report['cases'] if c['id']==a.id)
if case['status']!='not_attempted' or case['candidates']:raise SystemExit('Do not overwrite an attempted case')
source=root/'notes/runs/m2-checkpoints-media.json';data=json.loads(source.read_text())
checkpoint=next(c for c in data['cases'] if c['id']==a.id)
if not checkpoint.get('questions'):raise SystemExit('No recorded clarification supports abstention')
case.update(status='abstained',stage='requirement_review',reason=a.reason,
            review='Codex AI controller; no human response assumed',source_checkpoint_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),questions=checkpoint['questions'])
tmp=report_path.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(report_path)
print(json.dumps({'id':a.id,'status':'abstained','denominator_retained':True}))

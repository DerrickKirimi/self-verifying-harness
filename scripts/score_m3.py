"""Recompute M3 from unchanged local artifacts; missing attempts never disappear."""
import argparse
import json
from pathlib import Path
from svh.corpus import load_frozen_corpus
from svh.verification import digest, score

p=argparse.ArgumentParser()
p.add_argument('--run-directory',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
root=Path(__file__).resolve().parents[1]
manifest,annotations=load_frozen_corpus(root,root/'evals/frozen-m0.json')
run=root/a.run_directory
report=json.loads((run/'report.json').read_text())
rubric=json.loads((root/'evals/m3-rubric.json').read_text())
if report['corpus_sha256']!=manifest['corpus_sha256'] or rubric['corpus_sha256']!=manifest['corpus_sha256']:
    raise SystemExit('Different evaluation corpus')
for case in report['cases']:
    if case['id'] not in {x['id'] for x in annotations}:raise ValueError('Unknown case')
    for c in case['candidates']:
        directory=run/case['id']/str(c['number'])
        if 'pre' not in c:continue
        if digest((directory/'check.js').read_bytes())!=c['pre']['check_sha256']:raise ValueError('Frozen check changed')
        for side in ['pre','post']:
            if side not in c:continue
            observed=json.loads((directory/side/'observation.json').read_text())
            if observed!=c[side]:raise ValueError('Report differs from retained observation')
            if digest((directory/side/'console.log').read_bytes())!=observed['console_sha256']:
                raise ValueError('Browser console changed')
            raw_path=directory/side/'browser.json'
            if raw_path.exists():
                raw=json.loads(raw_path.read_text())
                if any(observed.get(k)!=v for k,v in raw.items()):raise ValueError('Browser result changed')
            elif observed.get('complete'):
                raise ValueError('Completed observation lost its browser result')
        review_path=directory/'alignment-review.json'
        if review_path.exists():
            review=json.loads(review_path.read_text())
            if c.get('alignment_review') and review!=c['alignment_review']:raise ValueError('Alignment review changed after repair')
            c['alignment_review']=review
        if 'post' in c:
            for path,sha in c['post']['source_files_sha256'].items():
                from svh.browser_runner import allowed_source
                allowed_source({path:b''})
                if digest((directory/'source'/path).read_bytes())!=sha:raise ValueError('Generated source changed')
        if c.get('native_regressions_passed'):
            if digest((directory/'native/observation.json').read_bytes())!=c['native_observation_sha256']:
                raise ValueError('Native regression proof changed')
result=score(report['cases'],rubric,[x['id'] for x in annotations])
result.update(corpus_sha256=manifest['corpus_sha256'],run_report_sha256=digest((run/'report.json').read_bytes()),
              budget=report['budget'],scope='Development run; AI-assisted claim alignment, not independent human scoring; Harbor integrity scored separately')
out=root/a.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

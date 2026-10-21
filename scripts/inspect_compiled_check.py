"""Capture loaded browser source for a frozen check's ambiguous webpack stack."""
import argparse
import json
import re
from pathlib import Path
from svh.browser_runner import CONFIG, REPORTER, CHECK_PATH
from svh.docker_backend import sandbox
from svh.verification import digest

CAPTURE=r'''
const fs=require('fs');
const puppeteer=require('/testbed/node_modules/puppeteer');
(async()=>{
  const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:9222'});
  try {
    for (const page of await browser.pages()) {
      const session=await page.target().createCDPSession();
      const ids=[],urls=[];
      session.on('Debugger.scriptParsed',s=>{
        urls.push(s.url);
        if(s.url.includes('SvhGeneratedSpec')) ids.push(s.scriptId);
      });
      await session.send('Debugger.enable');
      await new Promise(resolve=>setTimeout(resolve,200));
      fs.writeFileSync('/tmp/svh-script-urls.json',JSON.stringify(urls));
      for (const id of ids) {
        const source=await session.send('Debugger.getScriptSource',{scriptId:id});
        fs.writeFileSync('/tmp/svh-loaded-check.js',source.scriptSource);
      }
      await session.detach();
    }
  } finally {await browser.disconnect();}
  if(!fs.existsSync('/tmp/svh-loaded-check.js'))throw new Error('Loaded check source not found');
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
'''
p=argparse.ArgumentParser()
p.add_argument('--candidate-directory',type=Path,required=True)
p.add_argument('--name',default='stack-diagnostic')
a=p.parse_args()
case=a.candidate_directory.resolve()
pre=json.loads((case/'pre/observation.json').read_text())
check=(case/'check.js').read_bytes()
if digest(check)!=pre['check_sha256']:raise ValueError('Frozen check changed')
if not a.name.replace('-','').isalnum() or len(a.name)>64:raise ValueError('Invalid diagnostic name')
out=case/a.name;out.mkdir(exist_ok=False)
hook="""this.onSpecComplete=function(browser,result){
    if (!fs.existsSync('/tmp/svh-loaded-check.js')) {
      try {require('child_process').execFileSync('node',['/tmp/svh-capture.cjs'],{timeout:20000});}
      catch(error) {fs.writeFileSync('/tmp/svh-capture-error.txt',String(error.stderr));}
    }
"""
reporter=REPORTER.replace('this.onSpecComplete=function(browser,result){',hook)
config=CONFIG.replace("flags:['--no-sandbox'", "flags:['--remote-debugging-port=9222','--no-sandbox'")
config=config.replace('config.singleRun=true;', 'config.client=Object.assign({},config.client,{clearContext:false}); config.singleRun=true;')
with sandbox(pre['image'],pre['base_commit']) as backend:
    staged=[('/workspace/'+CHECK_PATH,check),('/tmp/svh-karma.cjs',config.encode()),
            ('/tmp/svh-reporter.cjs',reporter.encode()),('/tmp/svh-capture.cjs',CAPTURE.encode())]
    if any(x.error for x in backend.upload_files(staged)):raise ValueError('Could not stage diagnostic')
    run=backend.execute("su chromeuser -c './node_modules/.bin/karma start /tmp/svh-karma.cjs --no-colors'",timeout=300)
    (out/'console.log').write_text(run.output)
    rows=backend.download_files(['/tmp/svh-loaded-check.js','/tmp/svh-results.json','/workspace/'+CHECK_PATH])
    urls=backend.download_files(['/tmp/svh-script-urls.json','/tmp/svh-capture-error.txt'])
    for name,row in zip(('script-urls.json','capture-error.txt'),urls):
        if row.content is not None:(out/name).write_bytes(row.content)
    if any(x.error or x.content is None for x in rows):raise ValueError('Diagnostic source/result unavailable')
    if rows[2].content!=check:raise ValueError('Frozen check changed during diagnostic')
    (out/'loaded-check.js').write_bytes(rows[0].content)
    (out/'browser.json').write_bytes(rows[1].content)
proof={'scope':'Trusted CDP source capture, not a new generated candidate or fail/pass claim',
       'check_sha256':digest(check),'loaded_source_sha256':digest(rows[0].content),
       'diagnostic_config_sha256':digest(config.encode()),
       'diagnostic_reporter_sha256':digest(reporter.encode()),'exit_code':run.exit_code,
       'source_archive_sha256':backend.source_archive_sha256}
(out/'identity.json').write_text(json.dumps(proof,indent=2)+'\n')
lines=rows[0].content.decode().splitlines()
print(json.dumps(proof))
stack_lines=sorted({int(line) for result in pre.get('results',[]) for log in result.get('log',[])
                    for line in re.findall(r'SvhGeneratedSpec\.js:(\d+):',log)})
for line in stack_lines:
    print(json.dumps({'stack_line':line,'loaded_source':lines[line-1] if len(lines)>=line else None}))

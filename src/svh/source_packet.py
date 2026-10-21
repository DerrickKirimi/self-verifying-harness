"""Bounded retrieval of existing buggy source and nearby base specs/fixtures."""
import json
import re
import shlex
from pathlib import PurePosixPath

SCRIPT=r'''
import json,pathlib,re,sys
root=pathlib.Path('/workspace');paths=json.loads(sys.argv[1]);packet=[];budget=42000
def add(path,limit,line=None,tail=False):
    global budget
    if path.is_symlink() or not path.resolve().is_relative_to(root) or not path.is_file():return
    content=path.read_text(errors='replace')
    if line:
        lines=content.splitlines();start=max(0,line-90);text='\n'.join(lines[start:line+90]);offset=start+1
    elif tail:
        text=content[-limit:];offset=content[:max(0,len(content)-limit)].count('\n')+1
    else:text=content;offset=1
    text=text[:min(limit,budget)];budget-=len(text)
    if text:packet.append({'path':str(path),'first_line':offset,'content':text,'truncated':len(text)<len(content)})
    return content
specs=sorted((root/'test/spec').rglob('*Spec.js'))
for item in paths:
    path=root/item['path'];add(path,10000,item['line'])
    stem=re.sub(r'(Handler|Behavior|Provider)$','',path.stem).lower()
    matched=[p for p in specs if stem in p.stem.lower()]
    for spec in matched[:2]:
        if budget<3000:break
        text=add(spec,10000)
        if not text:continue
        if len(text)>10000 and budget>6000:add(spec,6000,tail=True)
        for relative in re.findall(r"require\(['\"]([^'\"]+\.bpmn)['\"]\)",text)[:3]:
            fixture=(spec.parent/relative).resolve() if relative.startswith('.') else (root/relative).resolve()
            if budget<1000:break
            add(fixture,8000)
print(json.dumps(packet))
'''


def source_packet(backend, claim):
    paths=[]
    for citation in claim.get('code_evidence',[])[:2]:
        path=PurePosixPath(citation['path'])
        if not str(path).startswith('/workspace/lib/') or '..' in path.parts:
            raise ValueError('Source retrieval requires a permitted checkpoint citation')
        paths.append({'path':str(path.relative_to('/workspace')),'line':citation['line']})
    result=backend.execute('python3 -I -c '+shlex.quote(SCRIPT)+' '+shlex.quote(json.dumps(paths)),timeout=30)
    if result.exit_code != 0 or result.truncated:raise ValueError('Could not retrieve bounded base source packet')
    return json.loads(result.output)

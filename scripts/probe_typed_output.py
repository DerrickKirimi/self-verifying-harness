"""Small paid integration diagnostic; never a generated software proof."""
import json
import argparse
from pathlib import Path
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
from langsmith import tracing_context
from svh.gemini import configured_model
from svh.generation import CheckCandidate
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--with-history',action='store_true');args=parser.parse_args()
model=configured_model(root,name='gemini-3.8-flash',output_cap=2048);model.reasoning_effort='low'
messages=[HumanMessage(content='Integration probe only. Return CheckCandidate with check_javascript="describe(\'probe\',function(){it(\'works\',function(){expect(true).to.equal(true);});});", requirement="probe behavior", rationale="integration test", visible_assertions=["true equals true"], uncertainty=null. Do not use empty strings.')]
for n in range(3 if args.with_history else 0):
 messages.extend([AIMessage(content='',tool_calls=[{'name':'read_file','args':{'file_path':'/workspace/probe.js'},'id':'probe-'+str(n)}]),ToolMessage(content='Probe behavior: true equals true',name='read_file',tool_call_id='probe-'+str(n))])
messages.append(HumanMessage(content='The inspection budget is exhausted; return the exact requested nonempty CheckCandidate now.'))
with tracing_context(enabled=False):
 response=model.bind_tools([CheckCandidate],tool_choice='any').invoke(messages)
report={'scope':'Synthetic final-tool transport diagnostic only; not a recording reproduction','tool_calls':response.tool_calls,'usage':response.usage_metadata,'finish':response.response_metadata.get('finish_reason'),'budget':model._budget.summary()}
(root/('notes/runs/m3-typed-output-history-probe.json' if args.with_history else 'notes/runs/m3-typed-output-probe.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

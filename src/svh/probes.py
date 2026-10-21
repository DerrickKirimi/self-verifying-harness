"""Bounded test development on fresh buggy source; the SDK owns iteration."""
import asyncio
import json
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from svh.browser_runner import observe
from svh.verification import digest, browser_verdict


def recorded_check_digests(case_directory):
    known=set()
    for stage in ('1','2'):
        directory=case_directory/stage
        for path in [directory/'check.js',*directory.glob('development-probes/probe-*/check.js')]:
            if path.is_file() and path.stat().st_size:
                known.add(digest(path.read_bytes()))
    return known


def require_candidate_capacity(case_directory, maximum=2):
    """Do not fund a new generation stage when no distinct version remains."""
    if len(recorded_check_digests(case_directory)) >= maximum:
        raise ValueError('Two distinct frozen check versions already exist; no new candidate generation is allowed')


def check_version_budget(case_directory, check, maximum=2):
    known=recorded_check_digests(case_directory)
    if digest(check) not in known and len(known)>=maximum:
        raise ValueError('Two distinct frozen check versions already exist for this case')


class ProbeInput(BaseModel):
    check_javascript: str = Field(min_length=1,max_length=128*1024,
        description='Complete reported-behavior reproduction: establish initial state, perform the reported action and assert the correct outcome. Never a setup smoke or console-only diagnostic.')


class ProbeRegistry:
    def __init__(self, task, stage_directory):
        self.task,self.directory=task,stage_directory
        self.records={}

    async def run(self, check_javascript):
        check=check_javascript.encode()
        for ref,row in self.records.items():
            if row['sha256']==digest(check):return self.response(ref,row)
        check_version_budget(self.directory.parent,check)
        if len(self.records)>=2:raise ValueError('Development probe budget exhausted')
        ref='probe-'+str(len(self.records)+1)
        directory=self.directory/'development-probes'/ref;directory.mkdir(parents=True,exist_ok=False)
        (directory/'check.js').write_bytes(check)
        result=await asyncio.to_thread(observe,self.task['image'],self.task['base_commit'],check,directory/'execution')
        row={'sha256':digest(check),'check':check,'observation':result}
        self.records[ref]=row
        if len(self.records)==2 and not any(browser_verdict(r['observation'],assertion_failure=True) for r in self.records.values()):
            raise ValueError('Two frozen development checks yielded no completed assertion failure')
        return self.response(ref,row)

    @staticmethod
    def response(ref,row):
        observed=row['observation']
        compact={k:observed.get(k) for k in ['complete','browser','errors','total','skipped','exit_code']}
        compact['results']=observed.get('results',[])[:8]
        text=json.dumps({'check_ref':ref,'sha256':row['sha256'],'observation':compact,
                         'assertion_failure':browser_verdict(observed,assertion_failure=True),
                         'instruction':'Correct setup/runtime mistakes. An initial-state assertion failure is not the reported bug. If the actual target assertion failed, return CheckSubmission referencing this check_ref; do not change its bytes.'})[:16000]
        return text,{'development_browser':observed,'check_ref':ref,'check_sha256':row['sha256']}

    def tool(self):
        return StructuredTool.from_function(coroutine=self.run,name='submit_browser_reproduction',args_schema=ProbeInput,
            description='Submit a COMPLETE reproduction of the reported bug with corrective assertions, on fresh BUGGY source in Docker. Every executed script consumes one of only TWO distinct versions for the entire case. Never submit setup smokes, DOM dumps or unrelated checks. Returns actual errors/assertions and never applies a fix.',
            response_format='content_and_artifact')

    def selected(self, ref):
        row=self.records.get(ref)
        if row is None or not browser_verdict(row['observation'],assertion_failure=True):
            raise ValueError('Final submission must reference an actually observed frozen assertion failure')
        return row['check']

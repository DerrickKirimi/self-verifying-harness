"""Controller-owned Karma/Chrome runner. Generated code is staged only in Docker."""
import json
from pathlib import PurePosixPath

from svh.docker_backend import sandbox
from svh.verification import digest

CHECK_PATH = 'test/SvhGeneratedSpec.js'

CONFIG = r'''module.exports = function(karma) {
  const set = karma.set.bind(karma);
  require('/workspace/test/config/karma.unit.js')({set: function(config) {
    process.env.CHROME_BIN='/usr/bin/google-chrome-stable';
    config.basePath='/workspace';
    if (!process.env.SVH_NATIVE) {
      config.files=['node_modules/promise-polyfill/dist/polyfill.js','test/SvhGeneratedSpec.js'];
      config.preprocessors={'test/SvhGeneratedSpec.js':['webpack','env']};
    }
    config.browsers=['SvhChrome'];
    config.customLaunchers={SvhChrome:{base:'ChromeHeadless',flags:['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage']}};
    config.singleRun=true; config.autoWatch=false;
    config.reporters=['svh'];
    config.plugins=['karma-*',{'reporter:svh':['type',require('/tmp/svh-reporter.cjs')]}];
    set(config);
  }});
};'''

REPORTER = r'''const fs = require('fs');
function Reporter() {
  const report={complete:false,errors:[],results:[],browser:null,disconnected:false,total:0,skipped:0};
  this.onBrowserStart=function(browser){report.browser=browser.name;};
  this.onBrowserError=function(browser,error){report.errors.push(String(error));};
  this.onBrowserComplete=function(browser){if(browser.lastResult && browser.lastResult.disconnected) report.disconnected=true;};
  this.onSpecComplete=function(browser,result){
    report.results.push({name:result.suite.concat([result.description]).join(' '),success:result.success,skipped:result.skipped,log:result.log});
    report.total++;if(result.skipped)report.skipped++;
  };
  this.onRunComplete=function(){report.complete=true;fs.writeFileSync('/tmp/svh-results.json',JSON.stringify(report));};
}
module.exports=Reporter;'''


def allowed_source(files):
    """Transfer only regular source-file contents; mutable agent git state is irrelevant."""
    if not files or len(files) > 32:
        raise ValueError('A bounded nonempty source fix is required')
    for path, content in files.items():
        p=PurePosixPath(path)
        if (not path.startswith('lib/') or p.suffix != '.js' or '..' in p.parts
                or p.is_absolute() or str(p) != path or not isinstance(content, bytes) or len(content)>1024**2):
            raise ValueError('Fixes may contain only bounded lib JavaScript file bytes')


def observe(image, base_commit, check, directory, *, source_files=None, native_test_patch=None, native=False):
    """Fresh sandbox for each observation; no model has access to the reporter."""
    directory.mkdir(parents=True, exist_ok=False)
    if not isinstance(check, bytes) or not 1 <= len(check) <= 128*1024:
        raise ValueError('A frozen bounded JavaScript check is required')
    if source_files is not None:
        allowed_source(source_files)
    with sandbox(image,base_commit) as backend:
        baseline=backend.source_fingerprint()
        files=[('/workspace/'+CHECK_PATH,check),('/tmp/svh-karma.cjs',CONFIG.encode()),('/tmp/svh-reporter.cjs',REPORTER.encode())]
        files += [('/workspace/'+path,content) for path,content in (source_files or {}).items()]
        if native_test_patch is not None:
            files.append(('/tmp/svh-native.diff',native_test_patch))
        if any(r.error for r in backend.upload_files(files)):
            raise ValueError('Could not stage frozen verification inputs')
        if native_test_patch is not None:
            applied=backend.execute('git apply --check /tmp/svh-native.diff && git apply /tmp/svh-native.diff')
            if applied.exit_code != 0:
                raise ValueError('Held-out native test patch does not apply')
        command=('SVH_NATIVE=1 ' if native or native_test_patch is not None else '') + "su chromeuser -c './node_modules/.bin/karma start /tmp/svh-karma.cjs --no-colors'"
        run=backend.execute(command,timeout=300)
        (directory/'console.log').write_text(run.output)
        downloaded=[] if backend.closed else backend.download_files(['/tmp/svh-results.json','/workspace/'+CHECK_PATH])
        if len(downloaded)!=2 or any(r.error or r.content is None for r in downloaded):
            result={'complete':False,'errors':['runner result unavailable'],'results':[]}
        else:
            if downloaded[1].content != check:
                raise ValueError('Frozen check changed during verification')
            (directory/'browser.json').write_bytes(downloaded[0].content)
            result=json.loads(downloaded[0].content)
        result.update(exit_code=run.exit_code,timed_out=run.exit_code is None,
            check_sha256=digest(check),image=image,base_commit=base_commit,
            source_is_base=source_files is None,source_archive_sha256=backend.source_archive_sha256,
            baseline_fingerprint=baseline,source_files_sha256={p:digest(b) for p,b in (source_files or {}).items()},
            runner_sha256=digest((CONFIG+REPORTER).encode()),console_sha256=digest(run.output.encode()))
        (directory/'observation.json').write_text(json.dumps(result,indent=2)+'\n')
        return result

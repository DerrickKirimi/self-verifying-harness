const fs = require('fs');
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
module.exports=Reporter;
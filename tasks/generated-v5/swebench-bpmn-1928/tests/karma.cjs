module.exports = function(karma) {
  process.env.PUPPETEER_EXECUTABLE_PATH='/usr/bin/google-chrome-stable';
  process.env.CHROME_BIN='/usr/bin/google-chrome-stable';
  const set = karma.set.bind(karma);
  require('/workspace/test/config/karma.unit.js')({set: function(config) {
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
};
// Probe the CoreImage blur path that iconservicesagent aborts in (MPSImageUnaryKernel.mm line 335 on the tablet).
// Run on the tablet: osascript -l JavaScript tablet-ci-blur-probe.js [sigma ...]
// A Metal assertion (MTLReportFailure) prints its full text to this process's stderr, which the system log redacts.
// Environment: CI_ENABLE_METAL_GPU / FORCE_SOFTWARE_RENDERER are passed through to CoreImage as given;
// PROBE_SOFTWARE=1 creates every context with kCIContextUseSoftwareRenderer (CoreImage's CPU renderer).
// The input is a checkerboard (a solid colour blurs to itself and may never reach the blur kernel); every sigma is tried
// at 128, 512 and 1024 px, in a fresh context each time, so the first failing size and sigma are the last lines printed.
ObjC.import('Foundation');
ObjC.import('CoreImage');

function envValue(name) {
  const value = $.NSProcessInfo.processInfo.environment.objectForKey(name);
  return value.isNil() ? '(unset)' : ObjC.unwrap(value);
}

function makeContext() {
  if (envValue('PROBE_SOFTWARE') !== '1') return $.CIContext.contextWithOptions($());
  const key = (typeof $.kCIContextUseSoftwareRenderer !== 'undefined') ? $.kCIContextUseSoftwareRenderer : 'software_renderer';
  const options = $.NSDictionary.dictionaryWithObjectForKey($.NSNumber.numberWithBool(true), key);
  return $.CIContext.contextWithOptions(options);
}

function render(sigma, size) {
  const ctx = makeContext();
  if (ctx.isNil()) { console.log('render sigma=' + sigma + ' size=' + size + ': no context'); return; }
  const rect = $.NSMakeRect(0, 0, size, size);
  const checker = $.CIFilter.filterWithName('CICheckerboardGenerator');
  checker.setValueForKey($.NSNumber.numberWithDouble(size / 16), 'inputWidth');
  const image = checker.valueForKey('outputImage').imageByCroppingToRect(rect);
  const blurred = image.imageByApplyingGaussianBlurWithSigma(sigma).imageByCroppingToRect(rect);
  console.log('render sigma=' + sigma + ' size=' + size);
  const cg = ctx.createCGImageFromRect(blurred, rect);
  console.log(cg ? '  ok' : '  render returned nil');
}

function run(argv) {
  const sigmas = argv.length > 0 ? argv.map(parseFloat) : [2, 8, 20, 50];
  console.log('CI_ENABLE_METAL_GPU=' + envValue('CI_ENABLE_METAL_GPU') + ' FORCE_SOFTWARE_RENDERER=' +
              envValue('FORCE_SOFTWARE_RENDERER') + ' PROBE_SOFTWARE=' + envValue('PROBE_SOFTWARE'));
  const first = makeContext();
  console.log('context: ' + (first.isNil() ? '(nil)' : ObjC.unwrap(first.description).split('\n')[0]));
  for (const sigma of sigmas) {
    for (const size of [128, 512, 1024]) render(sigma, size);
  }
  return 'done';
}

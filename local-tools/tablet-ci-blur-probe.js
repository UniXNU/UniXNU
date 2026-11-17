// Render checkerboard Gaussian blurs at 128, 512 and 1024 pixels.
// Run: osascript -l JavaScript tablet-ci-blur-probe.js [sigma ...]
// PROBE_SOFTWARE=1 selects the Core Image software renderer.
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

// Request application icons at several sizes and create their bitmaps.
// Run: osascript -l JavaScript tablet-icon-stress.js [rounds]
ObjC.import('AppKit');

function apps(dir) {
  const fm = $.NSFileManager.defaultManager;
  const names = fm.contentsOfDirectoryAtPathError(dir, $());
  const out = [];
  if (names.isNil()) return out;
  for (let i = 0; i < names.count; i++) {
    const name = ObjC.unwrap(names.objectAtIndex(i));
    if (name.endsWith('.app')) out.push(dir + '/' + name);
  }
  return out;
}

function run(argv) {
  const rounds = argv.length > 0 ? parseInt(argv[0], 10) : 3;
  const ws = $.NSWorkspace.sharedWorkspace;
  const paths = apps('/System/Applications').concat(apps('/System/Applications/Utilities'), apps('/Applications'));
  const sizes = [16, 32, 64, 128, 256, 512];
  let made = 0, failed = 0;
  const start = Date.now();
  for (let r = 0; r < rounds; r++) {
    for (const p of paths) {
      const icon = ws.iconForFile(p);
      for (const s of sizes) {
        icon.size = $.NSMakeSize(s, s);
        const cg = icon.CGImageForProposedRectContextHints($(), $(), $());   // nil rect: the image's size just set
        if (cg) made++; else failed++;
      }
    }
    console.log('round ' + (r + 1) + ': ' + paths.length + ' apps, ' + made + ' bitmaps, ' + failed + ' failed, ' +
                ((Date.now() - start) / 1000).toFixed(1) + ' s');
  }
  return 'done';
}

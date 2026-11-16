// Sample window-system pointer coordinates every 5 ms and report movement intervals.
// Run: osascript -l JavaScript tablet-pointer-probe.js [seconds] [threshold_px] [csv_path] [wait_seconds]
// The CSV stores milliseconds from the first movement, x and y.
ObjC.import('AppKit');
ObjC.import('Foundation');

function percentile(sorted, q) {
  if (sorted.length === 0) return 0;
  return sorted[Math.min(sorted.length - 1, Math.floor(q * sorted.length))];
}

function run(argv) {
  const seconds = argv.length > 0 ? parseFloat(argv[0]) : 30;
  const threshold = argv.length > 1 ? parseFloat(argv[1]) : 40;
  const csvPath = argv.length > 2 ? argv[2] : '';
  const waitSeconds = argv.length > 3 ? parseFloat(argv[3]) : 300;

  let p = $.NSEvent.mouseLocation;
  let last = {x: p.x, y: p.y, t: Date.now()};
  const waitEnd = Date.now() + waitSeconds * 1000;
  while (Date.now() < waitEnd) {
    p = $.NSEvent.mouseLocation;
    if (p.x !== last.x || p.y !== last.y) break;
    $.NSThread.sleepForTimeInterval(0.005);
  }
  if (p.x === last.x && p.y === last.y) {
    if (csvPath) $('0,' + last.x.toFixed(1) + ',' + last.y.toFixed(1) + '\n')
      .writeToFileAtomicallyEncodingError(csvPath, true, $.NSUTF8StringEncoding, $());
    console.log('no movement in ' + waitSeconds + ' s');
    return 'done';
  }

  const start = Date.now();
  const end = start + seconds * 1000;
  const rows = ['0,' + last.x.toFixed(1) + ',' + last.y.toFixed(1)];
  const gaps = [], steps = [], big = [];
  let samples = 0, path = 0, lastChange = start;
  last = {x: last.x, y: last.y, t: start};
  while (Date.now() < end) {
    p = $.NSEvent.mouseLocation;
    const now = Date.now();
    samples++;
    const dx = p.x - last.x, dy = p.y - last.y, d = Math.sqrt(dx * dx + dy * dy);
    if (d > 0) {
      const gap = now - lastChange;
      if (gap < 250) gaps.push(gap);          // a longer gap is the finger resting, not a report interval
      steps.push(d);
      path += d;
      rows.push((now - start) + ',' + p.x.toFixed(1) + ',' + p.y.toFixed(1));
      if (d > threshold && big.length < 40) big.push((now - start) + ' ms ' + last.x.toFixed(0) + ',' + last.y.toFixed(0) + ' -> ' +
                                                     p.x.toFixed(0) + ',' + p.y.toFixed(0) + ' (' + d.toFixed(0) + ' px)');
      lastChange = now;
      last = {x: p.x, y: p.y, t: now};
    }
    $.NSThread.sleepForTimeInterval(0.005);
  }
  if (csvPath) $(rows.join('\n') + '\n').writeToFileAtomicallyEncodingError(csvPath, true, $.NSUTF8StringEncoding, $());
  gaps.sort((a, b) => a - b);
  const sortedSteps = steps.slice().sort((a, b) => a - b);
  console.log('samples ' + samples + ' over ' + seconds + ' s, position changes ' + steps.length + ', path ' + path.toFixed(0) + ' px');
  console.log('gap between changes (ms, under 250): median ' + percentile(gaps, 0.5) + ', p90 ' + percentile(gaps, 0.9) +
              ', max ' + percentile(gaps, 1));
  console.log('step (px): median ' + percentile(sortedSteps, 0.5).toFixed(1) + ', p90 ' + percentile(sortedSteps, 0.9).toFixed(1) +
              ', max ' + percentile(sortedSteps, 1).toFixed(1) + '; steps over ' + threshold + ' px: ' +
              steps.filter(s => s > threshold).length);
  for (const line of big) console.log('  ' + line);
  return 'done';
}

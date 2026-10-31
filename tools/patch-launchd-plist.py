#!/usr/bin/env python3
"""Make selected launchd jobs log to the console (SWEET bring-up debugging).

  patch-launchd-plist.py IN.plist OUT.plist [LABEL ...] [--remove LABEL ...]
                         [--add KEY=JOB.plist ...]

IN is /System/Library/xpc/launchd.plist (binary plist, read by launchd when
booted with launchd_unsecure_cache=1). For every job whose Label is given,
stdout/stderr go to /dev/console (mode 0622, writable by the mobile user)
and the environment asks Apple's frameworks to mirror their logs there:
OS_ACTIVITY_DT_MODE=YES copies os_log to stderr (as under Xcode),
CFLOG_FORCE_STDERR=1 does the same for CFLog/NSLog. Uncaught exception
reasons and the frameworks' own error messages then show on screen.

Every job's _PanicOnCrash key is also renamed (_PanicOnCrasX), so a crashing
daemon does not panic the system during bring-up.

Jobs named after --remove are dropped from the cache altogether: launchd
then never registers their MachServices, so a lookup fails at once instead
of queueing on a port whose daemon cannot run (umi: com.apple.fairplayd.H2).

--add puts a job back: KEY is its path on the phone (the cache's key, e.g.
/System/Library/LaunchDaemons/com.apple.CommCenter-noncellular.plist), JOB
the LaunchDaemon plist itself (umi: CommCenter, removed in image v13).
"""
import plistlib, sys

LOG_ENV = {'OS_ACTIVITY_DT_MODE': 'YES', 'CFLOG_FORCE_STDERR': '1'}


def main():
    src, dst, args = sys.argv[1], sys.argv[2], sys.argv[3:]
    opts = {'--remove': [], '--add': []}
    labels, cur = set(), None
    for a in args:
        if a in opts:
            cur = opts[a]
        elif cur is None:
            labels.add(a)
        else:
            cur.append(a)
    remove = set(opts['--remove'])
    with open(src, 'rb') as f:
        plist = plistlib.load(f)
    daemons = plist['LaunchDaemons']
    removed = {k: daemons[k]['Label'] for k in daemons if daemons[k].get('Label') in remove}
    for key in removed:
        del daemons[key]
    added = []
    for spec in opts['--add']:
        key, path = spec.split('=', 1)
        if key in daemons:
            sys.exit(f'{key} is already in {src}')
        with open(path, 'rb') as f:
            daemons[key] = plistlib.load(f)
        added.append((key, daemons[key]['Label']))
    found = set()
    for job in daemons.values():
        if '_PanicOnCrash' in job:
            job['_PanicOnCrasX'] = job.pop('_PanicOnCrash')
        label = job.get('Label')
        if label in labels:
            job['StandardOutPath'] = '/dev/console'
            job['StandardErrorPath'] = '/dev/console'
            job.setdefault('EnvironmentVariables', {}).update(LOG_ENV)
            found.add(label)
    missing = (labels - found) | (remove - set(removed.values()))
    if missing:
        sys.exit(f'jobs not found: {", ".join(sorted(missing))}')
    with open(dst, 'wb') as f:
        plistlib.dump(plist, f, fmt=plistlib.FMT_BINARY)
    if found:
        print(f'{dst}: console logging for {", ".join(sorted(found))}')
    for key, label in sorted(removed.items()):
        print(f'{dst}: removed {label} ({key})')
    for key, label in added:
        print(f'{dst}: added {label} ({key})')


if __name__ == '__main__':
    main()

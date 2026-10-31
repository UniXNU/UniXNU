#!/usr/bin/env python3
"""Make selected launchd jobs log to the console (SWEET bring-up debugging).

  patch-launchd-plist.py IN.plist OUT.plist [LABEL ...] [--remove LABEL ...]

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
"""
import plistlib, sys

LOG_ENV = {'OS_ACTIVITY_DT_MODE': 'YES', 'CFLOG_FORCE_STDERR': '1'}


def main():
    src, dst, args = sys.argv[1], sys.argv[2], sys.argv[3:]
    remove = set()
    if '--remove' in args:
        i = args.index('--remove')
        args, remove = args[:i], set(args[i + 1:])
    labels = set(args)
    with open(src, 'rb') as f:
        plist = plistlib.load(f)
    daemons = plist['LaunchDaemons']
    removed = {k: daemons[k]['Label'] for k in daemons if daemons[k].get('Label') in remove}
    for key in removed:
        del daemons[key]
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


if __name__ == '__main__':
    main()

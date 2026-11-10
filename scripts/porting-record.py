#!/usr/bin/env python3
"""Validate device porting records and render them for the documentation site."""
import argparse
import fnmatch
from html import escape
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from urllib.parse import quote
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
AREAS = {
    'configuration': ('Configuration', '配置'),
    'firmware': ('Firmware and boot', '固件与启动'),
    'cpu': ('CPU and interrupts', 'CPU 与中断'),
    'memory': ('Memory and DMA', '内存与 DMA'),
    'storage': ('Storage and root', '存储与根卷'),
    'display': ('Display', '显示'),
    'input': ('Input', '输入'),
    'gpu': ('GPU', 'GPU'),
    'network': ('Network', '网络'),
    'audio': ('Audio', '音频'),
    'power': ('Power', '电源'),
    'packaging': ('Image assembly', '镜像组装'),
    'diagnostics': ('Diagnostics', '诊断'),
}
FIELDS = {
    'inputs': ('Hardware and dependencies', '硬件与依赖'),
    'configuration': ('Configuration', '配置'),
    'procedure': ('Procedure', '操作步骤'),
    'findings': ('Development findings', '开发经验'),
    'completion': ('Completion criteria', '完成条件'),
    'limits': ('Current limits', '当前范围'),
    'next_action': ('Next action', '下一步'),
}
STATES = {'planned', 'implemented', 'host-verified', 'device-verified', 'not-applicable'}


def git(device, *args):
    return subprocess.check_output(['git', '-C', str(device), *args], text=True).strip()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value):
    return isinstance(value, list) and bool(value) and all(text(item) for item in value)


def validate(record, board, label, allow_custom_components=False):
    need(record.get('schema_version') == 1, f'{label}: schema_version must be 1')
    info = record.get('device', {})
    for key in ('name', 'soc', 'os_profile', 'summary'):
        need(text(info.get(key)), f'{label}: device.{key} is required')
    for key in ('name', 'soc', 'os_profile'):
        need(info[key] == board.get('board', {}).get(key), f'{label}: device.{key} must match board.toml')
    areas = record.get('area', [])
    need(isinstance(areas, list), f'{label}: [[area]] is required')
    ids = [area.get('id') for area in areas]
    need(len(ids) == len(set(ids)), f'{label}: duplicate area ID')
    need(set(AREAS).issubset(ids), f'{label}: missing areas: {sorted(set(AREAS) - set(ids))}')
    selected = set(board.get('components', {}).get('include', []))
    catalog = {c['id']: c for c in tomllib.loads((ROOT / 'components.toml').read_text())['component']}
    pending = list(selected)
    while pending:
        component = pending.pop()
        need(component in catalog or allow_custom_components, f'{label}: unknown component {component}')
        for dependency in catalog.get(component, {}).get('dependencies', []):
            if dependency not in selected:
                selected.add(dependency)
                pending.append(dependency)
    covered = set()
    for area in areas:
        prefix = f'{label}/{area.get("id")}'
        need(re.fullmatch(r'[a-z][a-z0-9-]*', area.get('id', '')), f'{prefix}: invalid ID')
        need(area.get('status') in STATES, f'{prefix}: invalid status')
        for key in FIELDS:
            need(strings(area.get(key)), f'{prefix}: {key} requires concrete entries')
        need(strings(area.get('paths')), f'{prefix}: paths are required')
        for pattern in area['paths']:
            need(not pattern.startswith('/') and '..' not in Path(pattern).parts,
                 f'{prefix}: paths must be repository-relative')
        components = area.get('components')
        need(isinstance(components, list) and all(text(c) for c in components), f'{prefix}: components must be a list')
        need(all(re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', c) for c in components), f'{prefix}: invalid component ID')
        covered.update(components)
        evidence = area.get('evidence', [])
        need(isinstance(evidence, list), f'{prefix}: evidence must be a list')
        for item in evidence:
            need(item.get('kind') in ('source', 'host', 'device'), f'{prefix}: invalid evidence kind')
            need(text(item.get('reference')) and text(item.get('result')), f'{prefix}: evidence needs reference and result')
            ref = item['reference']
            need(ref.startswith('https://') or (not Path(ref).is_absolute() and '..' not in Path(ref).parts),
                 f'{prefix}: evidence must use HTTPS or a repository-relative path')
            if item['kind'] in ('host', 'device') or item.get('command'):
                need(text(item.get('command')), f'{prefix}: verification evidence needs a command')
                need(re.fullmatch(r'[0-9a-f]{40}', item.get('revision', '')), f'{prefix}: verification evidence needs a commit')
        if area['status'] == 'implemented':
            need(bool(evidence), f'{prefix}: implemented work needs evidence')
        if area['status'] in ('host-verified', 'device-verified'):
            kind = area['status'].split('-')[0]
            need(any(e['kind'] == kind for e in evidence), f'{prefix}: {kind} evidence is required')
        if area['status'] == 'not-applicable':
            need(not components, f'{prefix}: selected components require an active area')
    need(selected <= covered, f'{label}: components without an area: {sorted(selected - covered)}')
    return record


def check(device, base=None):
    record = tomllib.loads((device / 'porting.toml').read_text())
    board = tomllib.loads((device / 'board.toml').read_text())
    validate(record, board, str(device))
    for area in record['area']:
        for item in area['evidence']:
            if not item['reference'].startswith('https://'):
                need((device / item['reference']).is_file(), f'{area["id"]}: evidence file missing: {item["reference"]}')
    if base and set(base) != {'0'}:
        old_text = git(device, 'ls-tree', base, 'porting.toml')
        old = tomllib.loads(git(device, 'show', f'{base}:porting.toml')) if old_text else {}
        previous = {a['id']: a for a in old.get('area', [])}
        current = {a['id']: a for a in record['area']}
        changed = git(device, 'diff', '--name-only', '--no-renames', base, 'HEAD').splitlines()
        check_changes(previous, current, changed)
    print(f'{record["device"]["name"]}: {len(record["area"])} structured areas checked')
    return record


def check_changes(previous, current, changed):
    for path in changed:
        if path == 'porting.toml' or path.lower().endswith(('.md', '.rst')):
            continue
        owners = {key for key, area in current.items() if any(
            fnmatch.fnmatchcase(path, pattern) for pattern in area['paths'] + previous.get(key, {}).get('paths', []))}
        need(bool(owners), f'{path}: add its owner area and paths to porting.toml')
        for owner in owners:
            before = previous.get(owner, {})
            need(any(current[owner][key] != before.get(key) for key in ('findings', 'evidence')),
                 f'{path}: update {owner} findings or evidence with this change')

def markdown_text(value):
    """Render record prose as text in Markdown and Vue templates."""
    value = escape(value, quote=False).replace('{', '&#123;').replace('}', '&#125;')
    return re.sub(r'([\\`*\[\]()#!|_~])', r'\\\1', value).replace('\n', ' ').rstrip()


def render(record, repository, revision, zh=False):
    locale = int(zh)
    url = f'https://github.com/{repository}/blob/{revision}'
    lines = ['<div v-pre>', '', markdown_text(record['device']['summary']), '',
             ('源记录' if zh else 'Source record') + f': [porting.toml]({url}/porting.toml), `{revision}`.', '',
             ('本页按设备记录自动生成。' if zh else 'This page is generated from the device record.'), '',
             '| ' + ('部分 | 状态' if zh else 'Area | Status') + ' |', '| --- | --- |']
    for area in record['area']:
        title = AREAS.get(area['id'], (area['id'], area['id']))[locale]
        lines.append(f'| [{title}](#{area["id"]}) | `{area["status"]}` |')
    for area in record['area']:
        title = AREAS.get(area['id'], (area['id'], area['id']))[locale]
        lines += ['', f'## {title} {{#{area["id"]}}}', '', f'`{area["status"]}`', '']
        if area['components']:
            lines += [('组件' if zh else 'Components') + ': ' + ', '.join(f'`{c}`' for c in area['components']) + '.', '']
        for key, labels in FIELDS.items():
            lines += [f'### {labels[locale]}', ''] + ['- ' + markdown_text(entry) for entry in area[key]] + ['']
        lines += ['### ' + ('证据' if zh else 'Evidence'), '']
        for item in area['evidence']:
            ref = item['reference']
            link = ref if ref.startswith('https://') else f'{url}/{ref}'
            link = quote(link, safe='/:?&=+%~@#')
            lines += [f'- `{item["kind"]}`: [{markdown_text(item["result"])}]({link})']
            if item.get('command'):
                command = escape(item['command'], quote=False).replace('{', '&#123;').replace('}', '&#125;')
                lines += [f'  Command: <code>{command}</code>. Revision: `{item["revision"]}`.']
        if not area['evidence']:
            lines += [('按下一步操作收集证据。' if zh else 'Collect evidence using the next action.')]
    return '\n'.join(lines + ['', '</div>']) + '\n'


def site(overrides):
    local = dict(value.split('=', 1) for value in overrides)
    registry = tomllib.loads((ROOT / 'devices.toml').read_text())
    if registry.get('schema_version') == 2:
        import importlib.util
        spec = importlib.util.spec_from_file_location('device_catalog', ROOT / 'scripts/sync-devices.py')
        catalog = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(catalog)
        catalog.render_site(registry, local)
        return
    need(registry.get('schema_version') == 1, 'device registry schema_version must be 1')
    names = [entry['name'] for entry in registry.get('device', [])]
    need(len(names) == len(set(names)), 'duplicate registered device')
    output = ROOT / 'docs/.vitepress/records'
    output.mkdir(parents=True, exist_ok=True)
    for entry in registry['device']:
        name, repo, revision = entry['name'], entry['repository'], entry['revision']
        need(re.fullmatch(r'[a-z0-9-]+', name), 'invalid device name')
        need(re.fullmatch(r'UniXNU/[A-Za-z0-9_-]+', repo), f'{name}: official repository required')
        need(re.fullmatch(r'[0-9a-f]{40}', revision), f'{name}: pin a full commit')
        if name in local:
            path = Path(local[name])
            record = check(path)
        else:
            data = {}
            for filename in ('porting.toml', 'board.toml'):
                with urlopen(f'https://raw.githubusercontent.com/{repo}/{revision}/{filename}', timeout=30) as response:
                    data[filename] = tomllib.loads(response.read().decode())
            record = validate(data['porting.toml'], data['board.toml'], name)
        need(record['device']['name'] == name, f'{name}: record name mismatch')
        for zh in (False, True):
            (output / f'{name}{".zh" if zh else ""}.md').write_text(render(record, repo, revision, zh))
        print(f'{name}: rendered device record')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    check_parser = commands.add_parser('check')
    check_parser.add_argument('--device', type=Path, required=True)
    check_parser.add_argument('--base', help='compare code changes with this Git revision')
    site_parser = commands.add_parser('site')
    site_parser.add_argument('--local', action='append', default=[], metavar='DEVICE=PATH')
    args = parser.parse_args()
    try:
        if args.command == 'check':
            check(args.device, args.base)
        else:
            site(args.local)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'porting record: {error}\n')


if __name__ == '__main__':
    main()

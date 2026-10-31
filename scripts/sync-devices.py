#!/usr/bin/env python3
"""Discover public UniXNU device repositories and refresh the documentation catalog."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import tomllib
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / 'docs/.vitepress/device-records'
REPOSITORY = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+')
SLUG = re.compile(r'[a-z0-9][a-z0-9-]*')


def record_tools():
    spec = importlib.util.spec_from_file_location('porting_record', ROOT / 'scripts/porting-record.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GitHub:
    def __init__(self):
        self.token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
        if not self.token and shutil.which('gh'):
            result = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True)
            if result.returncode == 0:
                self.token = result.stdout.strip()
        if not self.token:
            raise ValueError('Set GITHUB_TOKEN or GH_TOKEN, or sign in with gh auth login')

    def request(self, path, payload=None):
        headers = {'Authorization': f'Bearer {self.token}',
                   'Accept': 'application/vnd.github+json', 'User-Agent': 'UniXNU-device-catalog'}
        data = json.dumps(payload).encode() if payload is not None else None
        for attempt in range(4):
            try:
                request = Request('https://api.github.com/' + path, data=data, headers=headers)
                with urlopen(request, timeout=60) as response:
                    body = response.read(32 * 1024 * 1024 + 1)
                if len(body) > 32 * 1024 * 1024:
                    raise ValueError('GitHub response exceeds 32 MiB')
                return json.loads(body)
            except HTTPError as error:
                if error.code not in (429, 500, 502, 503, 504) or attempt == 3:
                    raise
                time.sleep(2 ** attempt)

    def search(self, query):
        found = []
        for page in range(1, 11):
            result = self.request('search/repositories?' + urlencode({
                'q': query, 'per_page': 100, 'page': page}))
            if result.get('total_count', 0) > 1000:
                raise ValueError(f'Split this search into smaller queries: {query}')
            if result.get('incomplete_results'):
                raise ValueError(f'GitHub returned an incomplete search: {query}')
            items = result['items']
            found.extend(item['full_name'] for item in items)
            if len(items) < 100:
                return found
        return found

    def metadata(self, repositories):
        def batch(names):
            fields = []
            for index, name in enumerate(names):
                owner, repo = name.split('/')
                fields.append(f'r{index}:repository(owner:{json.dumps(owner)},name:{json.dumps(repo)})' +
                              '{nameWithOwner databaseId isPrivate isFork parent{nameWithOwner} '
                              'defaultBranchRef{name target{... on Commit{oid}}}}')
            result = self.request('graphql', {'query': 'query{' + ''.join(fields) + '}'})
            for error in result.get('errors', []):
                if error.get('type') != 'NOT_FOUND':
                    raise ValueError('GitHub metadata query failed: ' + error.get('message', 'unknown error'))
            items = {name: result.get('data', {}).get(f'r{index}') for index, name in enumerate(names)}
            fields = []
            for index, name in enumerate(names):
                item = items[name]
                if not item or item.get('isPrivate') or not item.get('defaultBranchRef'):
                    continue
                revision = item['defaultBranchRef']['target']['oid']
                owner, repo = item['nameWithOwner'].split('/')
                fields.append(f'r{index}:repository(owner:{json.dumps(owner)},name:{json.dumps(repo)})' +
                              '{board:object(expression:' + json.dumps(revision + ':board.toml') +
                              '){... on Blob{oid text}} record:object(expression:' +
                              json.dumps(revision + ':porting.toml') + '){... on Blob{oid text}}}')
            if fields:
                sources = self.request('graphql', {'query': 'query{' + ''.join(fields) + '}'})
                if sources.get('errors'):
                    raise ValueError('Could not read the pinned device source files')
                for index, name in enumerate(names):
                    if items[name]:
                        items[name].update(sources.get('data', {}).get(f'r{index}') or {})
            return items

        groups = [repositories[i:i + 12] for i in range(0, len(repositories), 12)]
        result = {}
        with ThreadPoolExecutor(max_workers=3) as pool:
            for group in pool.map(batch, groups):
                result.update(group)
        return result


def bootstrap_registry():
    """Register the current pages so their routes and legacy prose remain available."""
    rows = {}
    for line in (ROOT / 'docs/devices/index.md').read_text().splitlines():
        match = re.match(r'\| \[(.*?)\]\(/devices/([^/)]+)\) \| (.*?) \| (.*?) \|', line)
        if match:
            title, name, soc, summary = match.groups()
            rows[name] = {'title': title, 'soc': soc, 'summary': summary}
    entries = []
    for path in sorted((ROOT / 'docs/devices').glob('*.md')):
        if path.stem == 'index':
            continue
        content = path.read_text()
        table = re.search(r'^\| \[.*?\]\(https://github.com/([^/)]+/[^/)]+)\)', content, re.M)
        other = re.search(r'https://github.com/([^/()\s]+/[^/()\s]+)', content)
        match = table or other
        if not match:
            continue
        repo = match[1].removesuffix('.git')
        if not REPOSITORY.fullmatch(repo):
            continue
        translated = ROOT / 'docs/zh/devices' / path.name
        title = content.splitlines()[0].removeprefix('# ').strip()
        title_zh = translated.read_text().splitlines()[0].removeprefix('# ').strip() if translated.exists() else title
        entries.append({'name': path.stem, 'repository': repo, 'title': title,
                        'title_zh': title_zh, 'format': 1, 'legacy_page': 'preserve',
                        **{key: value for key, value in rows.get(path.stem, {}).items() if key != 'title'}})
    return {'schema_version': 2, 'device': entries}


def load_registry():
    registry = tomllib.loads((ROOT / 'devices.toml').read_text())
    if registry.get('schema_version') == 1:
        return bootstrap_registry()
    if registry.get('schema_version') != 2:
        raise ValueError('device registry schema_version must be 2')
    return registry


def write_registry(registry):
    lines = ['schema_version = 2', '']
    for entry in registry['device']:
        lines.append('[[device]]')
        for key, value in entry.items():
            if value is not None:
                lines.append(f'{key} = {json.dumps(value, ensure_ascii=False)}')
        lines.append('')
    (ROOT / 'devices.toml').write_text('\n'.join(lines))


def board_data(metadata):
    value = metadata.get('board')
    if not value or not value.get('text'):
        return None
    try:
        board = tomllib.loads(value['text'])
        identity = board.get('board', {})
        components = board.get('components', {})
        if not isinstance(identity, dict) or not isinstance(components, dict):
            return None
        if not isinstance(identity.get('name'), str) or not SLUG.fullmatch(identity['name']):
            return None
        selected = components.get('include', [])
        if not isinstance(selected, list) or not all(isinstance(item, str) for item in selected):
            return None
        return board
    except (ValueError, TypeError):
        return None


def update_entry(entry, metadata, tools):
    entry['repository'] = metadata['nameWithOwner']
    entry['repository_id'] = metadata.get('databaseId')
    board = board_data(metadata)
    if not board:
        if entry.get('format') != 2:
            entry['revision'] = metadata['defaultBranchRef']['target']['oid']
        return
    entry['revision'] = metadata['defaultBranchRef']['target']['oid']
    info = board['board']
    entry['board'] = info['name']
    if entry.get('legacy_page') == 'link' and entry['name'] != info['name']:
        suffix = f' ({entry["repository"].split("/")[0]})'
        for key in ('title', 'title_zh'):
            if not entry[key].endswith(suffix):
                entry[key] += suffix
    entry['soc'] = str(info.get('soc', ''))
    entry['format'] = 2 if board.get('schema_version') == 2 else 1
    if entry['format'] != 2:
        for key in ('record_state', 'record_error', 'os_profile', 'components'):
            entry.pop(key, None)
        (SNAPSHOTS / f'{entry["name"]}.toml').unlink(missing_ok=True)
        return
    entry['os_profile'] = str(info.get('os_profile', ''))
    entry['components'] = board.get('components', {}).get('include', [])
    raw = (metadata.get('record') or {}).get('text')
    entry['record_state'] = 'missing'
    entry.pop('record_error', None)
    snapshot = SNAPSHOTS / f'{entry["name"]}.toml'
    if raw:
        try:
            record = tomllib.loads(raw)
            tools.validate(record, board, entry['repository'], allow_custom_components=True)
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            entry['record_state'] = 'invalid'
            entry['record_error'] = str(error)
        else:
            snapshot.write_text(raw)
            entry['record_state'] = 'available'
    if entry['record_state'] != 'available':
        snapshot.unlink(missing_ok=True)


def synchronize(github):
    registry = load_registry()
    existing = registry['device']
    discovered = set()
    for query in ('unixnu in:name,description fork:true is:public',
                  'topic:unixnu fork:true is:public', 'org:UniXNU is:public'):
        discovered.update(github.search(query))
    requested = sorted(discovered | {entry['repository'] for entry in existing})
    metadata = github.metadata(requested)
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    tools = record_tools()
    by_id = {item['databaseId']: item for item in metadata.values()
             if item and item.get('databaseId') and not item.get('isPrivate')}
    used, signatures = set(), set()
    for entry in existing:
        item = metadata.get(entry['repository']) or by_id.get(entry.get('repository_id'))
        if not item or item.get('isPrivate') or not item.get('defaultBranchRef'):
            continue
        update_entry(entry, item, tools)
        used.add(item['nameWithOwner'].lower())
        if item.get('board'):
            signatures.add((item['board']['oid'], (item.get('record') or {}).get('oid')))
    names = {entry['name'] for entry in existing}
    candidates = [item for item in metadata.values() if item and not item.get('isPrivate')
                  and item.get('defaultBranchRef') and item['nameWithOwner'].lower() not in used]
    candidates.sort(key=lambda item: (not item['nameWithOwner'].startswith('UniXNU/'),
                                      item.get('isFork', False), item['nameWithOwner'].lower()))
    added = 0
    for item in candidates:
        repo = item['nameWithOwner']
        board = board_data(item)
        if not board:
            continue
        name = board['board']['name']
        signature = (item['board']['oid'], (item.get('record') or {}).get('oid'))
        if signature in signatures or repo.lower() in used:
            continue
        route = name
        if route in names:
            route = f'{name}-{repo.split("/")[0].lower()}'
        route = re.sub(r'[^a-z0-9-]', '-', route)
        if route in names:
            continue
        title = str(board['board'].get('description') or name).replace('\n', ' ')[:160]
        if route != name:
            title += f' ({repo.split("/")[0]})'
        entry = {'name': route, 'repository': repo, 'title': title, 'title_zh': title,
                 'format': 1, 'legacy_page': 'link'}
        update_entry(entry, item, tools)
        existing.append(entry)
        names.add(route)
        signatures.add(signature)
        used.add(repo.lower())
        added += 1
    registry['device'] = sorted(existing, key=lambda entry: (entry['name'] != 'sheng', entry['name']))
    write_registry(registry)
    render_site(registry)
    print(f'Scanned {len(discovered)} repositories; registered {len(existing)} sources; added {added}')
    for entry in existing:
        if entry.get('format') == 2 and entry.get('record_state') != 'available':
            print(f'{entry["repository"]}: record {entry.get("record_state", "missing")} '
                  f'{entry.get("record_error", "")}')
    return registry


def render_site(registry, local=None):
    tools = record_tools()
    local = local or {}
    names = set()
    navigation = []
    for entry in registry['device']:
        name, repo = entry['name'], entry['repository']
        if not SLUG.fullmatch(name) or not REPOSITORY.fullmatch(repo) or name in names:
            raise ValueError(f'Invalid or duplicate device entry: {name}')
        names.add(name)
        navigation.append({'name': name, 'title': entry['title'], 'title_zh': entry['title_zh']})
        record = None
        if entry.get('format') == 2:
            if name in local:
                record = tools.check(Path(local[name]))
            elif entry.get('record_state') == 'available':
                record = tomllib.loads((SNAPSHOTS / f'{name}.toml').read_text())
                board = {'board': {'name': entry.get('board', name), 'soc': entry['soc'],
                                   'os_profile': entry['os_profile']},
                         'components': {'include': entry.get('components', [])}}
                tools.validate(record, board, name, allow_custom_components=True)
        for zh in (False, True):
            directory = ROOT / ('docs/zh/devices' if zh else 'docs/devices')
            page = directory / f'{name}.md'
            if entry.get('format') != 2:
                if entry.get('legacy_page') == 'preserve' and page.exists():
                    continue
                page.write_text(f'[{repo}](https://github.com/{repo})\n')
                continue
            revision = entry.get('revision', '')
            if not re.fullmatch(r'[a-f0-9]{40}', revision):
                raise ValueError(f'{name}: pin a full source commit')
            title = tools.markdown_text(entry['title_zh' if zh else 'title'])
            body = f'# {title}\n\n[{repo}](https://github.com/{repo})\n\n'
            if record:
                body += tools.render(record, repo, revision, zh)
            else:
                body += ('在设备仓库补齐并校验 [porting.toml](/zh/porting/records)，随后生成各部分的适配记录。'
                         if zh else 'Complete and validate [porting.toml](/porting/records) in the device repository to publish its subsystem record.')
                if entry.get('record_error'):
                    body += '\n\n' + tools.markdown_text(entry['record_error'])
            page.write_text(body.rstrip() + '\n')
    (ROOT / 'docs/.vitepress/device-catalog.json').write_text(json.dumps(navigation, ensure_ascii=False, indent=2) + '\n')
    for zh in (False, True):
        prefix = '/zh' if zh else ''
        lines = ['# ' + ('设备' if zh else 'Devices'), '',
                 ('打开设备页查看来源、配置和适配记录。格式 2 页面由固定版本的 porting.toml 生成。'
                  if zh else 'Open a device page for its sources, configuration and porting record. Format 2 pages use porting.toml at the pinned source revision.'), '',
                 ('构建与验证见[构建与启动](/zh/building)、[移植步骤](/zh/porting/steps)和[日志抓取](/zh/porting/log-capture)。'
                  if zh else 'Follow [Build and boot](/building), [porting steps](/porting/steps) and [log capture](/porting/log-capture) for build and validation procedures.'), '',
                 '| ' + ('设备 | SoC | 格式 | 文档 | 仓库' if zh else 'Device | SoC | Format | Documentation | Repository') + ' |',
                 '| --- | --- | --- | --- | --- |']
        for entry in registry['device']:
            name, repo = entry['name'], entry['repository']
            title = tools.markdown_text(entry['title_zh' if zh else 'title'])
            state = ('适配记录' if zh else 'Porting record') if entry.get('record_state') == 'available' else (
                ('记录待补齐' if zh else 'Record pending') if entry.get('format') == 2 else
                ('设备说明' if zh else 'Device notes') if entry.get('legacy_page') == 'preserve' else
                ('仓库链接' if zh else 'Repository link'))
            lines.append(f'| [{title}]({prefix}/devices/{name}) | {tools.markdown_text(entry.get("soc", ""))} | '
                         f'{entry.get("format", 1)} | {state} | [{repo}](https://github.com/{repo}) |')
        lines += ['', '## ' + ('维护设备记录' if zh else 'Maintain device records') + ' {#adding-a-device}', '',
                  ('按[记录指南](/zh/porting/records#publishing-and-reuse)发布设备配置与适配记录。'
                   if zh else 'Publish device configuration and records using the [record guide](/porting/records#publishing-and-reuse).'), '']
        (ROOT / ('docs/zh/devices/index.md' if zh else 'docs/devices/index.md')).write_text('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render', action='store_true', help='render the committed catalog without scanning GitHub')
    args = parser.parse_args()
    try:
        if args.render:
            render_site(load_registry())
        else:
            synchronize(GitHub())
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'device catalog: {error}\n')


if __name__ == '__main__':
    main()

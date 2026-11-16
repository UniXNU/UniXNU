#!/usr/bin/env python3
"""Inventory every branch and differing file in a set of local fork repositories."""
import argparse
from collections import Counter
import concurrent.futures
import csv
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.parse


def command(*args):
    return subprocess.check_output([str(arg) for arg in args])


def git(repo, *args):
    return command('git', '-C', repo, *args)


def tree(repo, revision):
    entries = {}
    for item in git(repo, 'ls-tree', '-rz', '--full-tree', revision).split(b'\0'):
        if item:
            metadata, path = item.split(b'\t', 1)
            mode, kind, blob = metadata.decode().split()
            entries[path.decode()] = (mode, kind, blob)
    return entries


def classify(main, fork, bases):
    if bases and all(fork == base for base in bases):
        return 'upstream-only'
    if bases and all(main == base for base in bases):
        return 'fork-only'
    if bases and any(fork == base for base in bases):
        return 'multiple-bases'
    return 'both-changed' if bases else 'unrelated-history'


def inspect(name, repository, owner, upstream, output, fetch):
    repo = Path(repository).resolve()
    main_ref = 'refs/remotes/fork-audit-upstream/main'
    fork_ref = 'refs/remotes/fork-audit/'
    shallow = git(repo, 'rev-parse', '--is-shallow-repository').strip() == b'true'
    if shallow and not fetch:
        raise RuntimeError(f'{repo}: use --fetch to retrieve complete history')
    if fetch:
        if shallow:
            subprocess.run(['git', '-C', str(repo), 'fetch', '--quiet', '--unshallow',
                            '--no-tags', '--no-recurse-submodules',
                            f'https://github.com/{owner}/{name}.git'], check=True)
        subprocess.run(['git', '-C', str(repo), 'fetch', '--quiet', '--no-tags',
                        '--no-recurse-submodules', f'https://github.com/{upstream}/{name}.git',
                        '+refs/heads/main:' + main_ref], check=True)
        subprocess.run(['git', '-C', str(repo), 'fetch', '--quiet', '--prune', '--no-tags',
                        '--no-recurse-submodules', f'https://github.com/{owner}/{name}.git',
                        '+refs/heads/*:' + fork_ref + '*'], check=True)
    main = git(repo, 'rev-parse', main_ref).decode().strip()
    branches = []
    for line in git(repo, 'for-each-ref', '--format=%(refname) %(objectname)', fork_ref).decode().splitlines():
        reference, revision = line.split()
        branches.append((reference[len(fork_ref):], revision))
    trees = {}

    def entries(revision):
        if revision not in trees:
            trees[revision] = tree(repo, revision)
        return trees[revision]

    main_tree = entries(main)
    files = {}
    commits = {}
    branch_rows = []
    for branch, revision in branches:
        merge = subprocess.run(['git', '-C', str(repo), 'merge-base', '--all', main, revision], capture_output=True, check=False)
        if merge.returncode not in (0, 1):
            raise RuntimeError(merge.stderr.decode())
        bases = merge.stdout.decode().splitlines()
        base_trees = [entries(base) for base in bases]
        fork_tree = entries(revision)
        behind, ahead = map(int, git(repo, 'rev-list', '--left-right', '--count', main + '...' + revision).split())
        counts = Counter()
        for path in sorted(main_tree.keys() | fork_tree.keys()):
            old, new = main_tree.get(path), fork_tree.get(path)
            if old == new:
                counts['identical'] += 1
                continue
            status = classify(old, new, [base.get(path) for base in base_trees])
            counts[status] += 1
            identity = hashlib.sha256(json.dumps([name, path, old, new]).encode()).hexdigest()[:16]
            if identity not in files:
                patch = output / 'diffs' / name / (identity + '.patch')
                patch.parent.mkdir(parents=True, exist_ok=True)
                patch.write_bytes(git(repo, 'diff', '--no-ext-diff', '--no-textconv', '--no-renames',
                                     '--binary', main, revision, '--', path))
                hunks = [line for line in patch.read_text(errors='replace').splitlines() if line.startswith('@@')]
                files[identity] = dict(id=identity, repo=name, path=path, upstream_main=main,
                                       upstream_entry=old, fork_entry=new, branches=[], classifications=[],
                                       hunks=hunks, patch=str(patch.relative_to(output)),
                                       source_url=f'https://github.com/{owner}/{name}/blob/{revision}/' + urllib.parse.quote(path),
                                       decision='pending', reason='')
            row = files[identity]
            row['branches'].append(branch)
            if status not in row['classifications']:
                row['classifications'].append(status)
        revision_commits = git(repo, 'rev-list', revision, '^' + main).decode().splitlines()
        for commit in revision_commits:
            if commit not in commits:
                data = git(repo, 'show', '-s', '--format=%an%x00%ae%x00%aI%x00%P%x00%s', commit).decode().rstrip('\n').split('\0')
                author, email, date, parents, title = data
                paths = git(repo, 'diff-tree', '--root', '--no-commit-id', '--name-only', '-r', '-m', '-z', commit).split(b'\0')
                commits[commit] = dict(repo=name, sha=commit, author=author, email=email, date=date,
                                       parents=parents.split(), title=title,
                                       paths=sorted({path.decode() for path in paths if path}), branches=[],
                                       source_url=f'https://github.com/{owner}/{name}/commit/{commit}')
            commits[commit]['branches'].append(branch)
        branch_rows.append(dict(repo=name, branch=branch, sha=revision, upstream_main=main,
                                merge_bases=bases, ahead=ahead, behind=behind, files=dict(counts)))
    return dict(repo=name, path=str(repo), upstream_main=main, branches=branch_rows,
                files=list(files.values()), commits=list(commits.values()))


def write_csv(path, rows, fields):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value
                             for key, value in row.items() if key in fields})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repositories', type=Path, required=True, help='JSON object mapping repository names to local paths')
    parser.add_argument('--owner', required=True)
    parser.add_argument('--upstream', default='UniXNU')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fetch', action='store_true', help='refresh upstream main and every fork branch')
    parser.add_argument('--review', type=Path, help='JSON rows with file id, decision and reason annotations')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    repositories = json.loads(args.repositories.read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(inspect, name, path, args.owner, args.upstream, output, args.fetch)
                   for name, path in sorted(repositories.items())]
        results = [future.result() for future in futures]
    branches = [row for result in results for row in result['branches']]
    files = [row for result in results for row in result['files']]
    commits = [row for result in results for row in result['commits']]
    if args.review:
        reviews = {row['id']: row for row in json.loads(args.review.read_text())}
        for row in files:
            if review := reviews.get(row['id']):
                row.update(decision=review['decision'], reason=review['reason'])
    snapshot = dict(captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    owner=args.owner, upstream=args.upstream, repositories=results)
    (output / 'audit.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n')
    write_csv(output / 'branches.csv', branches, ['repo', 'branch', 'sha', 'upstream_main', 'ahead', 'behind', 'merge_bases', 'files'])
    fields = ['id', 'repo', 'path', 'classifications', 'decision', 'reason',
              'branches', 'hunks', 'upstream_entry', 'fork_entry', 'patch', 'source_url']
    write_csv(output / 'files.csv', files, fields)
    write_csv(output / 'fork-files.csv',
              [row for row in files if any(kind != 'upstream-only' for kind in row['classifications'])], fields)
    write_csv(output / 'commits.csv', commits, ['repo', 'sha', 'author', 'date', 'title', 'branches', 'paths', 'source_url'])
    for result in results:
        candidates = sum(any(kind != 'upstream-only' for kind in row['classifications']) for row in result['files'])
        print(f"{result['repo']}: {len(result['branches'])} branches, {len(result['files'])} distinct file differences, "
              f"{candidates} fork changes, {len(result['commits'])} commits")


if __name__ == '__main__':
    main()

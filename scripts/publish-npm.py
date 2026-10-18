#!/usr/bin/env python3
"""Validate signed upstream bytes before preparing or publishing npm packages."""
import argparse
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tarfile
import zipfile

SOURCE = 'romulofebasi/synapse'
MIRROR = 'romulofebasi/synapse-releases'
ISSUER = 'https://token.actions.githubusercontent.com'
PLATFORMS = (
    ('darwin', 'arm64', 'aarch64-apple-darwin', 'tar.gz', 'syn'),
    ('linux', 'x64', 'x86_64-unknown-linux-gnu', 'tar.gz', 'syn'),
    ('linux', 'arm64', 'aarch64-unknown-linux-gnu', 'tar.gz', 'syn'),
    ('win32', 'x64', 'x86_64-pc-windows-msvc', 'zip', 'syn.exe'),
)
MAX_ARCHIVE = 512 * 1024 * 1024
MAX_TEXT = 16 * 1024 * 1024


class Rejected(Exception):
    """A named publication boundary refused the selected inputs."""


def require(value, reason):
    if not value:
        raise Rejected(reason)


def version(tag):
    require(isinstance(tag, str) and len(tag) <= 64 and re.fullmatch(
        r'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', tag), 'invalid-tag')
    return tag[1:]


def run(arguments, *, cwd=None):
    try:
        return subprocess.run(arguments, cwd=cwd, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Rejected('external-tool-unavailable-or-timeout') from error


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate-json-field')
        result[key] = value
    return result


def document(data):
    try:
        return json.loads(data, object_pairs_hook=unique_object)
    except (ValueError, UnicodeError) as error:
        raise Rejected('invalid-json') from error


def sha(stream):
    stream.seek(0)
    result = hashlib.file_digest(stream, 'sha256').hexdigest()
    stream.seek(0)
    return result


def regular(stack, path, maximum):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError as error:
        raise Rejected('missing-or-unsafe-file') from error
    stream = stack.enter_context(os.fdopen(fd, 'rb'))
    info = os.fstat(stream.fileno())
    require(stat.S_ISREG(info.st_mode) and 0 < info.st_size <= maximum, 'invalid-file-size-or-type')
    return stream


def archive_names(tag):
    selected = version(tag)
    return {f'synapse-{selected}-{target}.{suffix}' for _, _, target, suffix, _ in PLATFORMS}


def download(tag, directory, repository):
    version(tag)
    require(repository == MIRROR, 'wrong-mirror')
    require(not os.path.lexists(directory), 'download-destination-exists')
    names = archive_names(tag) | {'release-metadata.json', 'SHA256SUMS', 'SHA256SUMS.cosign.bundle'}
    command = ['gh', 'release', 'download', tag, '--repo', repository, '--dir', str(directory)]
    for name in sorted(names):
        command.extend(['--pattern', name])
    require(run(command).returncode == 0, 'download-failed')


def receipt(data, tag):
    require(isinstance(data, dict) and set(data) == {'schemaVersion', 'tag', 'version', 'commit', 'inputs', 'notesSHA256'}, 'invalid-source-receipt')
    require(type(data['schemaVersion']) is int and data['schemaVersion'] == 1 and data['tag'] == tag
            and data['version'] == version(tag), 'source-receipt-tag-mismatch')
    require(isinstance(data['commit'], str) and re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', data['commit']), 'invalid-source-commit')
    inputs = data['inputs']
    require(isinstance(inputs, dict) and set(inputs) == {'Cargo.toml', 'Cargo.lock', 'CHANGELOG.md'}, 'invalid-source-inputs')
    require(all(isinstance(v, str) and re.fullmatch(r'[0-9a-f]{64}', v)
                for v in [*inputs.values(), data['notesSHA256']]), 'invalid-source-digest')
    return data


def archive_members(stack, stream, prefix, suffix, binary, changelog_digest):
    if suffix == 'zip':
        archive = stack.enter_context(zipfile.ZipFile(stream))
        members = archive.infolist()
        names = [(m.filename, m.is_dir(), m.file_size, m) for m in members]
        require(all(m.orig_filename == m.filename and not m.flag_bits & 1
                    and ((m.is_dir() and stat.S_IFMT(m.external_attr >> 16) in (0, stat.S_IFDIR))
                         or (not m.is_dir() and stat.S_IFMT(m.external_attr >> 16) in (0, stat.S_IFREG)
                             and not m.external_attr & 0x10))
                    for m in members), 'unsafe-archive-member')
        opener = lambda member: archive.open(member)
    else:
        archive = stack.enter_context(tarfile.open(fileobj=stream, mode='r:gz'))
        members = archive.getmembers()
        names = [(m.name, m.isdir(), m.size, m) for m in members]
        require(all(m.isfile() or m.isdir() for m in members), 'unsafe-archive-member')
        opener = archive.extractfile
    require(4 <= len(names) <= 5, 'invalid-archive-inventory')
    allowed = {prefix + '/' + name for name in (binary, 'README.md', 'LICENSE', 'CHANGELOG.md')}
    seen, files = set(), {}
    for name, directory, size, member in names:
        canonical = name.rstrip('/')
        require(canonical not in seen, 'duplicate-archive-member')
        seen.add(canonical)
        if directory:
            require(canonical == prefix, 'unsafe-archive-directory')
        else:
            require(name in allowed and 0 < size <= (MAX_ARCHIVE if name.endswith('/' + binary) else MAX_TEXT), 'unexpected-archive-member')
            files[name] = member
    require(set(files) == allowed, 'missing-archive-member')
    with opener(files[prefix + '/CHANGELOG.md']) as changelog:
        require(hashlib.sha256(changelog.read(MAX_TEXT + 1)).hexdigest() == changelog_digest, 'archive-changelog-mismatch')
    return opener, files[prefix + '/' + binary]


def write_json(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def prepare(tag, directory, output, launcher):
    selected = version(tag)
    require(directory.is_dir() and not directory.is_symlink(), 'unsafe-download-directory')
    archives = archive_names(tag)
    signed = archives | {'release-metadata.json'}
    require({p.name for p in directory.iterdir()} == signed | {'SHA256SUMS', 'SHA256SUMS.cosign.bundle'}, 'incomplete-release-inventory')
    require(not os.path.lexists(output), 'package-destination-exists')
    with ExitStack() as stack:
        streams = {name: regular(stack, directory / name, MAX_ARCHIVE if name in archives else MAX_TEXT)
                   for name in signed | {'SHA256SUMS', 'SHA256SUMS.cosign.bundle'}}
        def identity(info):
            return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns
        frozen = {name: identity(os.fstat(stream.fileno())) for name, stream in streams.items()}
        def unchanged():
            require(all(identity(os.stat(directory / name, follow_symlinks=False)) == frozen[name]
                        and identity(os.fstat(stream.fileno())) == frozen[name]
                        for name, stream in streams.items()), 'release-input-changed')
        signature_identity = f'https://github.com/{SOURCE}/.github/workflows/release.yml@refs/tags/{tag}'
        verified = run(['cosign', 'verify-blob', '--bundle', str(directory / 'SHA256SUMS.cosign.bundle'),
                        '--certificate-identity', signature_identity, '--certificate-oidc-issuer', ISSUER,
                        str(directory / 'SHA256SUMS')])
        require(verified.returncode == 0, 'signature-verification-failed')
        unchanged()
        checksums = ''.join(f'{sha(streams[name])}  {name}\n' for name in sorted(signed))
        require(streams['SHA256SUMS'].read() == checksums.encode(), 'signed-checksum-mismatch')
        source = receipt(document(streams['release-metadata.json'].read()), tag)
        descriptors = []
        for system, cpu, target, suffix, binary in PLATFORMS:
            prefix = f'synapse-{selected}-{target}'
            descriptors.append((system, cpu, binary, *archive_members(stack, streams[f'{prefix}.{suffix}'], prefix,
                               suffix, binary, source['inputs']['CHANGELOG.md'])))
        # Validate all four authenticated archives before preparing any npm package.
        output.mkdir(mode=0o700)
        packages = []
        for system, cpu, binary, opener, member in descriptors:
            destination = output / f'{system}-{cpu}'
            destination.mkdir()
            with opener(member) as original, (destination / binary).open('xb') as target:
                count = 0
                while block := original.read(1024 * 1024):
                    count += len(block)
                    require(count <= MAX_ARCHIVE, 'expanded-binary-too-large')
                    target.write(block)
            (destination / binary).chmod(0o755)
            package = {'name': f'@febasi/synapse-{system}-{cpu}', 'version': selected,
                       'description': f'Prebuilt syn binary for {system}-{cpu}. Companion to @febasi/synapse.',
                       'license': 'MIT', 'os': [system], 'cpu': [cpu], 'files': [binary],
                       'homepage': f'https://github.com/{MIRROR}',
                       'repository': {'type': 'git', 'url': f'git+https://github.com/{MIRROR}.git'}}
            write_json(destination / 'package.json', package)
            packages.append((destination, package['name']))
        destination = output / 'launcher'
        destination.mkdir()
        (destination / 'bin').mkdir()
        with ExitStack() as launcher_stack:
            package = document(regular(launcher_stack, launcher / 'package.json', MAX_TEXT).read())
            require(package.get('name') == '@febasi/synapse' and package.get('bin') == {'syn': 'bin/syn.js'}
                    and package.get('files') == ['bin/syn.js', 'README.md']
                    and set(package.get('optionalDependencies', {})) == {name for _, name in packages}
                    and not package.get('scripts'), 'invalid-launcher')
            for name in ('README.md', 'bin/syn.js'):
                (destination / name).write_bytes(regular(launcher_stack, launcher / name, MAX_TEXT).read())
            (destination / 'bin/syn.js').chmod(0o755)
            package['version'] = selected
            package['optionalDependencies'] = {name: selected for _, name in packages}
            write_json(destination / 'package.json', package)
        packages.append((destination, '@febasi/synapse'))
        write_json(output / 'source-receipt.json', source)
        unchanged()
        return packages


def registry_exists(name, selected):
    result = run(['npm', 'view', f'{name}@{selected}', 'version', '--json'])
    if result.returncode == 0:
        require(document(result.stdout) == selected, 'unexpected-registry-version')
        return True
    response = document(result.stdout.strip() or result.stderr)
    require(isinstance(response, dict) and isinstance(response.get('error'), dict)
            and response['error'].get('code') == 'E404', 'registry-query-failed')
    return False


def publish(tag, directory, output, launcher):
    selected = version(tag)
    packages = prepare(tag, directory, output, launcher)
    npm = run(['npm', '--version'])
    require(npm.returncode == 0 and re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', npm.stdout.strip())
            and tuple(map(int, npm.stdout.strip().split('.'))) >= (11, 5, 1), 'unsupported-npm-version')
    pending = [(path, name) for path, name in packages if not registry_exists(name, selected)]
    for path, name in pending:
        require(run(['npm', 'publish', '--provenance', '--access', 'public', '--ignore-scripts'], cwd=path).returncode == 0,
                'npm-publication-failed')
        print(json.dumps({'status': 'published', 'package': name, 'version': selected}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['resolve', 'download', 'prepare', 'publish'])
    parser.add_argument('--tag', required=True)
    parser.add_argument('--github-output', type=Path)
    parser.add_argument('--repository', default=MIRROR)
    parser.add_argument('--directory', type=Path, default=Path('dl'))
    parser.add_argument('--output', type=Path, default=Path('prepared'))
    parser.add_argument('--launcher', type=Path, default=Path('npm/synapse'))
    args = parser.parse_args()
    try:
        selected = version(args.tag)
        if args.operation == 'resolve':
            require(args.github_output is not None, 'missing-output-path')
            with args.github_output.open('a') as stream:
                stream.write(f'tag={args.tag}\nversion={selected}\n')
        elif args.operation == 'download':
            download(args.tag, args.directory, args.repository)
        elif args.operation == 'prepare':
            prepare(args.tag, args.directory, args.output, args.launcher)
        else:
            publish(args.tag, args.directory, args.output, args.launcher)
        return 0
    except Rejected as error:
        print(json.dumps({'status': 'rejected', 'reason': str(error)}))
        return 1
    except (OSError, ValueError, tarfile.TarError, zipfile.BadZipFile, KeyError, TypeError):
        print(json.dumps({'status': 'rejected', 'reason': 'malformed-publication-input'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

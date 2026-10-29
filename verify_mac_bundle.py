#!/usr/bin/env python3
"""Check Intel architecture and deployment metadata; target-system testing remains required."""
import argparse
import hashlib
import json
import plistlib
import struct
from pathlib import Path

MINIMUM = (10, 13, 0)
MAGIC64 = 0xFEEDFACF
X86_64 = 0x01000007


def version(value):
    return value >> 16, (value >> 8) & 255, value & 255


def macho(data, target=MINIMUM):
    if len(data) < 32:
        raise ValueError('Truncated Mach-O header')
    magic, cpu, subtype, _, count, size, _, _ = struct.unpack_from('<IiiIIIII', data)
    if magic != MAGIC64:
        raise ValueError('Expected a thin, little-endian 64-bit Mach-O, not a universal or non-Mac binary')
    if cpu != X86_64 or (subtype & 0xFFFFFF) != 3:
        raise ValueError('Expected generic x86_64, not Apple Silicon or a newer-CPU-only Intel subtype')
    end = 32 + size
    if end > len(data):
        raise ValueError('Truncated load commands')
    cursor, minimums, libraries = 32, [], []
    for _ in range(count):
        if cursor + 8 > end:
            raise ValueError('Invalid load-command count')
        command, length = struct.unpack_from('<II', data, cursor)
        if length < 8 or cursor + length > end:
            raise ValueError('Invalid load-command size')
        if command == 0x32:  # LC_BUILD_VERSION
            if length < 24:
                raise ValueError('Truncated LC_BUILD_VERSION')
            platform, minimum = struct.unpack_from('<II', data, cursor + 8)
            if platform != 1:
                raise ValueError('Binary does not target macOS')
            minimums.append(version(minimum))
        elif command == 0x24:  # LC_VERSION_MIN_MACOSX
            if length < 16:
                raise ValueError('Truncated LC_VERSION_MIN_MACOSX')
            minimums.append(version(struct.unpack_from('<I', data, cursor + 8)[0]))
        elif command in {0xC, 0x80000018, 0x8000001F, 0x20, 0x80000023}:
            if length < 24:
                raise ValueError('Truncated dylib command')
            offset = struct.unpack_from('<I', data, cursor + 8)[0]
            if offset < 24 or offset >= length:
                raise ValueError('Invalid library path')
            path = data[cursor + offset:cursor + length].split(b'\0', 1)[0].decode('utf8')
            if path.startswith('/') and not path.startswith(('/usr/lib/', '/System/Library/')):
                raise ValueError('Nonportable absolute library dependency: ' + path)
            libraries.append(path)
        cursor += length
    if cursor != end or not minimums:
        raise ValueError('Missing or inconsistent deployment load commands')
    if max(minimums) > target:
        raise ValueError('Binary still requires macOS ' + '.'.join(map(str, max(minimums))))
    return {'architecture':'x86_64', 'minimum_macos':'.'.join(map(str, max(minimums))), 'libraries':libraries}


def verify(bundle, target=MINIMUM):
    info = plistlib.loads((bundle / 'Contents/Info.plist').read_bytes())
    minimum = tuple(int(part) for part in info.get('LSMinimumSystemVersion', '').split('.'))
    if minimum + (0,) * (3 - len(minimum)) != target:
        raise ValueError('Info.plist does not declare the requested deployment target')
    executable = bundle / 'Contents/MacOS' / info['CFBundleExecutable']
    result = {'bundle':bundle.name, 'files':{}, 'status':'candidate_metadata_passed',
              'runtime_tested_on_target':False,
              'requested_minimum_macos':'.'.join(map(str, target)),
              'limit':'Architecture and version metadata only; old-system symbols, audio, MIDI, and plugins still need a test on the target Mac.'}
    for path in bundle.rglob('*'):
        if not path.is_file() or path.is_symlink():
            continue
        with path.open('rb') as file:
            first = file.read(4)
        if path != executable and first not in {b'\xcf\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xce\xfa\xed\xfe', b'\xfe\xed\xfa\xce', b'\xca\xfe\xba\xbe', b'\xbe\xba\xfe\xca', b'\xca\xfe\xba\xbf', b'\xbf\xba\xfe\xca'}:
            continue
        data = path.read_bytes()
        item = macho(data, target)
        item['sha256'] = hashlib.sha256(data).hexdigest()
        result['files'][str(path.relative_to(bundle))] = item
    if str(executable.relative_to(bundle)) not in result['files']:
        raise ValueError('Main executable was not verified')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--json', type=Path)
    parser.add_argument('--minimum-macos', default='10.13')
    args = parser.parse_args()
    target = tuple(int(x) for x in args.minimum_macos.split('.'))
    if len(target) not in (2, 3):
        parser.error('--minimum-macos must be a major.minor[.patch] version')
    target += (0,) * (3 - len(target))
    result = verify(args.bundle.resolve(), target)
    output = json.dumps(result, indent=2) + '\n'
    if args.json:
        args.json.write_text(output)
    print(output)

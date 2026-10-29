#!/usr/bin/env python3
"""Apply the minimal, idempotent LYNX 0.1.19 macOS deployment metadata fix."""
import argparse
from pathlib import Path

OLD = '<key>LSMinimumSystemVersion</key><string>11.0</string>'
NEW = '<key>LSMinimumSystemVersion</key><string>${CMAKE_OSX_DEPLOYMENT_TARGET}</string>'


def apply(root):
    path = root / 'CMakeLists.txt'
    content = path.read_text()
    if content.count(NEW) == 1 and OLD not in content:
        print('Deployment metadata fix is already applied.')
        return
    if content.count(OLD) != 1 or 'project(LYNX VERSION 0.1.19 ' not in content:
        raise SystemExit('Unexpected source version or CMake layout. No files were changed.')
    path.write_text(content.replace(OLD, NEW))
    print('Info.plist now follows CMAKE_OSX_DEPLOYMENT_TARGET; the normal 11.0 default is preserved.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    apply(parser.parse_args().source.resolve())

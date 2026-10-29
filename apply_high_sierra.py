#!/usr/bin/env python3
"""Backport LYNX's four filesystem users without disabling SDK availability checks."""
import argparse
import hashlib
from pathlib import Path
import shutil
import urllib.request
from apply_compatibility import apply as apply_metadata

GHC_COMMIT = '8a2edd6d92ed820521d42c94d179462bf06b5ed3'
GHC_SHA256 = '522791c2a2f1959193fdff61f4668c5ba894459753170b2246971272ee8ddc47'
SOURCE_SHAS = {
    'FlpImport.cpp': 'd25672b7d69cae999d7d3cb1d594e02352f947d390b1a3c9151a6deeb67a02f2',
    'SoundFont.cpp': '34b741f1e2804614f20b0bf67d56c105b907a17e5c324ace91850b2a553cb220',
    'SoundFontLoad.cpp': 'aea33712ceb14a7fc31d19e1570017ec1a067b7cad6fd56e2797d01f6c1c76d4',
    'SoundFontIndex.cpp': '46317eea24cc73f1f89ae40611b267609d3b8547f18ef9b953d0dd54087abd40',
}
REPLACEMENTS = [
    ('#include <filesystem>', '#include "core/CompatibilityFilesystem.h"'),
    ('std::filesystem', 'lynx::compatfs'),
    ('std::ifstream', 'lynx::compatio::ifstream'),
    ('std::ofstream', 'lynx::compatio::ofstream'),
]


def apply(root, header=None):
    root = Path(root).resolve()
    kit = Path(__file__).resolve().parent
    prepared = []
    for name, expected in SOURCE_SHAS.items():
        path = root / 'src/core' / name
        current = path.read_text()
        original = current
        for old, new in reversed(REPLACEMENTS):
            original = original.replace(new, old)
        if hashlib.sha256(original.encode()).hexdigest() != expected:
            raise SystemExit('Unexpected source content: ' + name + '; no backport applied.')
        updated = original
        for old, new in REPLACEMENTS:
            updated = updated.replace(old, new)
        if current not in (original, updated):
            raise SystemExit('Partly modified source: ' + name + '; no backport applied.')
        prepared.append((path, updated))
    if header:
        data = Path(header).read_bytes()
    else:
        url = 'https://raw.githubusercontent.com/gulrak/filesystem/' + GHC_COMMIT + '/include/ghc/filesystem.hpp'
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read()
    if hashlib.sha256(data).hexdigest() != GHC_SHA256:
        raise SystemExit('Filesystem dependency checksum mismatch; no backport applied.')
    apply_metadata(root)
    (root / 'src/core/ghc_filesystem.hpp').write_bytes(data)
    shutil.copy2(kit / 'compatibility/CompatibilityFilesystem.h', root / 'src/core/CompatibilityFilesystem.h')
    for path, updated in prepared:
        path.write_text(updated)
    print('High Sierra filesystem backport applied; dependency SHA-256 verified.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--filesystem-header', type=Path)
    args = parser.parse_args()
    apply(args.source, args.filesystem_header)

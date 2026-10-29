#!/usr/bin/env python3
import contextlib
import io
import plistlib
import struct
import tempfile
import unittest
from pathlib import Path
import apply_compatibility as patch
import verify_mac_bundle as check


def binary(minimum=0x000A0D00, cpu=check.X86_64, subtype=3, library=None):
    commands = struct.pack('<IIIIII',0x32,24,1,minimum,0x000F0000,0)
    count = 1
    if library:
        value = library.encode() + b'\0'
        length = (24 + len(value) + 7) // 8 * 8
        commands += struct.pack('<IIIIII',0xC,length,24,0,0,0) + value + bytes(length-24-len(value))
        count += 1
    return struct.pack('<IiiIIIII',check.MAGIC64,cpu,subtype,2,count,len(commands),0,0) + commands


class CompatibilityKitTests(unittest.TestCase):
    def test_accepts_requested_intel_target(self):
        result = check.macho(binary(library='/usr/lib/libc++.1.dylib'))
        self.assertEqual(result['minimum_macos'],'10.13.0')
        self.assertEqual(result['architecture'],'x86_64')

    def test_rejects_wrong_cpu_or_newer_os(self):
        for data in (binary(0x000A0E00),binary(0x000A0F00),binary(0x000B0000),binary(cpu=0x0100000C),binary(subtype=8)):
            with self.subTest(data=data), self.assertRaises(ValueError):
                check.macho(data)

    def test_rejects_truncated_or_nonportable_binary(self):
        for data in (b'',binary()[:-3],b'\xca\xfe\xba\xbe'+bytes(60),binary(library='/opt/homebrew/lib/libfoo.dylib')):
            with self.subTest(data=data), self.assertRaises(ValueError):
                check.macho(data)

    def test_bundle_requires_matching_minimum_and_main_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)/'LYNX.app'
            (bundle/'Contents/MacOS').mkdir(parents=True)
            info = bundle/'Contents/Info.plist'
            info.write_bytes(plistlib.dumps({'CFBundleExecutable':'LYNX','LSMinimumSystemVersion':'10.13'}))
            (bundle/'Contents/MacOS/LYNX').write_bytes(binary())
            self.assertFalse(check.verify(bundle)['runtime_tested_on_target'])
            info.write_bytes(plistlib.dumps({'CFBundleExecutable':'LYNX','LSMinimumSystemVersion':'11.0'}))
            with self.assertRaises(ValueError): check.verify(bundle)

    def test_explicit_catalina_profile_keeps_its_own_minimum(self):
        data = binary(0x000A0F00)
        self.assertEqual(check.macho(data, (10, 15, 0))['minimum_macos'], '10.15.0')
        with self.assertRaises(ValueError):
            check.macho(data, (10, 13, 0))

    def test_patch_is_idempotent_and_preserves_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'CMakeLists.txt'
            before='set(CMAKE_OSX_DEPLOYMENT_TARGET "11.0" CACHE STRING "Minimum macOS version")\nproject(LYNX VERSION 0.1.19 LANGUAGES C CXX)\n'+patch.OLD
            p.write_text(before)
            with contextlib.redirect_stdout(io.StringIO()):
                patch.apply(root);once=p.read_text();patch.apply(root)
            self.assertEqual(p.read_text(),once)
            self.assertIn(patch.NEW,once)
            self.assertIn('"11.0" CACHE',once)
            p.write_text('another project')
            with self.assertRaises(SystemExit): patch.apply(root)
            self.assertEqual(p.read_text(),'another project')


if __name__=='__main__':
    unittest.main(verbosity=2)

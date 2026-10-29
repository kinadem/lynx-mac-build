# LYNX High Sierra compatibility source audit

Target confirmed from the system screenshot: macOS 10.13.6, Intel Core 2 Duo,
4 GB RAM. No serial number or identifying hardware report is included here.

The source remains pinned to LYNX v0.1.19-alpha, commit
`18f0c18a46c3e2eec3f85268819810d5ecfb4e58`, with JUCE 8.0.4.

## Changes for this target

- Make Info.plist follow the selected compiler deployment target.
- Select generic x86-64 and macOS 10.13, with no global SSE4.2/AVX/AVX2/FMA
  requirement; keep the existing optional Harmor/Harmless AVX kernels disabled.
- Replace `std::filesystem` in FlpImport.cpp, SoundFont.cpp, SoundFontLoad.cpp,
  and SoundFontIndex.cpp with the pinned ghc::filesystem implementation and its
  compatible stream wrappers. High Sierra's libc++ lacks std::filesystem.
- Verify each source preimage before patching and verify the third-party header
  SHA-256. Keep the MIT notice with the installer.
- Leave compiler availability diagnostics enabled as errors for unguarded APIs.
- Retain a separate explicit Catalina build profile and its historical reports.

JUCE 8.0.4 declares Intel deployment support back to macOS 10.11. That is framework
support, not proof of this application's complete old-system compatibility.
The native application must build, self-test, pass Mach-O/plist checks, verify
its ad-hoc signature, and produce a verified DMG before it is offered for testing.
It still needs a real High Sierra launch and audio/MIDI/keyboard/project/export
trial. Third-party plugins need separate tests and must meet their own OS/CPU/RAM
requirements. The patch does not alter their binaries or licensing.

The upstream Mac host enables VST3 and Audio Units; Mac VST2 hosting and a
separate-process Mac plugin sandbox are not provided by this release.

## Dependency

- ghc::filesystem v1.5.14 (MIT)
- Commit: 8a2edd6d92ed820521d42c94d179462bf06b5ed3
- Header SHA-256: 522791c2a2f1959193fdff61f4668c5ba894459753170b2246971272ee8ddc47
- Source: https://github.com/gulrak/filesystem/tree/8a2edd6d92ed820521d42c94d179462bf06b5ed3

See the README, successful workflow's reports, and reports/ for actual validation
results. The earlier Linux-only preparation record is historical.

# LYNX for older Intel Macs

Build an experimental macOS 10.13+ Intel installer from the open-source
[LYNX](https://github.com/Ka1-S/LYNX) digital audio workstation.

The source is pinned to **v0.1.19-alpha**, commit
`18f0c18a46c3e2eec3f85268819810d5ecfb4e58`, with JUCE 8.0.4.
This repository contains the compatibility patch, build recipe, and checks.

## High Sierra / Core 2 target

The current target is **macOS High Sierra 10.13.6 on an Intel Core 2 Duo with
4 GB RAM**. The earlier Catalina DMG requires 10.15 and cannot run on High Sierra.
The High Sierra profile backports four source files' filesystem operations using
[ghc::filesystem v1.5.14](https://github.com/gulrak/filesystem/tree/8a2edd6d92ed820521d42c94d179462bf06b5ed3),
with pinned source hashes, a verified dependency checksum, and its MIT notice.
It keeps SDK availability checks enabled and compiles for generic x86-64 without
global SSE4.2/AVX/FMA requirements. Runtime-dispatched optimizations remain gated
by the upstream CPU checks. High Sierra runtime testing is still required.

## Build and download

The workflow runs on changes to the build files on `main`, or from
**Actions → Build LYNX Intel High Sierra candidate → Run workflow**.
It uses GitHub's standard `macos-15-intel` runner, creates an ad-hoc signed DMG,
and uploads the DMG, SHA-256 checksum, metadata report, and app self-test report
as the **LYNX-Intel-High-Sierra-CANDIDATE** artifact. Artifacts are retained for 7 days.
Standard GitHub-hosted build minutes are free for public repositories.

## Successful High Sierra-targeted build

[Build 40915498843](https://github.com/kinadem/lynx-mac-build/actions/runs/40915498843)
passed from recipe commit `a118e0fe77c75693fe7a095d0599686d40db159b`.
The app compiled with a 10.13 deployment target and unguarded newer-API warnings
as errors. Native app self-test, Intel/10.13 metadata checks, ad-hoc signature
verification and DMG verification passed on the modern Intel build host.
Downloaded artifact and DMG checksums matched. The DMG is **14,333,538 bytes**.

[High Sierra build reports and checksum](reports/2026-10-29-high-sierra/) record
the results. The filesystem backport also passed all **1,289,425 upstream core
checks** on Linux. Actual High Sierra launch, physical audio/MIDI and plugins
still require testing on the target machine; the build is a candidate.

## Earlier Catalina build (requires macOS 10.15+)

[Build 40909987245](https://github.com/kinadem/lynx-mac-build/actions/runs/40909987245)
passed on 29 October 2026, from build-recipe commit
`4dd0ec7fb327972da32e41e69ddb22c7d3dcf725`. The host ran macOS 15.7.9
with Xcode 16.4. Compilation, the app self-test (`result=OK`), ad-hoc signature
verification, Intel/10.15 metadata checks, and `hdiutil verify` passed.

The candidate DMG is **14,321,724 bytes**. Downloaded artifact and DMG checksums
matched the build outputs. [Reports and DMG checksum](reports/2026-10-29/)
record these results. The image is ad-hoc signed and is not notarized.

## Compatibility status

A successful workflow verifies the app on the modern Intel build host.
**It does not establish that it runs correctly on High Sierra or on a particular
older processor.** Launch, sound, keyboard/MIDI recording, save/reopen, WAV
export, and third-party plugins still require tests on the target Mac.

Mac VST3 and Audio Units use the existing LYNX plugin host. Nexus requires a
separately installed, licensed Mac plugin compatible with the target system.
Nexus is not bundled or tested by this workflow.

See [START_HERE.md](START_HERE.md), [Source_Audit.md](Source_Audit.md), and the
workflow's reports for the scope and evidence. LYNX is licensed under
[GNU AGPL v3](LYNX_LICENSE.txt); upstream attribution and third-party notices
are preserved in the installer.

# LYNX for Intel Mac / Catalina

Build an experimental macOS 10.15+ Intel installer from the open-source
[LYNX](https://github.com/Ka1-S/LYNX) digital audio workstation.

The source is pinned to **v0.1.19-alpha**, commit
`18f0c18a46c3e2eec3f85268819810d5ecfb4e58`, with JUCE 8.0.4.
This repository contains the compatibility patch, build recipe, and checks.

## Build and download

The workflow runs on changes to the build files on `main`, or from
**Actions → Build LYNX Intel Catalina candidate → Run workflow**.
It uses GitHub's standard `macos-15-intel` runner, creates an ad-hoc signed DMG,
and uploads the DMG, SHA-256 checksum, metadata report, and app self-test report
as the **LYNX-Intel-Catalina-CANDIDATE** artifact. Artifacts are retained for 7 days.
Standard GitHub-hosted build minutes are free for public repositories.

## First successful Mac build

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
**It does not establish that it runs correctly on Catalina or on a particular
older processor.** Launch, sound, keyboard/MIDI recording, save/reopen, WAV
export, and third-party plugins still require tests on the target Mac.

Mac VST3 and Audio Units use the existing LYNX plugin host. Nexus requires a
separately installed, licensed Mac plugin compatible with the target system.
Nexus is not bundled or tested by this workflow.

See [START_HERE.md](START_HERE.md), [Source_Audit.md](Source_Audit.md), and the
workflow's reports for the scope and evidence. LYNX is licensed under
[GNU AGPL v3](LYNX_LICENSE.txt); upstream attribution and third-party notices
are preserved in the installer.

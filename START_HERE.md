# LYNX Intel Mac compatibility kit

Prepared on 29 October 2026.

**Use an installer only from a successful GitHub Actions run, together with that run's metadata and self-test reports.** This repository contains the source changes and reproducible build recipe. A successful build is a compatibility candidate, not proof of Catalina runtime compatibility. The working target is an Intel Mac running macOS Catalina 10.15 or newer. The exact target model, processor, memory, and macOS version remain unconfirmed.

LYNX is already open source. This work uses its available C++ source to prepare an older-Mac port; decompiling its executable is unnecessary.

## Start on your Mac

1. Extract the ZIP fully.
2. Open `Check_My_Mac.command` with Terminal. It writes `Mac_Compatibility.txt` beside itself, showing the OS, model identifier, CPU, and memory. It makes no system changes, collects no serial number or account name, and uploads nothing.
3. Check that the computer is Intel and macOS is at least 10.15. An older OS needs a different port. Apple Silicon should use the official native LYNX build instead of this Intel profile.

The checker is not an installer. Do not change the operating system or disable system protections to run it. If macOS blocks it, its contents can be read first, then invoked in Terminal with `bash` and the script's full path.

## What was changed

- LYNX's app bundle previously stated macOS 11 explicitly even when the compiler target was lowered. The patch makes that field follow the actual compiler deployment target.
- The build recipe selects **Intel x86_64 and macOS 10.15**, uses conservative CPU instructions, and disables two optional AVX kernels for the older-CPU target.
- Keyboard playing, MIDI input, Piano roll, Channel rack, Playlist, audio rendering, VST3, and Mac Audio Units use the existing LYNX implementation.
- A validator rejects a generated app with the wrong CPU, newer minimum OS, inconsistent bundle metadata, or a developer-machine absolute library path. Metadata passing does not prove old-OS runtime compatibility.

## Build a candidate

This should be done on a Mac with a current Apple C++ toolchain and CMake 3.22 or newer. A modern Mac can compile for the older Intel target. Trying to install a new development toolchain on an old Catalina laptop may fail; the hosted build route avoids that problem.

**Local Mac build:** open Terminal in this extracted directory and run:

```bash
bash ./build_intel_catalina.sh
```

The script downloads the exact audited LYNX release into `work/LYNX`, applies the patch, builds and checks `LYNX.app`, runs its native self-test on the build Mac, then creates a candidate DMG and SHA-256 checksum in `work/output`. It does not install the app or overwrite an existing installed LYNX. Existing candidate DMGs receive distinct filenames on repeat builds.

**GitHub Mac build:** changes to the build files on `main` start the workflow automatically. A build can also be started from Actions → Build LYNX Intel Catalina candidate → Run workflow. Download the candidate artifact after a successful run and extract its DMG. The workflow uploads a build artifact and does not publish a release. Check the actual run for its status; the earlier source-audit results describe preparation before a hosted Mac build. GitHub documents standard hosted runners as free for public repositories; private repositories have their own usage limits and billing rules. See https://docs.github.com/en/actions/reference/runners/github-hosted-runners.

Keep the source notices and license. The build script pins LYNX 0.1.19-alpha to commit `18f0c18a46c3e2eec3f85268819810d5ecfb4e58`; it does not silently follow later releases.

## What still must pass on your Mac

Open the candidate; hear a built-in instrument; play/release notes from your computer keyboard and MIDI controller; record into the Piano roll; save, close, and reopen a project; export a WAV. Then test a small project with your actual installed Mac Nexus plugin and its library.

Nexus compatibility is separate from LYNX compatibility. This port does not convert Windows DLLs or 32-bit instruments into Mac plugins, change Nexus CPU/OS requirements, or include a Nexus license. The inspected LYNX Mac host enables VST3 and Audio Units. Plugin crashes are not isolated in a separate process on Mac in this release.

## Files

- `Source_Audit.md`: findings and module map.
- `catalina-metadata.patch` / `apply_compatibility.py`: the minimal source fix.
- `build_intel_catalina.sh`: pinned Mac build and packaging.
- `verify_mac_bundle.py`: architecture and deployment metadata checks.
- `Check_My_Mac.command`: read-only hardware/OS report.
- `test_kit.py`: compatibility-kit checks.
- `Validation_Results.txt`: checks actually completed in this session.
- `LYNX_LICENSE.txt`: upstream GNU AGPL v3 text. Upstream code and attribution remain intact.

This is an alpha-based compatibility candidate. Its readiness must be decided from a real run on your target Mac.

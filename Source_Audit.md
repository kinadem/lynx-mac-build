# LYNX source analysis for an older Intel Mac

Prepared on 29 October 2026. Scope: source inspection and a compatibility build kit; no Mac binary or physical-device validation was completed.

## Decision

A Catalina/Intel port is a reasonable candidate for compilation and runtime testing. The inspected source does not establish that the complete application needs Big Sur. There are explicit version settings to change and an older MIDI implementation to retain. Successful Linux core checks strengthen confidence in the conservative CPU configuration, but cannot establish Mac compatibility.

The actual target Mac has not been identified in this task. Intel x86_64 and macOS Catalina 10.15 are working assumptions. If its OS is older, this kit does not cover it. If its OS is 11 or newer, the official build may already be suitable.

## Audited versions

| Item | Pinned version |
|---|---|
| Repository | https://github.com/Ka1-S/LYNX |
| Release | v0.1.19-alpha |
| LYNX source commit | `18f0c18a46c3e2eec3f85268819810d5ecfb4e58` |
| JUCE | 8.0.4, source commit `51d11a2be6d5c97ccf12b4e5e827006e19f0555a` |
| Language | C++20 for LYNX |
| License | GNU AGPL v3, with third-party notices in the upstream repository |

The source was cloned and selected modules read directly. This is source analysis and port preparation, rather than reconstruction from a compiled executable. It is not an exhaustive audit of every synth engine or every operating-system call.

## Findings that affect this Mac port

**1. The operating-system minimum is declared twice.** Root `CMakeLists.txt` sets `CMAKE_OSX_DEPLOYMENT_TARGET` to 11.0 as a cache default. Separately, `juce_add_gui_app` merges an Info.plist fragment containing a literal `LSMinimumSystemVersion` of 11.0. Passing a lower compiler target alone leaves inconsistent app metadata. The supplied one-line patch makes the plist field use `${CMAKE_OSX_DEPLOYMENT_TARGET}`. The build recipe then supplies 10.15 explicitly. The ordinary default remains 11.0.

**2. Build Intel-only for this candidate.** The public release recipe builds both arm64 and x86_64. The candidate requests x86_64 and generic x86-64 code generation, with AVX/AVX2/FMA disabled as global compiler targets. Optional AVX kernels in Harmor and Harmless are also disabled using their existing source switches. This avoids relying on those optimizations on an older Intel processor. It does not change a third-party plugin's own CPU requirements.

**3. The pinned framework has a legacy CoreMIDI path.** JUCE 8.0.4's README lists older Intel deployment support. Its `modules/juce_audio_devices/native/juce_CoreMidi_mac.mm` chooses a new-API-only implementation for minimum OS 11+, and retains both old and new implementations for lower minimums. That is an important reason to recompile correctly instead of editing the version label on a prebuilt app.

**4. The worker wake-up mechanism is already Mac-specific.** `src/core/WorkerPool.cpp` uses libdispatch semaphores on Apple systems. I did not find a dependency on C++20 counting semaphores, jthread, or atomic wait/notify in the inspected LYNX source paths. That inspection is not a complete symbol-availability audit. The build recipe treats unguarded newer Apple API availability warnings as errors; a Catalina runtime check is still required for SDK/C++ runtime problems that compile-time checks miss.

**5. Mac plugin formats differ from Windows.** The Mac target enables JUCE Audio Units and VST3. `Vst2Format.cpp` contains Windows and Linux loading paths, not a Mac VST2 host. Existing Windows DLLs are not Mac instruments. `PluginSandbox.cpp` has no Mac separate-process host in this release, so the candidate should first be exercised with built-in instruments before loading third-party plugins.

**6. Building on the old laptop is not the only route.** LYNX requires C++20 and CMake >=3.22. The old Mac's last available Xcode may not be a suitable build toolchain. A newer Apple build host can target an older Intel OS. The included, manually triggered GitHub workflow uses an Intel Mac runner and uploads a candidate DMG; it has not been executed in this session.

## Source map for further development

| System | Files inspected or traced | Relevance |
|---|---|---|
| Deployment metadata | `CMakeLists.txt`, `scripts/package-macos.sh`, `.github/workflows/release.yml` | Compiler OS target, bundle minimum, architectures and packaging |
| Computer keyboard | `src/ui/MainComponent.cpp`, `src/core/KeyMap.cpp`, `src/core/KeyMap.h` | Notes are sent to selected channels; repeated keys are suppressed; release tracking prevents held notes surviving selection changes |
| MIDI input and recording | `src/engine/AudioEngine.cpp`, `src/core/Recorder.h` | Input channel selection, note queues, velocity and recording queues |
| Plugin adapter | `src/engine/PluginHost.cpp`, `src/engine/PluginHost.h` | Note-on/off MIDI, instance creation, saved state and render routing |
| CPU and workers | `src/core/WorkerPool.cpp`, `Simd.h`, `Harmor.cpp`, `Harmless.cpp` | Older-CPU settings, Mac semaphores and optional AVX code paths |
| Project files and export | Architecture documentation identifies `src/engine/ProjectFile.cpp`, `Exporter.cpp`, and `src/core/RackRenderer.cpp` | Native project persistence and audio export; full GUI-side round-trip testing remains a Mac task |

Piano roll, Channel rack, Playlist and Mixer remain native JUCE components under `src/ui/`. This kit prepares portability; it does not introduce a new interface or pretend to replace every FL Studio feature.

## Validation completed

Read `Validation_Results.txt` for the exact results. The pure C++ core was compiled on Linux x86_64 using conservative CPU settings, and its upstream test program completed 1,289,425 checks with zero failures. No external FL Studio projects or Nexus installations were provided.

The first CMake test build exposed an upstream test-harness macro conflict: GNU-extension C++ mode defines `unix`, while one test declares a local variable of that name. The test translation unit was then compiled in strict `-std=c++20` mode, matching the upstream local-build script's language mode, against the already compiled core. No assertions were removed. The Mac build recipe requests strict C++ mode too.

Five compatibility-kit test methods passed. These exercise accepted/rejected Mach-O metadata, architecture, OS minimum, malformed input, nonportable library paths, and idempotent patch application. Their Mach-O inputs are synthetic fixtures, not a Mac executable produced here. Both shell scripts passed syntax checks.

## Remaining acceptance gate

A real Mac build must pass compilation, the native app self-test, signing integrity, and the bundle metadata validator. Then the actual target Mac must pass launch, Core Audio output, typing-keyboard note release, MIDI input, Piano roll recording, project save/reopen, and WAV export. The user's installed Mac Nexus plugin must separately pass loading, preset selection, live notes, reopening and export.

This session ran on Linux and had no Apple SDK, Xcode, Core Audio device, or Nexus binary. A DMG was not fabricated or relabeled. A passing candidate metadata report must never be described as certified Catalina compatibility.

## Primary references

- Pinned LYNX source: https://github.com/Ka1-S/LYNX/tree/18f0c18a46c3e2eec3f85268819810d5ecfb4e58
- Build configuration: https://github.com/Ka1-S/LYNX/blob/18f0c18a46c3e2eec3f85268819810d5ecfb4e58/CMakeLists.txt
- Architecture: https://github.com/Ka1-S/LYNX/blob/18f0c18a46c3e2eec3f85268819810d5ecfb4e58/docs/ARCHITECTURE.md
- Platform notes: https://github.com/Ka1-S/LYNX/blob/18f0c18a46c3e2eec3f85268819810d5ecfb4e58/docs/PLATFORMS.md
- Pinned JUCE: https://github.com/juce-framework/JUCE/tree/51d11a2be6d5c97ccf12b4e5e827006e19f0555a
- Hosted Mac runners: https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- Nexus requirements: https://refx.com/nexus

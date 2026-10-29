# LYNX for High Sierra / older Intel Mac

The current target is macOS High Sierra 10.13.6 on a Core 2 Duo / 4 GB machine.
The previous Catalina candidate requires macOS 10.15; use a filename containing
`high-sierra` on a system running 10.13.6.

Download a DMG only from a successful **Build LYNX Intel High Sierra candidate**
GitHub Actions run. Extract the workflow artifact, open its DMG, and drag LYNX
into Applications. See [INSTALLATION.md](INSTALLATION.md) for the first tests.

The host can build and self-test the app, verify its signature, validate Intel
and minimum-OS metadata, and check its disk image. Those checks cannot establish
that the app runs correctly on the target older Mac or with third-party plugins.

## Build from source

On a modern Mac with Xcode, CMake, Git, and Python 3:

```bash
bash ./build_intel_mac.sh
```

The default target is 10.13. To explicitly select the previous 10.15 profile:

```bash
bash ./build_intel_catalina.sh
```

The build uses LYNX v0.1.19-alpha at commit
`18f0c18a46c3e2eec3f85268819810d5ecfb4e58` and JUCE 8.0.4. The High Sierra
profile downloads ghc::filesystem v1.5.14 from its pinned commit and verifies its
SHA-256 before changing the four filesystem users. License notices are bundled.
Compilation treats unguarded newer Apple API warnings as errors.

Nexus is separate. Its version must support this OS, CPU and installed memory;
changing the host's deployment target does not change the plugin's requirements.
Use built-in sounds for the first launch/record/save/export test.

# LYNX older Intel Mac candidate

Open the DMG and drag LYNX into Applications. The filename identifies the target:
`high-sierra` targets macOS 10.13+, while `catalina` targets macOS 10.15+.
Use the High Sierra file on a Mac running 10.13.6.

The app is ad-hoc signed, without Apple notarization. The installer contains the
application and license notices; Nexus and third-party sound libraries are separate.

First test a built-in instrument, computer-keyboard note-on/off, recording into
the Piano roll, saving/reopening a project, and WAV export. Use a small project
on a Core 2 Duo / 4 GB machine. Plugin compatibility depends on each plugin's own
OS, CPU instruction and memory requirements.

Successful build-host checks do not prove that the app runs on the older target
Mac. Refer to the reports from the corresponding GitHub Actions run.

Source: https://github.com/kinadem/lynx-mac-build
Upstream LYNX: https://github.com/Ka1-S/LYNX
LYNX source revision: 18f0c18a46c3e2eec3f85268819810d5ecfb4e58

The High Sierra profile uses gulrak/filesystem v1.5.14 under its MIT license to
replace file operations missing from High Sierra's libc++. The implementation is
pinned to commit 8a2edd6d92ed820521d42c94d179462bf06b5ed3 and checksum verified.

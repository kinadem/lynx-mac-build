#!/usr/bin/env bash
# LYNX 0.1.19 alpha -> an Intel/Catalina CANDIDATE build. AGPL-3.0.
# Build on a Mac with current Xcode/Apple Clang and CMake >=3.22. Never changes your OS or installed LYNX.
set -euo pipefail
if [[ "$(uname -s)" != Darwin ]]; then
    printf '%s\n' 'An Apple macOS build host with Xcode is required. Linux cannot build this application with the tools in this kit.' >&2
    exit 2
fi
KIT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR="${LYNX_MAC_WORKDIR:-$KIT_DIR/work}"
SOURCE_DIR="$WORK_DIR/LYNX"
BUILD_DIR="$WORK_DIR/build"
OUT_DIR="$WORK_DIR/output"
UPSTREAM_SHA=18f0c18a46c3e2eec3f85268819810d5ecfb4e58
UPSTREAM_TAG=v0.1.19-alpha
for tool in git cmake python3 xcrun codesign hdiutil ditto shasum; do
    command -v "$tool" >/dev/null || { printf 'Missing build tool: %s\n' "$tool" >&2; exit 2; }
done
xcrun --find clang++ >/dev/null
mkdir -p "$WORK_DIR" "$OUT_DIR"
if [[ ! -d "$SOURCE_DIR/.git" ]]; then
    git clone --depth 1 --branch "$UPSTREAM_TAG" https://github.com/Ka1-S/LYNX.git "$SOURCE_DIR"
fi
actual_sha="$(git -C "$SOURCE_DIR" rev-parse HEAD)"
[[ "$actual_sha" == "$UPSTREAM_SHA" ]] || { printf '%s\n' 'Source revision differs from the audited release. No build attempted.' >&2; exit 2; }
# Keep the download and upstream notices intact; patch only the bundle minimum-version field.
python3 "$KIT_DIR/apply_compatibility.py" "$SOURCE_DIR"
PORTABLE_FLAGS='-O2 -DNDEBUG -march=x86-64 -mtune=generic -mno-avx -mno-avx2 -mno-fma'
cmake -S "$SOURCE_DIR" -B "$BUILD_DIR" -G 'Unix Makefiles' \
    -DCMAKE_BUILD_TYPE=Release -DLYNX_BUILD_APP=ON -DCMAKE_CXX_EXTENSIONS=OFF \
    -DCMAKE_OSX_DEPLOYMENT_TARGET=10.15 -DCMAKE_OSX_ARCHITECTURES=x86_64 \
    -DCMAKE_C_FLAGS_RELEASE="$PORTABLE_FLAGS" \
    -DCMAKE_CXX_FLAGS_RELEASE="$PORTABLE_FLAGS -DHARMOR_NO_AVX -DHARMLESS_NO_AVX" \
    -DCMAKE_CXX_FLAGS=-Werror=unguarded-availability-new
cmake --build "$BUILD_DIR" --target LYNX --parallel "${LYNX_BUILD_JOBS:-2}"
APP="$BUILD_DIR/LYNX_artefacts/Release/LYNX.app"
[[ -d "$APP" ]] || { printf '%s\n' 'The expected LYNX.app was not produced.' >&2; exit 1; }
python3 "$KIT_DIR/verify_mac_bundle.py" "$APP" --json "$OUT_DIR/Metadata_Check.json"
# Exercise native application code on the build Mac. This is NOT a run on Catalina.
"$APP/Contents/MacOS/LYNX" --selftest "$OUT_DIR/Mac_Build_Host_Selftest.txt" "$OUT_DIR/Test_Project.lynx"
grep -q '^result=OK' "$OUT_DIR/Mac_Build_Host_Selftest.txt"
STAGE_DIR="$(mktemp -d "$WORK_DIR/stage.XXXXXX")"
trap 'rm -rf "$STAGE_DIR"' EXIT
ditto "$APP" "$STAGE_DIR/LYNX.app"
codesign --force --deep --sign - "$STAGE_DIR/LYNX.app"
codesign --verify --deep --strict "$STAGE_DIR/LYNX.app"
python3 "$KIT_DIR/verify_mac_bundle.py" "$STAGE_DIR/LYNX.app" --json "$OUT_DIR/Metadata_Check.json"
ln -s /Applications "$STAGE_DIR/Applications"
cp "$SOURCE_DIR/LICENSE" "$STAGE_DIR/LYNX_LICENSE.txt"
cp "$SOURCE_DIR/THIRD_PARTY.md" "$STAGE_DIR/THIRD_PARTY.md"
cp "$KIT_DIR/START_HERE.md" "$STAGE_DIR/START_HERE.md"
DMG="$OUT_DIR/LYNX-0.1.19-alpha-catalina-intel-CANDIDATE.dmg"
if [[ -e "$DMG" ]]; then
    DMG="$OUT_DIR/LYNX-0.1.19-alpha-catalina-intel-CANDIDATE-$(date +%Y%m%d-%H%M%S).dmg"
fi
hdiutil create -volname 'LYNX Catalina candidate' -srcfolder "$STAGE_DIR" -fs HFS+ -format UDZO "$DMG"
hdiutil verify "$DMG"
shasum -a 256 "$DMG" > "$DMG.sha256"
printf '\nCandidate created: %s\nThis is not certified Catalina/Nexus compatibility; test it on the target Mac.\n' "$DMG"

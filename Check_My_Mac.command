#!/bin/bash
# Read-only hardware/OS check. Writes a report beside this script; no serial number, login name, or network upload.
set -eu
if [[ "$(uname -s)" != Darwin ]]; then
    printf '%s\n' 'Run this checker on your Mac.' >&2
    exit 2
fi
TASK_DIR="$(cd "$(dirname "$0")" && pwd)"
REPORT="$TASK_DIR/Mac_Compatibility.txt"
{
    printf '%s\n' 'LYNX compatibility information (no serial number or account name)'
    printf '\nmacOS version: '; sw_vers -productVersion
    printf 'Architecture: '; uname -m
    printf 'Model identifier: '; sysctl -n hw.model
    printf 'Processor: '; sysctl -n machdep.cpu.brand_string 2>/dev/null || true
    printf 'Memory in bytes: '; sysctl -n hw.memsize
    printf 'CPU features: '; sysctl -n machdep.cpu.features 2>/dev/null || true
    printf '\n%s\n' 'Current candidate target: Intel x86_64, macOS 10.13 or newer.'
    printf '%s\n' 'A successful build still requires a runtime test on the actual target Mac.'
    printf '%s\n' 'Nexus requires its own matching Mac plugin, supported CPU/OS, license and sound library.'
} > "$REPORT"
cat "$REPORT"
printf '\nSaved report: %s\n' "$REPORT"

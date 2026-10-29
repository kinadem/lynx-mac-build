#!/usr/bin/env bash
# Retain the previous 10.15 profile as an explicit opt-in.
set -euo pipefail
export LYNX_MACOS_TARGET=10.15
exec bash "$(cd "$(dirname "$0")" && pwd)/build_intel_mac.sh"

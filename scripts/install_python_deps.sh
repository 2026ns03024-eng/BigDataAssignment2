#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 -m ensurepip --user --upgrade 2>/dev/null || true
python3 -m pip install --user --upgrade pip 2>/dev/null || true
python3 -m pip install --user -r "$ROOT/requirements.txt"
echo "Installed packages for $(whoami)"

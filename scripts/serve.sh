#!/usr/bin/env bash
# The Night Library — static files + same-origin illustrator proxy (see serve.py).
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 scripts/serve.py

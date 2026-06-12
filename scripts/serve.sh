#!/usr/bin/env bash
# The Night Library — local static server. The writer (llama-server :8080) and the
# optional illustrator (Bonsai-Image-Demo :8800) run as their own processes.
set -euo pipefail
cd "$(dirname "$0")/.."
echo "The Night Library → http://127.0.0.1:8400/web/"
echo "  writer:      llama-server on :8080 (required)"
echo "  illustrator: Bonsai-Image-Demo on :8800 (optional — dream canvas otherwise)"
exec python3 -m http.server 8400 --bind 127.0.0.1

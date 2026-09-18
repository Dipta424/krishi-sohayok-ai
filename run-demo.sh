#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/backend"
if [[ ! -d venv ]]; then
  echo "Missing backend/venv — run: cd backend && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"
  exit 1
fi
# shellcheck disable=SC1091
source venv/bin/activate
echo "Krishi Sohayok — open http://localhost:8000 (API keys optional; fallbacks enabled)"
exec uvicorn main:app --host 0.0.0.0 --port 8000

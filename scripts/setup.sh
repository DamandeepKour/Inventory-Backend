#!/usr/bin/env bash
# One-time setup: create venv and install dependencies.
set -e
cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

echo "Installing dependencies..."
.venv/bin/pip install -r app/requirements.txt

echo ""
echo "Setup complete. Activate the venv with:"
echo "  source .venv/bin/activate"
echo ""
echo "Then run (with Postgres running):"
echo "  python3 scripts/init_db.py"
echo "  python3 scripts/sync_db.py"
echo "  python3 scripts/seed_db.py"
echo ""
echo "Start the API:"
echo "  cd app && ../.venv/bin/uvicorn main:app --reload"

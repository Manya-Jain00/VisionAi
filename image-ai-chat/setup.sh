#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────
# setup.sh — One-time setup for Image AI Chat (Linux / macOS)
#
# Usage:  chmod +x setup.sh && ./setup.sh
# ──────────────────────────────────────────────────────────
set -e

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║        Image AI Chat — Setup Script             ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# 1. Check Python 3
if ! command -v python3 &>/dev/null; then
  echo "❌  Python 3 not found. Please install Python 3.9+ first."
  echo "    https://www.python.org/downloads/"
  exit 1
fi

PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓  Python found: $PY_VERSION"

# 2. Create virtual environment
if [ ! -d "venv" ]; then
  echo ""
  echo "→  Creating virtual environment …"
  python3 -m venv venv
  echo "✓  Virtual environment created (./venv)"
else
  echo "✓  Virtual environment already exists."
fi

# 3. Activate venv
source venv/bin/activate
echo "✓  Virtual environment activated."

# 4. Upgrade pip silently
pip install --upgrade pip --quiet

# 5. Install dependencies
echo ""
echo "→  Installing Python dependencies (this may take a few minutes) …"
pip install -r requirements.txt
echo ""
echo "✓  All dependencies installed."

# 6. Create uploads folder
mkdir -p uploads
echo "✓  uploads/ folder ready."

echo ""
echo "══════════════════════════════════════════════════"
echo "  ✅  Setup complete!"
echo ""
echo "  To run the app:"
echo "    source venv/bin/activate"
echo "    python app.py"
echo ""
echo "  Then open:  http://127.0.0.1:5000"
echo "══════════════════════════════════════════════════"
echo ""

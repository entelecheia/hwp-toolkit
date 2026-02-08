#!/bin/bash
# HWP Toolkit - Dependency Setup Script for macOS
# Installs all required packages for HWP/HWPX processing

set -e

echo "=== HWP Toolkit: Installing Dependencies (macOS) ==="

# Python packages
echo "[1/3] Installing Python packages..."
pip3 install --user olefile pyhwp pyhwp2md python-hwpx gethwp weasyprint markdown 2>&1 | tail -10

# Node.js md2hwp (install in skill directory)
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "[2/3] Installing md2hwp (Node.js) in $SKILL_DIR..."
cd "$SKILL_DIR"
if [ ! -d "node_modules/md2hwp" ]; then
    npm install 2>&1 | tail -5
else
    echo "  md2hwp already installed."
fi

# unhwp CLI (Rust binary) - macOS support
echo "[3/3] Checking unhwp CLI..."
if command -v unhwp &>/dev/null; then
    echo "  unhwp already installed: $(unhwp --version)"
else
    echo "  NOTE: unhwp is not available as a pre-built binary for macOS."
    echo "  If you need unhwp, install it via cargo:"
    echo "    cargo install unhwp"
    echo "  Or use the Python-based tools instead (pyhwp2md, gethwp)."
fi

echo ""
echo "=== Setup Complete (macOS) ==="
echo "Installed tools:"
echo "  ✓ pyhwp (hwp5txt, hwp5html, hwp5odt)"
echo "  ✓ pyhwp2md (HWP/HWPX → Markdown)"
echo "  ✓ python-hwpx (HWPX read/write/edit)"
echo "  ✓ gethwp (HWP/HWPX text extraction)"
echo "  ✓ weasyprint (HTML → PDF conversion)"
echo "  ✓ markdown (Markdown processing)"
echo "  ✓ md2hwp (Markdown → HWPX via Node.js)"
echo "  - unhwp (optional, install via cargo if needed)"
echo ""
echo "You can now use the HWP toolkit scripts!"

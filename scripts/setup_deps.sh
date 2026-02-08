#!/bin/bash
# HWP Toolkit - Dependency Setup Script
# Installs all required packages for HWP/HWPX processing

set -e

echo "=== HWP Toolkit: Installing Dependencies ==="

# Python packages
echo "[1/3] Installing Python packages..."
sudo pip3 install olefile pyhwp pyhwp2md python-hwpx gethwp 2>&1 | tail -5

# Node.js md2hwp (install in skill directory)
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "[2/3] Installing md2hwp (Node.js) in $SKILL_DIR..."
cd "$SKILL_DIR"
if [ ! -d "node_modules/md2hwp" ]; then
    npm install md2hwp 2>&1 | tail -3
else
    echo "  md2hwp already installed."
fi

# unhwp CLI (Rust binary)
echo "[3/3] Installing unhwp CLI..."
if command -v unhwp &>/dev/null; then
    echo "  unhwp already installed: $(unhwp --version)"
else
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        RELEASE_URL=$(curl -sL https://api.github.com/repos/iyulab/unhwp/releases/latest | python3 -c "import json,sys; data=json.load(sys.stdin); urls=[a['browser_download_url'] for a in data.get('assets',[]) if 'linux' in a['name']]; print(urls[0] if urls else '')")
        if [ -n "$RELEASE_URL" ]; then
            curl -sL "$RELEASE_URL" -o /tmp/unhwp.tar.gz
            tar -xzf /tmp/unhwp.tar.gz -C /tmp/
            sudo mv /tmp/unhwp /usr/local/bin/
            rm -f /tmp/unhwp.tar.gz
            echo "  unhwp installed: $(unhwp --version)"
        else
            echo "  WARNING: Could not find unhwp release URL"
        fi
    else
        echo "  WARNING: unhwp binary not available for $ARCH"
    fi
fi

echo ""
echo "=== Setup Complete ==="
echo "Installed tools:"
echo "  - pyhwp (hwp5txt, hwp5html, hwp5odt)"
echo "  - pyhwp2md (HWP/HWPX → Markdown)"
echo "  - python-hwpx (HWPX read/write/edit)"
echo "  - gethwp (HWP/HWPX text extraction)"
echo "  - md2hwp (Markdown → HWPX via Node.js)"
echo "  - unhwp (HWP/HWPX → Markdown/Text/JSON)"

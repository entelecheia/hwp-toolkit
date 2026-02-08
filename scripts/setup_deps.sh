#!/bin/bash
# HWP Toolkit - Universal Dependency Setup Script
# Automatically detects OS and runs the appropriate setup script

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected OS: Linux"
    bash "$SCRIPT_DIR/setup_deps_linux.sh"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected OS: macOS"
    bash "$SCRIPT_DIR/setup_deps_macos.sh"
else
    echo "Error: Unsupported OS: $OSTYPE"
    echo "This toolkit supports Linux and macOS only."
    exit 1
fi

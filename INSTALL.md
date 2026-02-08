# Installation Guide

## Quick Start

### 1. Install System Dependencies (macOS only)

```bash
brew install gobject-introspection cairo pango gdk-pixbuf libffi
```

### 2. Setup Python Environment

**Using uv (recommended):**
```bash
uv venv
uv pip install -r requirements.txt
```

**Using pip:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Install Node.js Dependencies

```bash
npm install
```

### 4. Activate Environment

```bash
source .venv/bin/activate
```

The activation script automatically configures the library paths for WeasyPrint.

## Verification

Test that all packages are working:

```bash
python -c "import olefile, hwpx, gethwp, markdown; print('✓ Core packages OK')"
python -c "import weasyprint; print('✓ WeasyPrint OK')"
```

## Troubleshooting

### WeasyPrint Import Error

If you see `OSError: cannot load library 'libgobject-2.0-0'`:

1. Ensure Homebrew libraries are installed:
   ```bash
   brew list | grep -E "(gobject|cairo|pango)"
   ```

2. Check that the activate script includes the library path:
   ```bash
   grep DYLD_FALLBACK_LIBRARY_PATH .venv/bin/activate
   ```

3. Manually set the environment variable:
   ```bash
   export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_FALLBACK_LIBRARY_PATH"
   ```

### Using direnv (Optional)

For automatic environment setup when entering the directory:

```bash
# Install direnv
brew install direnv

# Allow the .envrc file
direnv allow
```

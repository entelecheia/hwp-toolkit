# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a toolkit for processing Korean HWP (Hangul Word Processor) and HWPX files. The toolkit provides command-line utilities to read, create, convert, edit, and analyze HWP/HWPX documents in environments where the Hangul office suite is not available (primarily Linux).

The toolkit wraps multiple Python libraries and external tools (Node.js md2hwp, unhwp CLI) into a cohesive set of scripts.

## Setup

Before using or testing any scripts, run the setup script to install all dependencies:

```bash
bash scripts/setup_deps.sh
```

This installs:
- Python packages: `olefile`, `pyhwp`, `pyhwp2md`, `python-hwpx`, `gethwp`, `weasyprint`, `markdown`
- Node.js package: `md2hwp` (installed in repository root's node_modules/)
- CLI tool: `unhwp` (Rust binary, x86_64 Linux only)

## Architecture

### File Format Support

- **HWP files (.hwp)**: Binary OLE2 format with compressed/encrypted sections
- **HWPX files (.hwpx)**: XML-based ZIP archive format (newer, easier to work with)

### Core Scripts

All scripts are in `scripts/` and are standalone Python executables:

1. **`hwp_read.py`** - Extract text content
   - Primary: Uses `pyhwp2md` for both HWP and HWPX
   - Fallback: `python-hwpx` for HWPX, custom `olefile` parser for HWP
   - Output formats: Markdown (default), text, JSON

2. **`hwp_create.py`** - Create new HWPX files
   - Two methods:
     - `--method python-hwpx` (default): Fast, limited formatting, good for structured data
     - `--method md2hwp`: Better Markdown support (headings, lists, formatting), requires Node.js
   - Input sources: `--body` (text), `--markdown` (file), `--markdown-text` (string), `--json` (structured)
   - Note: Only creates HWPX (not HWP)

3. **`hwp_convert.py`** - Convert to other formats
   - Targets: PDF, HTML, Markdown, plain text, ODT
   - PDF workflow: HWP/HWPX → Markdown → HTML → WeasyPrint → PDF
   - ODT conversion: Uses `hwp5odt` CLI (HWP files only)

4. **`hwp_edit.py`** - Modify existing HWPX files
   - Operations: text replacement (`--replace`), add paragraph (`--add-paragraph`), add table (`--add-table`), add memo/comment (`--add-memo`)
   - Uses `gethwp` for text replacement, `python-hwpx` for structural changes
   - Note: Only works with HWPX (not HWP)

5. **`hwp_analyze.py`** - Inspect file structure
   - For HWP: Shows OLE2 streams, metadata (version, compression, encryption), record tag statistics
   - For HWPX: Shows ZIP entries, section count, image count, paragraph count
   - Output: JSON structure summary

### Key Dependencies

- **`pyhwp2md`**: Primary tool for reading HWP/HWPX and converting to Markdown
- **`python-hwpx`**: Library for creating and editing HWPX files programmatically
- **`olefile`**: Low-level HWP (OLE2) file parsing
- **`gethwp`**: Text replacement in HWPX files
- **`md2hwp`**: Node.js module for Markdown → HWPX conversion with rich formatting
- **`weasyprint`**: HTML → PDF conversion
- **`pyhwp`**: Provides CLI tools (`hwp5txt`, `hwp5html`, `hwp5odt`)

### Important Technical Details

#### HWP File Structure
- OLE2 compound file format
- Key streams: `FileHeader`, `BodyText/Section0`, `BodyText/Section1`, ..., `PrvText`, `BinData/*`
- Records are tagged with IDs: tag 67 = PARA_TEXT, tag 80 = TABLE
- Text is UTF-16LE encoded with control codes
- Sections can be zlib-compressed (flag in FileHeader byte 36)

#### HWPX File Structure
- ZIP archive with XML files
- Key entries: `mimetype`, `version.xml`, `Contents/section*.xml`, `BinData/*`
- Easier to parse than HWP

#### Markdown Conversion Strategy
The toolkit prefers a two-step approach:
1. HWP/HWPX → Markdown (using `pyhwp2md`)
2. Markdown → HTML or PDF (using `markdown` + `weasyprint`)

This provides better cross-format compatibility than direct conversion.

## Testing Scripts

To test individual scripts:

```bash
# Read a file
python3 scripts/hwp_read.py path/to/file.hwp

# Create from Markdown
python3 scripts/hwp_create.py output.hwpx --markdown input.md --method md2hwp

# Convert to PDF
python3 scripts/hwp_convert.py input.hwpx --to pdf -o output.pdf

# Edit (replace text)
python3 scripts/hwp_edit.py input.hwpx output.hwpx --replace "old" "new"

# Analyze structure
python3 scripts/hwp_analyze.py file.hwp
```

## Important Constraints

- **HWPX-only operations**: `hwp_create.py` and `hwp_edit.py` only work with HWPX format
- **HWP-only operations**: ODT conversion (`--to odt`) only works with HWP files
- **Node.js dependency**: `--method md2hwp` requires `md2hwp` to be installed in `node_modules/`
- **Linux focus**: The `unhwp` CLI tool and `hwp5odt` are primarily for Linux environments

## Skill Integration

This repository is also packaged as a Claude Code skill (see `SKILL.md`). The skill provides the same functionality but with hardcoded absolute paths for the scripts directory (`/Users/yj.lee/workspace/projects/hwp-toolkit/scripts/`).

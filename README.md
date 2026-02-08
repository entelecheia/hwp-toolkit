# HWP Toolkit

A comprehensive toolkit for processing Korean HWP (Hangul Word Processor) and HWPX files. This toolkit provides command-line utilities to read, create, convert, edit, and analyze HWP/HWPX documents in environments where the Hangul office suite is not installed.

## Features

- **Read** - Extract text content from HWP/HWPX files to Markdown, plain text, or JSON
- **Create** - Generate new HWPX files from Markdown, plain text, or structured JSON data
- **Convert** - Convert HWP/HWPX files to PDF, HTML, Markdown, ODT, or plain text
- **Edit** - Modify existing HWPX files (text replacement, add paragraphs, tables, memos)
- **Analyze** - Inspect file structure and extract metadata

## Quick Start

### Installation

Install all required dependencies:

```bash
bash scripts/setup_deps.sh
```

This installs:
- Python packages: `olefile`, `pyhwp`, `pyhwp2md`, `python-hwpx`, `gethwp`, `weasyprint`, `markdown`
- Node.js package: `md2hwp`
- CLI tool: `unhwp` (Linux x86_64 only)

### Basic Usage

**Read a HWP/HWPX file:**
```bash
python3 scripts/hwp_read.py document.hwp
```

**Create HWPX from Markdown:**
```bash
python3 scripts/hwp_create.py output.hwpx --markdown input.md --method md2hwp
```

**Convert to PDF:**
```bash
python3 scripts/hwp_convert.py document.hwpx --to pdf -o output.pdf
```

**Edit a file (replace text):**
```bash
python3 scripts/hwp_edit.py input.hwpx output.hwpx --replace "old text" "new text"
```

**Analyze file structure:**
```bash
python3 scripts/hwp_analyze.py document.hwp
```

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `hwp_read.py` | Extract text content from HWP/HWPX files |
| `hwp_create.py` | Create new HWPX files from various sources |
| `hwp_convert.py` | Convert HWP/HWPX to PDF, HTML, Markdown, ODT, or text |
| `hwp_edit.py` | Modify existing HWPX files |
| `hwp_analyze.py` | Inspect file structure and metadata |
| `setup_deps.sh` | Install all required dependencies |

## File Format Support

- **HWP (.hwp)** - Binary OLE2 format used by older versions of Hangul Word Processor
- **HWPX (.hwpx)** - XML-based ZIP format used by newer versions (easier to work with)

Note: Some operations (create, edit) only support HWPX format.

## Claude Code Skill

This toolkit is also available as a [Claude Code](https://claude.ai/code) skill for seamless integration with AI-assisted workflows.

## Documentation

- [SKILL.md](SKILL.md) - Detailed usage guide and examples
- [CLAUDE.md](CLAUDE.md) - Architecture and technical documentation
- [references/hwp_format_reference.md](references/hwp_format_reference.md) - HWP/HWPX file format specifications

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

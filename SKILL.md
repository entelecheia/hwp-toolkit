---
name: hwp-toolkit
description: A comprehensive toolkit for processing HWP and HWPX files. Use for reading, creating, editing, converting, and analyzing Korean word processor documents. Supports conversion to PDF, Markdown, HTML, and text. Ideal for tasks involving HWP/HWPX files on a Linux environment where the Hangul office suite is not installed.
---

# HWP/HWPX Toolkit

This skill provides a suite of command-line tools to read, create, edit, convert, and analyze Hangul Word Processor (HWP and HWPX) files in a Linux environment.

## One-Time Setup

Before using any scripts for the first time, run the setup script to install all required dependencies (Python packages, Node.js modules, and CLI tools).

```bash
bash /Users/yj.lee/workspace/projects/hwp-toolkit/scripts/setup_deps.sh
```

## Core Capabilities & Scripts

This skill includes several Python scripts located in the `scripts/` directory. Use them to perform specific actions on HWP/HWPX files.

| Task | Script | Description |
|---|---|---|
| **Read Content** | `hwp_read.py` | Extracts text from HWP/HWPX files into Markdown. |
| **Create Document** | `hwp_create.py` | Creates new HWPX files from text, Markdown, or JSON data. |
| **Convert Format** | `hwp_convert.py` | Converts HWP/HWPX files to PDF, HTML, Markdown, ODT, or TXT. |
| **Edit Document** | `hwp_edit.py` | Performs edits on HWPX files, such as text replacement. |
| **Analyze Structure** | `hwp_analyze.py` | Shows metadata and structural information about a file. |

---

## Scripts Reference

### 1. Read HWP/HWPX Content

Use `hwp_read.py` to extract the textual content from a document into Markdown format. This is the best starting point for understanding a document's contents.

**Usage:**
```bash
python3 /Users/yj.lee/workspace/projects/hwp-toolkit/scripts/hwp_read.py <input_file.hwp_or_hwpx>
```

**Example:**
```bash
# Read the content of a report and print as Markdown
python3 /Users/yj.lee/workspace/projects/hwp-toolkit/scripts/hwp_read.py "/path/to/report.hwp"
```

### 2. Create HWPX Documents

Use `hwp_create.py` to generate new `.hwpx` files. You can create them from plain text, structured JSON, or Markdown.

**Key Methods:**
- **`--method python-hwpx` (Default):** Good for creating simple documents with paragraphs and tables from structured data. It is fast but has limited formatting support.
- **`--method md2hwp`:** Recommended for converting Markdown. It provides better support for headings, lists, and text formatting (bold, italic).

**Examples:**

*   **From Markdown (Recommended Method):**
    ```bash
    # Create an HWPX file from a Markdown file, preserving formatting
    python3 /Users/yj.lee/workspace/projects/hwp-toolkit/scripts/hwp_create.py "output.hwpx" --markdown "/path/to/input.md" --method md2hwp --title "Document Title"
    ```

*   **From Plain Text:**
    ```bash
    # Create a simple HWPX file from a string
    python3 /Users/yj.lee/workspace/projects/hwp-toolkit/scripts/hwp_create.py "output.hwpx" --title "Simple Doc" --body "This is the first paragraph.\nThis is the second."
    ```

*   **From JSON:**
    ```bash
    # Create an HWPX file from a structured JSON file
    python3 /Users/yj.lee/workspace/projects/hwp-toolkit/scripts/hwp_create.py "output.hwpx" --json "/path/to/data.json"
    ```

### 3. Convert HWP/HWPX to Other Formats

Use `hwp_convert.py` to convert HWP/HWPX files into more common formats like PDF, HTML, or plain text.

**Recommended Workflow: Convert to PDF**

The most reliable way to convert to PDF is via an HTML intermediate step. The script handles this automatically.

```bash
# Convert any HWP or HWPX file to PDF
python3 /Users/yj.lee/workspace/projects/hwp-toolkit/scripts/hwp_convert.py "/path/to/document.hwpx" --to pdf -o "/path/to/output.pdf"
```

**Other Formats:**

```bash
# Convert to HTML
python3 /Users/yj.lee/workspace/projects/hwp-toolkit/scripts/hwp_convert.py "doc.hwp" --to html

# Convert to Markdown
python3 /Users/yj.lee/workspace/projects/hwp-toolkit/scripts/hwp_convert.py "doc.hwpx" --to md

# Convert HWP to ODT (only for .hwp files)
python3 /Users/yj.lee/workspace/projects/hwp-toolkit/scripts/hwp_convert.py "doc.hwp" --to odt
```

### 4. Edit HWPX Documents

Use `hwp_edit.py` to make modifications to existing `.hwpx` files. This script works only with the HWPX format.

**Examples:**

*   **Replace Text:**
    ```bash
    # Find and replace all occurrences of a string
    python3 /Users/yj.lee/workspace/projects/hwp-toolkit/scripts/hwp_edit.py "input.hwpx" "output.hwpx" --replace "old text" "new text"
    ```

*   **Add a Paragraph:**
    ```bash
    # Add a new paragraph to the end of the document
    python3 /Users/yj.lee/workspace/projects/hwp-toolkit/scripts/hwp_edit.py "input.hwpx" "output.hwpx" --add-paragraph "This is a new paragraph."
    ```

### 5. Analyze File Structure

Use `hwp_analyze.py` to get a JSON summary of a file's internal structure, including metadata, streams (for HWP), or XML entries (for HWPX).

**Usage:**
```bash
python3 /Users/yj.lee/workspace/projects/hwp-toolkit/scripts/hwp_analyze.py "/path/to/document.hwp"
```

---

## Technical Details

For a deeper understanding of the HWP and HWPX file formats, refer to the bundled reference document:

- `/Users/yj.lee/workspace/projects/hwp-toolkit/references/hwp_format_reference.md`

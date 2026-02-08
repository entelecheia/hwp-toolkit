#!/usr/bin/env python3
"""
Create HWPX files from text/Markdown content using python-hwpx.

Usage:
    python hwp_create.py <output_file.hwpx> --title "Title" --body "Body text"
    python hwp_create.py <output_file.hwpx> --markdown <input.md>
    python hwp_create.py <output_file.hwpx> --json <structured_input.json>

Dependencies:
    pip install python-hwpx
"""

import sys
import os
import argparse
import json
import re
from io import BytesIO


def create_hwpx_from_paragraphs(output_path: str, title: str = "", author: str = "",
                                 paragraphs: list = None, tables: list = None):
    """
    Create an HWPX file with paragraphs and optional tables.

    Args:
        output_path: Output .hwpx file path
        title: Document title (added as first paragraph if provided)
        author: Document author
        paragraphs: List of paragraph strings
        tables: List of dicts with 'headers' and 'rows' keys
    """
    from hwpx.document import HwpxDocument
    from hwpx.templates import blank_document_bytes

    source = BytesIO(blank_document_bytes())
    doc = HwpxDocument.open(source)
    section = doc.sections[0]

    if title:
        doc.add_paragraph(title, section=section)

    if paragraphs:
        for p in paragraphs:
            if p.strip():
                doc.add_paragraph(p.strip(), section=section)

    if tables:
        for tbl in tables:
            headers = tbl.get("headers", [])
            rows = tbl.get("rows", [])
            if not headers and rows:
                headers = [f"Col{i+1}" for i in range(len(rows[0]))]
            ncols = len(headers)
            nrows = len(rows) + 1  # +1 for header row

            table = doc.add_table(rows=nrows, cols=ncols, section=section)
            for ci, h in enumerate(headers):
                table.set_cell_text(0, ci, str(h))
            for ri, row in enumerate(rows):
                for ci, cell in enumerate(row):
                    if ci < ncols:
                        table.set_cell_text(ri + 1, ci, str(cell))

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    doc.save(output_path)
    return output_path


def create_hwpx_from_markdown_via_node(output_path: str, markdown_text: str,
                                        title: str = "Document", author: str = ""):
    """
    Create HWPX from Markdown using md2hwp (Node.js).
    Supports headings, bold, italic, tables, and lists.

    Args:
        output_path: Output .hwpx file path
        markdown_text: Markdown content string
        title: Document title metadata
        author: Document author metadata
    """
    import subprocess
    import tempfile

    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    node_modules = os.path.join(skill_dir, "node_modules")

    if not os.path.exists(os.path.join(node_modules, "md2hwp")):
        raise RuntimeError(
            "md2hwp not installed. Run: cd {} && npm install md2hwp".format(skill_dir)
        )

    # Write markdown to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(markdown_text)
        md_path = f.name

    # Write temp JS script
    # Note: process.argv[2] = md_path, process.argv[3] = output_path
    # because process.argv[0]=node, process.argv[1]=script.js
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(f"""
const {{ convertMarkdownToHwp }} = require('{node_modules}/md2hwp');
const fs = require('fs');
const mdPath = process.argv[2];
const outPath = process.argv[3];
const md = fs.readFileSync(mdPath, 'utf-8');
(async () => {{
    const buf = await convertMarkdownToHwp(md, {{
        title: {json.dumps(title)},
        author: {json.dumps(author or 'hwp-toolkit')}
    }});
    fs.writeFileSync(outPath, buf);
}})().catch(e => {{ console.error(e); process.exit(1); }});
""")
        js_path = f.name

    try:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        result = subprocess.run(
            ["node", js_path, md_path, output_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            raise RuntimeError(f"md2hwp failed: {result.stderr}")
        if not os.path.exists(output_path):
            raise RuntimeError("md2hwp did not produce output file")
        return output_path
    finally:
        os.unlink(js_path)
        os.unlink(md_path)


def parse_markdown_to_structure(md_text: str) -> dict:
    """Parse simple Markdown into paragraphs and tables for python-hwpx."""
    paragraphs = []
    tables = []
    current_table_lines = []

    for line in md_text.split('\n'):
        stripped = line.strip()

        # Table line
        if '|' in stripped and stripped.startswith('|'):
            current_table_lines.append(stripped)
            continue

        # End of table
        if current_table_lines:
            tbl = _parse_md_table(current_table_lines)
            if tbl:
                tables.append(tbl)
            current_table_lines = []

        # Heading → plain text (python-hwpx doesn't support heading styles easily)
        if stripped.startswith('#'):
            text = re.sub(r'^#+\s*', '', stripped)
            paragraphs.append(text)
        elif stripped:
            # Remove basic markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            text = re.sub(r'^[-*+]\s+', '', text)
            paragraphs.append(text)

    if current_table_lines:
        tbl = _parse_md_table(current_table_lines)
        if tbl:
            tables.append(tbl)

    return {"paragraphs": paragraphs, "tables": tables}


def _parse_md_table(lines: list) -> dict:
    """Parse Markdown table lines into headers and rows."""
    if len(lines) < 2:
        return None
    cells = []
    for line in lines:
        row = [c.strip() for c in line.strip('|').split('|')]
        cells.append(row)

    # Skip separator line (---|----|---)
    headers = cells[0]
    rows = []
    for row in cells[1:]:
        if all(set(c.strip()) <= {'-', ':', ' '} for c in row):
            continue
        rows.append(row)

    return {"headers": headers, "rows": rows}


def main():
    parser = argparse.ArgumentParser(description="Create HWPX files")
    parser.add_argument("output", help="Output HWPX file path")
    parser.add_argument("--title", default="", help="Document title")
    parser.add_argument("--author", default="", help="Document author")
    parser.add_argument("--body", help="Plain text body (paragraphs separated by newlines)")
    parser.add_argument("--markdown", help="Path to Markdown file to convert")
    parser.add_argument("--markdown-text", help="Markdown text string to convert")
    parser.add_argument("--json", help="Path to JSON file with structured content")
    parser.add_argument("--method", choices=["python-hwpx", "md2hwp"], default="python-hwpx",
                        help="Creation method (default: python-hwpx)")
    args = parser.parse_args()

    if not args.output.endswith('.hwpx'):
        args.output += '.hwpx'

    # Determine content source
    if args.markdown:
        with open(args.markdown, 'r', encoding='utf-8') as f:
            md_text = f.read()
        if args.method == "md2hwp":
            create_hwpx_from_markdown_via_node(args.output, md_text, args.title, args.author)
        else:
            struct = parse_markdown_to_structure(md_text)
            create_hwpx_from_paragraphs(
                args.output, args.title, args.author,
                struct["paragraphs"], struct["tables"]
            )
    elif args.markdown_text:
        if args.method == "md2hwp":
            create_hwpx_from_markdown_via_node(args.output, args.markdown_text, args.title, args.author)
        else:
            struct = parse_markdown_to_structure(args.markdown_text)
            create_hwpx_from_paragraphs(
                args.output, args.title, args.author,
                struct["paragraphs"], struct["tables"]
            )
    elif args.json:
        with open(args.json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        create_hwpx_from_paragraphs(
            args.output,
            data.get("title", args.title),
            data.get("author", args.author),
            data.get("paragraphs", []),
            data.get("tables", [])
        )
    elif args.body:
        paragraphs = [p for p in args.body.split('\n') if p.strip()]
        create_hwpx_from_paragraphs(args.output, args.title, args.author, paragraphs)
    else:
        print("Error: Provide --body, --markdown, --markdown-text, or --json", file=sys.stderr)
        sys.exit(1)

    print(f"Created: {args.output}")


if __name__ == "__main__":
    main()

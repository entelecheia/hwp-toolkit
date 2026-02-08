#!/usr/bin/env python3
"""
Edit HWPX files: text replacement, add paragraphs, add tables, add memos.

Usage:
    python hwp_edit.py <input.hwpx> <output.hwpx> --replace "old" "new"
    python hwp_edit.py <input.hwpx> <output.hwpx> --add-paragraph "New paragraph text"
    python hwp_edit.py <input.hwpx> <output.hwpx> --add-table '{"headers":["A","B"],"rows":[["1","2"]]}'

Dependencies:
    pip install python-hwpx gethwp
"""

import sys
import os
import argparse
import json


def replace_text(input_path: str, output_path: str, find: str, replace: str) -> str:
    """Replace text in HWPX file using gethwp."""
    import gethwp
    gethwp.change_word(input_path, output_path, find, replace)
    return output_path


def add_paragraph(input_path: str, output_path: str, text: str) -> str:
    """Add a paragraph to an existing HWPX file."""
    from hwpx.document import HwpxDocument

    doc = HwpxDocument.open(input_path)
    section = doc.sections[0]
    doc.add_paragraph(text, section=section)
    doc.save(output_path)
    return output_path


def add_table(input_path: str, output_path: str, headers: list, rows: list) -> str:
    """Add a table to an existing HWPX file."""
    from hwpx.document import HwpxDocument

    doc = HwpxDocument.open(input_path)
    section = doc.sections[0]

    ncols = len(headers)
    nrows = len(rows) + 1

    table = doc.add_table(rows=nrows, cols=ncols, section=section)
    for ci, h in enumerate(headers):
        table.set_cell_text(0, ci, str(h))
    for ri, row in enumerate(rows):
        for ci, cell in enumerate(row):
            if ci < ncols:
                table.set_cell_text(ri + 1, ci, str(cell))

    doc.save(output_path)
    return output_path


def add_memo(input_path: str, output_path: str, memo_text: str, para_index: int = 0) -> str:
    """Add a memo (comment) to a paragraph in an HWPX file."""
    from hwpx.document import HwpxDocument

    doc = HwpxDocument.open(input_path)
    paragraphs = list(doc.paragraphs)
    if para_index < len(paragraphs):
        doc.add_memo_with_anchor(memo_text, paragraph=paragraphs[para_index], memo_shape_id_ref="0")
    doc.save(output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Edit HWPX files")
    parser.add_argument("input", help="Input HWPX file")
    parser.add_argument("output", help="Output HWPX file")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--replace", nargs=2, metavar=("FIND", "REPLACE"),
                       help="Replace text: --replace 'old text' 'new text'")
    group.add_argument("--add-paragraph", metavar="TEXT",
                       help="Add a paragraph at the end")
    group.add_argument("--add-table", metavar="JSON",
                       help='Add a table: --add-table \'{"headers":["A","B"],"rows":[["1","2"]]}\'')
    group.add_argument("--add-memo", nargs='+', metavar=("TEXT", "PARA_INDEX"),
                       help="Add a memo: --add-memo 'comment text' [paragraph_index]")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.replace:
            replace_text(args.input, args.output, args.replace[0], args.replace[1])
            print(f"Replaced '{args.replace[0]}' → '{args.replace[1]}' in {args.output}")
        elif args.add_paragraph:
            add_paragraph(args.input, args.output, args.add_paragraph)
            print(f"Added paragraph to {args.output}")
        elif args.add_table:
            tbl = json.loads(args.add_table)
            add_table(args.input, args.output, tbl["headers"], tbl["rows"])
            print(f"Added table to {args.output}")
        elif args.add_memo:
            memo_text = args.add_memo[0]
            para_idx = int(args.add_memo[1]) if len(args.add_memo) > 1 else 0
            add_memo(args.input, args.output, memo_text, para_idx)
            print(f"Added memo to paragraph {para_idx} in {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

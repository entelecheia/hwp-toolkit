#!/usr/bin/env python3
"""
Convert HWP/HWPX files to PDF, HTML, Markdown, ODT, or plain text.

Usage:
    python hwp_convert.py <input_file> --to pdf [-o output_file]
    python hwp_convert.py <input_file> --to md
    python hwp_convert.py <input_file> --to html
    python hwp_convert.py <input_file> --to txt
    python hwp_convert.py <input_file> --to odt

Dependencies:
    pip install pyhwp2md python-hwpx weasyprint markdown olefile
"""

import sys
import os
import argparse
import subprocess


def convert_to_markdown(input_path: str) -> str:
    """Convert HWP/HWPX to Markdown using pyhwp2md."""
    from pyhwp2md import convert
    return convert(input_path)


def convert_to_text(input_path: str) -> str:
    """Convert HWP/HWPX to plain text."""
    ext = os.path.splitext(input_path)[1].lower()

    # Try pyhwp2md first
    try:
        from pyhwp2md import convert
        return convert(input_path)
    except Exception:
        pass

    # Fallback: hwp5txt for HWP files
    if ext == ".hwp":
        try:
            result = subprocess.run(["hwp5txt", input_path], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass

    # Fallback: olefile parser
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from hwp_read import read_file
        return read_file(input_path, "txt")
    except Exception as e:
        raise RuntimeError(f"Failed to convert to text: {e}")


def convert_to_html(input_path: str, standalone: bool = True) -> str:
    """Convert HWP/HWPX to HTML."""
    import markdown as md_lib

    md_text = convert_to_markdown(input_path)
    html_body = md_lib.markdown(md_text, extensions=['tables', 'fenced_code'])

    if standalone:
        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{os.path.basename(input_path)}</title>
<style>
body {{ font-family: 'Malgun Gothic', 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif;
       max-width: 800px; margin: 0 auto; padding: 2em; font-size: 11pt; line-height: 1.8; color: #333; }}
h1 {{ font-size: 18pt; border-bottom: 2px solid #333; padding-bottom: 0.3em; }}
h2 {{ font-size: 15pt; border-bottom: 1px solid #ccc; padding-bottom: 0.2em; }}
h3 {{ font-size: 13pt; }}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
th, td {{ border: 1px solid #666; padding: 8px 12px; text-align: left; }}
th {{ background-color: #f5f5f5; font-weight: bold; }}
tr:nth-child(even) {{ background-color: #fafafa; }}
code {{ background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
pre {{ background-color: #f4f4f4; padding: 1em; border-radius: 5px; overflow-x: auto; }}
blockquote {{ border-left: 4px solid #ddd; margin: 1em 0; padding: 0.5em 1em; color: #666; }}
ul, ol {{ padding-left: 2em; }}
li {{ margin-bottom: 0.3em; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""
    return html_body


def convert_to_pdf(input_path: str, output_path: str) -> str:
    """Convert HWP/HWPX to PDF via Markdown → HTML → WeasyPrint."""
    from weasyprint import HTML

    html_content = convert_to_html(input_path, standalone=True)
    HTML(string=html_content).write_pdf(output_path)
    return output_path


def convert_to_odt(input_path: str, output_path: str) -> str:
    """Convert HWP to ODT using pyhwp's hwp5odt (HWP only)."""
    ext = os.path.splitext(input_path)[1].lower()
    if ext != ".hwp":
        raise ValueError("ODT conversion via hwp5odt is only supported for .hwp files")

    result = subprocess.run(
        ["hwp5odt", input_path, "--output", output_path],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"hwp5odt failed: {result.stderr}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Convert HWP/HWPX to other formats")
    parser.add_argument("input", help="Input HWP or HWPX file")
    parser.add_argument("--to", required=True, choices=["pdf", "md", "html", "txt", "odt"],
                        help="Target format")
    parser.add_argument("-o", "--output", help="Output file path (auto-generated if omitted)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    base = os.path.splitext(args.input)[0]
    ext_map = {"pdf": ".pdf", "md": ".md", "html": ".html", "txt": ".txt", "odt": ".odt"}
    output_path = args.output or (base + ext_map[args.to])

    try:
        if args.to == "pdf":
            convert_to_pdf(args.input, output_path)
            print(f"PDF created: {output_path}")
        elif args.to == "md":
            content = convert_to_markdown(args.input)
            if args.output:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Markdown saved: {output_path}")
            else:
                print(content)
        elif args.to == "html":
            content = convert_to_html(args.input)
            if args.output:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"HTML saved: {output_path}")
            else:
                print(content)
        elif args.to == "txt":
            content = convert_to_text(args.input)
            if args.output:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Text saved: {output_path}")
            else:
                print(content)
        elif args.to == "odt":
            convert_to_odt(args.input, output_path)
            print(f"ODT created: {output_path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

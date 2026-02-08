#!/usr/bin/env python3
"""
Read HWP/HWPX files and extract text content as Markdown.

Usage:
    python hwp_read.py <input_file> [-o output_file] [--format md|txt|json]

Dependencies:
    pip install pyhwp2md olefile python-hwpx
"""

import sys
import os
import argparse
import json


def read_hwpx_with_pyhwp2md(filepath: str) -> str:
    """Read HWP or HWPX file using pyhwp2md (primary method)."""
    from pyhwp2md import convert
    return convert(filepath)


def read_hwp_with_olefile(filepath: str) -> str:
    """Read HWP (binary OLE2) file using olefile-based parser (fallback)."""
    import struct
    import zlib
    import olefile

    if not olefile.isOleFile(filepath):
        raise ValueError(f"Not a valid HWP file: {filepath}")

    ole = olefile.OleFileIO(filepath)
    try:
        header = ole.openstream("FileHeader").read()
        is_compressed = header[36] & 1

        all_text = []
        section_idx = 0
        while True:
            stream_name = f"BodyText/Section{section_idx}"
            if not ole.exists(stream_name):
                break
            body = ole.openstream(stream_name).read()
            if is_compressed:
                body = zlib.decompress(body, -15)

            offset = 0
            while offset < len(body) - 4:
                hdr = struct.unpack('<I', body[offset:offset + 4])[0]
                tag = hdr & 0x3FF
                size = (hdr >> 20) & 0xFFF
                if size == 0xFFF:
                    if offset + 8 > len(body):
                        break
                    size = struct.unpack('<I', body[offset + 4:offset + 8])[0]
                    data_off = offset + 8
                else:
                    data_off = offset + 4
                if data_off + size > len(body):
                    break

                if tag == 67:  # PARA_TEXT
                    data = body[data_off:data_off + size]
                    text = _decode_hwp_text(data)
                    if text.strip():
                        all_text.append(text)

                offset = data_off + size
                if offset <= data_off:
                    break
            section_idx += 1

        return "\n".join(all_text)
    finally:
        ole.close()


def _decode_hwp_text(data: bytes) -> str:
    """Decode HWP UTF-16LE text data with control code handling."""
    import struct
    decoded = ""
    i = 0
    while i < len(data) - 1:
        cc = struct.unpack('<H', data[i:i + 2])[0]
        if cc == 0:
            break
        elif cc < 32:
            if cc in [1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18, 21, 22, 23]:
                i += 16
                continue
            elif cc == 10:
                decoded += "\n"
            elif cc == 9:
                decoded += "\t"
            i += 2
            continue
        elif 0x20 <= cc <= 0xFFFF and not (0xD800 <= cc <= 0xDFFF):
            decoded += chr(cc)
        i += 2
    return decoded.strip()


def read_hwpx_with_python_hwpx(filepath: str) -> str:
    """Read HWPX file using python-hwpx (structured access)."""
    from hwpx.document import HwpxDocument
    doc = HwpxDocument.open(filepath)
    texts = []
    for para in doc.paragraphs:
        t = para.text if hasattr(para, 'text') else str(para)
        if t and t.strip():
            texts.append(t.strip())
    return "\n".join(texts)


def read_file(filepath: str, output_format: str = "md") -> str:
    """Read HWP or HWPX file and return content in specified format."""
    ext = os.path.splitext(filepath)[1].lower()

    # Try pyhwp2md first (handles both HWP and HWPX)
    try:
        content = read_hwpx_with_pyhwp2md(filepath)
        if content and content.strip():
            if output_format == "txt":
                return content
            return content
    except Exception as e:
        print(f"[INFO] pyhwp2md failed ({e}), trying fallback...", file=sys.stderr)

    # Fallback methods
    if ext == ".hwpx":
        try:
            return read_hwpx_with_python_hwpx(filepath)
        except Exception as e:
            print(f"[WARN] python-hwpx failed: {e}", file=sys.stderr)
    elif ext == ".hwp":
        try:
            return read_hwp_with_olefile(filepath)
        except Exception as e:
            print(f"[WARN] olefile parser failed: {e}", file=sys.stderr)

    raise RuntimeError(f"Failed to read file: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Read HWP/HWPX files and extract text")
    parser.add_argument("input", help="Input HWP or HWPX file path")
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    parser.add_argument("--format", choices=["md", "txt", "json"], default="md",
                        help="Output format (default: md)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    content = read_file(args.input, args.format)

    if args.format == "json":
        output = json.dumps({"source": args.input, "content": content}, ensure_ascii=False, indent=2)
    else:
        output = content

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()

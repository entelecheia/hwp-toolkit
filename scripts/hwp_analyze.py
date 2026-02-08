#!/usr/bin/env python3
"""
Analyze HWP/HWPX file structure and extract metadata.

Usage:
    python hwp_analyze.py <input_file>

Dependencies:
    pip install olefile python-hwpx
"""

import sys
import os
import json
import struct
import zlib
from collections import Counter


def analyze_hwp(filepath: str) -> dict:
    """Analyze HWP (OLE2 binary) file structure."""
    import olefile

    if not olefile.isOleFile(filepath):
        raise ValueError(f"Not a valid HWP file: {filepath}")

    ole = olefile.OleFileIO(filepath)
    info = {"format": "HWP", "path": filepath, "streams": [], "metadata": {}, "stats": {}}

    try:
        # Streams
        for entry in ole.listdir():
            stream_path = "/".join(entry)
            try:
                size = ole.get_size(stream_path)
                info["streams"].append({"name": stream_path, "size": size})
            except Exception:
                info["streams"].append({"name": stream_path, "size": 0})

        # FileHeader
        header = ole.openstream("FileHeader").read()
        sig = header[:32].decode('utf-8', errors='ignore').rstrip('\x00')
        version = f"{header[32]}.{header[33]}.{header[34]}.{header[35]}"
        flags = header[36]

        info["metadata"] = {
            "signature": sig,
            "version": version,
            "compressed": bool(flags & 1),
            "encrypted": bool(flags & 2),
            "distributed": bool(flags & 4),
            "has_script": bool(flags & 8),
        }

        # Preview text
        if ole.exists("PrvText"):
            prv = ole.openstream("PrvText").read()
            try:
                info["metadata"]["preview"] = prv.decode('utf-16-le', errors='ignore')[:500]
            except Exception:
                pass

        # Images
        images = [s for s in info["streams"] if s["name"].startswith("BinData/")]
        info["stats"]["image_count"] = len(images)
        info["stats"]["images"] = [s["name"] for s in images]

        # Section count
        section_count = 0
        while ole.exists(f"BodyText/Section{section_count}"):
            section_count += 1
        info["stats"]["section_count"] = section_count

        # Record tag statistics (from Section0)
        if info["metadata"]["compressed"] is not None and ole.exists("BodyText/Section0"):
            body = ole.openstream("BodyText/Section0").read()
            if info["metadata"]["compressed"]:
                try:
                    body = zlib.decompress(body, -15)
                except Exception:
                    body = None

            if body:
                tag_counter = Counter()
                offset = 0
                while offset < len(body) - 4:
                    hdr = struct.unpack('<I', body[offset:offset + 4])[0]
                    tag = hdr & 0x3FF
                    size = (hdr >> 20) & 0xFFF
                    if size == 0xFFF:
                        if offset + 8 > len(body):
                            break
                        size = struct.unpack('<I', body[offset + 4:offset + 8])[0]
                        offset += 8
                    else:
                        offset += 4
                    tag_counter[tag] += 1
                    offset += size
                    if offset <= 0 or size < 0:
                        break

                info["stats"]["total_records"] = sum(tag_counter.values())
                info["stats"]["has_tables"] = 80 in tag_counter
                info["stats"]["table_count"] = tag_counter.get(80, 0)
                info["stats"]["paragraph_count"] = tag_counter.get(67, 0)

    finally:
        ole.close()

    return info


def analyze_hwpx(filepath: str) -> dict:
    """Analyze HWPX (XML/ZIP) file structure."""
    import zipfile

    info = {"format": "HWPX", "path": filepath, "entries": [], "metadata": {}, "stats": {}}

    with zipfile.ZipFile(filepath, 'r') as zf:
        for zi in zf.infolist():
            info["entries"].append({
                "name": zi.filename,
                "size": zi.file_size,
                "compressed_size": zi.compress_size
            })

        # Read mimetype
        if "mimetype" in zf.namelist():
            info["metadata"]["mimetype"] = zf.read("mimetype").decode('utf-8', errors='ignore').strip()

        # Read version.xml
        if "version.xml" in zf.namelist():
            info["metadata"]["version_xml"] = zf.read("version.xml").decode('utf-8', errors='ignore')

        # Count sections
        sections = [e for e in zf.namelist() if e.startswith("Contents/section") and e.endswith(".xml")]
        info["stats"]["section_count"] = len(sections)

        # Count images
        images = [e for e in zf.namelist() if e.startswith("BinData/") or e.startswith("Contents/BinData/")]
        info["stats"]["image_count"] = len(images)
        info["stats"]["images"] = images

    # Use python-hwpx for deeper analysis
    try:
        from hwpx.document import HwpxDocument
        doc = HwpxDocument.open(filepath)
        info["stats"]["paragraph_count"] = len(list(doc.paragraphs))
        # Check for tables
        table_count = 0
        for para in doc.paragraphs:
            text = para.text if hasattr(para, 'text') else ''
        info["stats"]["section_count"] = len(doc.sections)
    except Exception:
        pass

    return info


def analyze(filepath: str) -> dict:
    """Analyze HWP or HWPX file."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".hwp":
        return analyze_hwp(filepath)
    elif ext == ".hwpx":
        return analyze_hwpx(filepath)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python hwp_analyze.py <input_file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    info = analyze(filepath)
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

# HWP/HWPX Format Reference

## HWP 5.0 (Binary OLE2 Format)

HWP files use the OLE2 compound file format. Internal structure:

```
HWP File (OLE2)
├── FileHeader (256 bytes) — signature, version, flags (compressed/encrypted)
├── DocInfo — document properties, fonts, styles
├── BodyText/
│   ├── Section0 — body content (zlib compressed)
│   ├── Section1 ...
├── BinData/ — embedded images (BIN0001.BMP, etc.)
├── PrvText — preview text (UTF-16LE)
└── PrvImage — preview image (PNG)
```

### Key Record Tags (BodyText sections)

| TagID | Name | Purpose |
|-------|------|---------|
| 64 | PARA_HEADER | Paragraph header |
| 66 | LIST_HEADER | List/table cell header |
| 67 | PARA_TEXT | Paragraph text (UTF-16LE) |
| 71 | CTRL_HEADER | Control (table, image, etc.) |
| 80 | TABLE | Table definition (rows, cols) |
| 81 | CELL | Cell definition |

### Text Extraction

Records are parsed from 4-byte headers: TagID (10bit), Level (10bit), Size (12bit).
Text is in PARA_TEXT (tag 67) records, encoded as UTF-16LE with control codes (chars < 32).
Extended controls (chars 1-8, 11-18, 21-23) consume 16 extra bytes.

## HWPX (XML/ZIP Format)

HWPX is the open XML-based format (since 2021), based on OWPML specification.

```
HWPX File (ZIP)
├── mimetype — "application/hwp+zip"
├── version.xml
├── settings.xml
├── META-INF/
│   ├── container.xml
│   ├── container.rdf
│   └── manifest.xml
├── Contents/
│   ├── content.hpf — content manifest
│   ├── header.xml — document header (fonts, styles, charShapes)
│   ├── section0.xml — body content
│   └── BinData/ — embedded images
└── Preview/
    ├── PrvText.txt
    └── PrvImage.png
```

### Key XML Namespaces

- `hp:` — body content (paragraphs, runs, tables)
- `hh:` — header (charShape, paraShape, fonts, styles)
- `hc:` — content manifest

### HWPUNIT

1 HWPUNIT ≈ 1/7200 inch. Default A4 page: 59528 × 84188 HWPUNIT.

## Tool Compatibility

| Tool | HWP Read | HWPX Read | HWPX Write | PDF Convert |
|------|----------|-----------|------------|-------------|
| pyhwp2md | Yes | Yes | No | No |
| python-hwpx | No | Yes | Yes | No |
| md2hwp | No | No | Yes | No |
| olefile parser | Yes | No | No | No |
| unhwp CLI | Yes | Yes | No | No |
| gethwp | Yes | Yes | No | No |
| WeasyPrint | — | — | — | Via HTML |

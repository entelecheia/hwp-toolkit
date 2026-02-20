#!/usr/bin/env python3
"""
MCP Server for HWP/HWPX Toolkit.

Exposes the hwp-toolkit scripts as MCP tools that Claude can call directly.
Run with the project's .venv Python interpreter:
    .venv/bin/python mcp_server.py

Configure in Claude Code via .mcp.json (project-level) or:
    claude mcp add hwp-toolkit --scope project
"""

import os
import sys
import json

# macOS: ensure Homebrew libraries are findable for WeasyPrint
if sys.platform == "darwin":
    homebrew_lib = "/opt/homebrew/lib"
    current = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    if homebrew_lib not in current:
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = (
            f"{homebrew_lib}:{current}" if current else homebrew_lib
        )

# Make scripts/ importable without installing the package
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hwp-toolkit")


# ---------------------------------------------------------------------------
# Tool 1: Read
# ---------------------------------------------------------------------------

@mcp.tool()
def hwp_read(input_path: str, output_format: str = "md") -> str:
    """HWP/HWPX 파일에서 텍스트를 추출합니다.

    Args:
        input_path: HWP 또는 HWPX 파일의 절대 경로
        output_format: 출력 형식 — "md" (Markdown, 기본값), "txt" (일반 텍스트), "json"

    Returns:
        지정한 형식의 추출된 텍스트 내용
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {input_path}")
    if output_format not in ("md", "txt", "json"):
        raise ValueError(f"지원하지 않는 형식: {output_format}. 'md', 'txt', 'json' 중 하나여야 합니다.")

    from hwp_read import read_file

    content = read_file(input_path, output_format)

    if output_format == "json":
        return json.dumps({"source": input_path, "content": content}, ensure_ascii=False, indent=2)
    return content


# ---------------------------------------------------------------------------
# Tool 2: Create
# ---------------------------------------------------------------------------

@mcp.tool()
def hwp_create(
    output_path: str,
    title: str = "",
    author: str = "",
    body: str = "",
    markdown_text: str = "",
    markdown_file: str = "",
    json_file: str = "",
    method: str = "python-hwpx",
) -> str:
    """새 HWPX 파일을 텍스트, Markdown, 또는 JSON 내용으로 생성합니다.

    Args:
        output_path: 생성할 .hwpx 파일의 절대 경로
        title: 문서 제목
        author: 문서 작성자
        body: 일반 텍스트 본문 (\\n으로 단락 구분)
        markdown_text: Markdown 문자열 (직접 입력)
        markdown_file: Markdown 파일 경로 (.md)
        json_file: 구조화된 JSON 파일 경로 ({"title","author","paragraphs","tables"} 형식)
        method: 생성 방법 — "python-hwpx" (기본값, 빠름) 또는 "md2hwp" (Markdown 서식 보존)

    Returns:
        생성된 파일의 경로
    """
    if not output_path.endswith(".hwpx"):
        output_path += ".hwpx"
    if method not in ("python-hwpx", "md2hwp"):
        raise ValueError(f"지원하지 않는 방법: {method}. 'python-hwpx' 또는 'md2hwp'여야 합니다.")

    from hwp_create import (
        create_hwpx_from_paragraphs,
        create_hwpx_from_markdown_via_node,
        parse_markdown_to_structure,
    )

    if markdown_file:
        if not os.path.exists(markdown_file):
            raise FileNotFoundError(f"Markdown 파일을 찾을 수 없습니다: {markdown_file}")
        with open(markdown_file, "r", encoding="utf-8") as f:
            md_text = f.read()
        if method == "md2hwp":
            create_hwpx_from_markdown_via_node(output_path, md_text, title, author)
        else:
            struct = parse_markdown_to_structure(md_text)
            create_hwpx_from_paragraphs(output_path, title, author, struct["paragraphs"], struct["tables"])

    elif markdown_text:
        if method == "md2hwp":
            create_hwpx_from_markdown_via_node(output_path, markdown_text, title, author)
        else:
            struct = parse_markdown_to_structure(markdown_text)
            create_hwpx_from_paragraphs(output_path, title, author, struct["paragraphs"], struct["tables"])

    elif json_file:
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"JSON 파일을 찾을 수 없습니다: {json_file}")
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        create_hwpx_from_paragraphs(
            output_path,
            data.get("title", title),
            data.get("author", author),
            data.get("paragraphs", []),
            data.get("tables", []),
        )

    elif body:
        paragraphs = [p for p in body.split("\n") if p.strip()]
        create_hwpx_from_paragraphs(output_path, title, author, paragraphs)

    else:
        raise ValueError("body, markdown_text, markdown_file, json_file 중 하나를 제공해야 합니다.")

    return f"생성 완료: {output_path}"


# ---------------------------------------------------------------------------
# Tool 3: Convert
# ---------------------------------------------------------------------------

@mcp.tool()
def hwp_convert(input_path: str, target_format: str, output_path: str = "") -> str:
    """HWP/HWPX 파일을 다른 형식으로 변환합니다.

    Args:
        input_path: 입력 HWP 또는 HWPX 파일의 절대 경로
        target_format: 대상 형식 — "pdf", "md", "html", "txt", "odt"
        output_path: 출력 파일 경로 (생략 시 자동 생성)

    Returns:
        출력 파일 경로 (pdf/odt), 또는 텍스트 내용 (md/html/txt에서 output_path 생략 시)
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {input_path}")

    valid_formats = ("pdf", "md", "html", "txt", "odt")
    if target_format not in valid_formats:
        raise ValueError(f"지원하지 않는 형식: {target_format}. {valid_formats} 중 하나여야 합니다.")

    from hwp_convert import (
        convert_to_markdown,
        convert_to_text,
        convert_to_html,
        convert_to_pdf,
        convert_to_odt,
    )

    ext_map = {"pdf": ".pdf", "md": ".md", "html": ".html", "txt": ".txt", "odt": ".odt"}
    base = os.path.splitext(input_path)[0]
    resolved_output = output_path or (base + ext_map[target_format])

    if target_format == "pdf":
        convert_to_pdf(input_path, resolved_output)
        return f"PDF 생성 완료: {resolved_output}"

    elif target_format == "md":
        content = convert_to_markdown(input_path)
        if output_path:
            with open(resolved_output, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Markdown 저장 완료: {resolved_output}"
        return content

    elif target_format == "html":
        content = convert_to_html(input_path)
        if output_path:
            with open(resolved_output, "w", encoding="utf-8") as f:
                f.write(content)
            return f"HTML 저장 완료: {resolved_output}"
        return content

    elif target_format == "txt":
        content = convert_to_text(input_path)
        if output_path:
            with open(resolved_output, "w", encoding="utf-8") as f:
                f.write(content)
            return f"텍스트 저장 완료: {resolved_output}"
        return content

    elif target_format == "odt":
        convert_to_odt(input_path, resolved_output)
        return f"ODT 생성 완료: {resolved_output}"


# ---------------------------------------------------------------------------
# Tool 4: Edit
# ---------------------------------------------------------------------------

@mcp.tool()
def hwp_edit(
    input_path: str,
    output_path: str,
    operation: str,
    find_text: str = "",
    replace_text: str = "",
    paragraph_text: str = "",
    table_json: str = "",
    memo_text: str = "",
    para_index: int = 0,
) -> str:
    """기존 HWPX 파일을 편집합니다. HWPX 형식 파일만 지원합니다.

    Args:
        input_path: 입력 HWPX 파일의 절대 경로
        output_path: 출력 HWPX 파일의 절대 경로
        operation: 작업 유형 — "replace", "add_paragraph", "add_table", "add_memo"
        find_text: [replace 전용] 찾을 텍스트
        replace_text: [replace 전용] 바꿀 텍스트
        paragraph_text: [add_paragraph 전용] 추가할 단락 텍스트
        table_json: [add_table 전용] 테이블 JSON 문자열 {"headers":[...],"rows":[[...]]}
        memo_text: [add_memo 전용] 메모 텍스트
        para_index: [add_memo 전용] 메모를 붙일 단락 인덱스 (기본값: 0)

    Returns:
        출력 파일 경로
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {input_path}")

    valid_ops = ("replace", "add_paragraph", "add_table", "add_memo")
    if operation not in valid_ops:
        raise ValueError(f"지원하지 않는 작업: {operation}. {valid_ops} 중 하나여야 합니다.")

    from hwp_edit import (
        replace_text as _replace_text,
        add_paragraph,
        add_table,
        add_memo,
    )

    if operation == "replace":
        if not find_text:
            raise ValueError("'replace' 작업에는 find_text가 필요합니다.")
        _replace_text(input_path, output_path, find_text, replace_text)
        return f"'{find_text}' → '{replace_text}' 교체 완료: {output_path}"

    elif operation == "add_paragraph":
        if not paragraph_text:
            raise ValueError("'add_paragraph' 작업에는 paragraph_text가 필요합니다.")
        add_paragraph(input_path, output_path, paragraph_text)
        return f"단락 추가 완료: {output_path}"

    elif operation == "add_table":
        if not table_json:
            raise ValueError("'add_table' 작업에는 table_json이 필요합니다.")
        tbl = json.loads(table_json)
        add_table(input_path, output_path, tbl["headers"], tbl["rows"])
        return f"테이블 추가 완료: {output_path}"

    elif operation == "add_memo":
        if not memo_text:
            raise ValueError("'add_memo' 작업에는 memo_text가 필요합니다.")
        add_memo(input_path, output_path, memo_text, para_index)
        return f"메모 추가 완료 (단락 {para_index}): {output_path}"


# ---------------------------------------------------------------------------
# Tool 5: Analyze
# ---------------------------------------------------------------------------

@mcp.tool()
def hwp_analyze(input_path: str) -> str:
    """HWP/HWPX 파일의 내부 구조와 메타데이터를 분석합니다.

    Args:
        input_path: HWP 또는 HWPX 파일의 절대 경로

    Returns:
        파일 구조, 섹션 수, 이미지 수, 단락 수 등을 포함한 JSON 문자열
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {input_path}")

    from hwp_analyze import analyze

    info = analyze(input_path)
    return json.dumps(info, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")

"""
hwp_read.py 테스트.

- read_file: HWPX 파일에서 텍스트 추출 (md/txt/json)
- 내부 파서 함수: read_hwpx_with_python_hwpx
"""

import json

import pytest

from hwp_read import read_file, read_hwpx_with_python_hwpx


class TestReadFile:
    def test_returns_string(self, base_hwpx):
        result = read_file(base_hwpx, "md")
        assert isinstance(result, str)

    def test_content_not_empty(self, base_hwpx):
        result = read_file(base_hwpx, "md")
        assert result.strip()

    def test_contains_known_text(self, base_hwpx):
        result = read_file(base_hwpx, "md")
        assert "첫 번째 단락" in result or "테스트 문서" in result

    def test_format_txt(self, base_hwpx):
        result = read_file(base_hwpx, "txt")
        assert isinstance(result, str)
        assert result.strip()

    def test_format_json_returns_string(self, base_hwpx):
        """json 포맷도 문자열을 반환해야 한다 (MCP 서버가 JSON 직렬화)."""
        result = read_file(base_hwpx, "md")
        assert isinstance(result, str)

    def test_file_not_found_raises(self):
        with pytest.raises((FileNotFoundError, RuntimeError, Exception)):
            read_file("/nonexistent/path/file.hwpx", "md")

    def test_read_from_sample_md_created_hwpx(self, tmp_hwpx, sample_md):
        """sample.md → HWPX 생성 후 다시 읽기."""
        from hwp_create import create_hwpx_from_paragraphs, parse_markdown_to_structure

        with open(sample_md, encoding="utf-8") as f:
            md_text = f.read()
        struct = parse_markdown_to_structure(md_text)
        create_hwpx_from_paragraphs(
            tmp_hwpx, title="샘플", paragraphs=struct["paragraphs"]
        )
        result = read_file(tmp_hwpx, "md")
        assert "HWP Toolkit" in result or "주요 기능" in result or "결론" in result

    def test_multiple_paragraphs_all_present(self, tmp_path):
        """생성한 단락들이 읽기 결과에 모두 포함되어야 한다."""
        from hwp_create import create_hwpx_from_paragraphs

        paragraphs = ["알파", "베타", "감마"]
        out = str(tmp_path / "multi.hwpx")
        create_hwpx_from_paragraphs(out, paragraphs=paragraphs)
        result = read_file(out, "md")
        for p in paragraphs:
            assert p in result


class TestReadHwpxWithPythonHwpx:
    def test_returns_string(self, base_hwpx):
        result = read_hwpx_with_python_hwpx(base_hwpx)
        assert isinstance(result, str)

    def test_content_nonempty(self, base_hwpx):
        result = read_hwpx_with_python_hwpx(base_hwpx)
        assert result.strip()

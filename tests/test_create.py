"""
hwp_create.py 테스트.

- create_hwpx_from_paragraphs: 일반 텍스트/단락으로 HWPX 생성
- create_hwpx_from_markdown_via_node: md2hwp Node.js 경유 생성 (Node 필요)
- parse_markdown_to_structure: Markdown 파싱 유틸
"""

import os
import zipfile

import pytest

from hwp_create import (
    create_hwpx_from_paragraphs,
    create_hwpx_from_markdown_via_node,
    parse_markdown_to_structure,
)


# ---------------------------------------------------------------------------
# create_hwpx_from_paragraphs
# ---------------------------------------------------------------------------

class TestCreateFromParagraphs:
    def test_basic_output_exists(self, tmp_hwpx):
        create_hwpx_from_paragraphs(tmp_hwpx, title="제목", paragraphs=["내용"])
        assert os.path.exists(tmp_hwpx)

    def test_output_is_valid_zip(self, tmp_hwpx):
        create_hwpx_from_paragraphs(tmp_hwpx, paragraphs=["테스트"])
        assert zipfile.is_zipfile(tmp_hwpx)

    def test_mimetype_entry(self, tmp_hwpx):
        create_hwpx_from_paragraphs(tmp_hwpx, paragraphs=["테스트"])
        with zipfile.ZipFile(tmp_hwpx) as zf:
            assert "mimetype" in zf.namelist()
            assert zf.read("mimetype").decode() == "application/hwp+zip"

    def test_section_xml_exists(self, tmp_hwpx):
        create_hwpx_from_paragraphs(tmp_hwpx, paragraphs=["단락1"])
        with zipfile.ZipFile(tmp_hwpx) as zf:
            sections = [n for n in zf.namelist() if n.startswith("Contents/section")]
            assert len(sections) >= 1

    def test_multiple_paragraphs(self, tmp_hwpx):
        paragraphs = ["단락 A", "단락 B", "단락 C"]
        create_hwpx_from_paragraphs(tmp_hwpx, paragraphs=paragraphs)
        assert os.path.getsize(tmp_hwpx) > 0

    def test_with_title_and_author(self, tmp_hwpx):
        create_hwpx_from_paragraphs(
            tmp_hwpx, title="테스트 제목", author="이영준", paragraphs=["본문"]
        )
        assert os.path.exists(tmp_hwpx)

    def test_with_table(self, tmp_hwpx):
        tables = [{"headers": ["이름", "나이"], "rows": [["철수", "20"], ["영희", "22"]]}]
        create_hwpx_from_paragraphs(tmp_hwpx, paragraphs=["표 테스트"], tables=tables)
        assert os.path.exists(tmp_hwpx)

    def test_empty_paragraphs_filtered(self, tmp_hwpx):
        """빈 문자열 단락은 무시되어야 한다."""
        create_hwpx_from_paragraphs(tmp_hwpx, paragraphs=["", "  ", "실제 내용"])
        assert os.path.exists(tmp_hwpx)

    def test_auto_add_hwpx_extension(self, tmp_path):
        """출력 경로에 .hwpx가 없어도 저장 가능해야 한다."""
        out = str(tmp_path / "output_no_ext")
        # create_hwpx_from_paragraphs는 확장자를 강제하지 않음 — 경로 그대로 저장
        create_hwpx_from_paragraphs(out + ".hwpx", paragraphs=["내용"])
        assert os.path.exists(out + ".hwpx")

    def test_table_without_headers_auto_generates(self, tmp_hwpx):
        """headers가 없고 rows만 있을 때 Col1, Col2... 자동 생성."""
        tables = [{"headers": [], "rows": [["A", "B"], ["C", "D"]]}]
        create_hwpx_from_paragraphs(tmp_hwpx, paragraphs=["헤더 없는 표"], tables=tables)
        assert os.path.exists(tmp_hwpx)


# ---------------------------------------------------------------------------
# parse_markdown_to_structure
# ---------------------------------------------------------------------------

class TestParseMarkdown:
    def test_heading_becomes_paragraph(self):
        md = "# 제목\n## 소제목\n본문"
        result = parse_markdown_to_structure(md)
        assert "제목" in result["paragraphs"]
        assert "소제목" in result["paragraphs"]

    def test_bold_italic_stripped(self):
        md = "**굵게** *기울임* 일반"
        result = parse_markdown_to_structure(md)
        combined = " ".join(result["paragraphs"])
        assert "굵게" in combined
        assert "기울임" in combined
        assert "**" not in combined
        assert "*" not in combined

    def test_unordered_list_prefix_stripped(self):
        md = "- 항목1\n- 항목2"
        result = parse_markdown_to_structure(md)
        combined = " ".join(result["paragraphs"])
        assert "항목1" in combined
        assert "-" not in combined

    def test_table_parsed(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = parse_markdown_to_structure(md)
        assert len(result["tables"]) == 1
        tbl = result["tables"][0]
        assert tbl["headers"] == ["A", "B"]
        assert tbl["rows"] == [["1", "2"]]

    def test_empty_lines_ignored(self):
        md = "\n\n내용\n\n"
        result = parse_markdown_to_structure(md)
        assert "내용" in result["paragraphs"]

    def test_no_tables_in_plain_text(self):
        md = "단순 텍스트만"
        result = parse_markdown_to_structure(md)
        assert result["tables"] == []


# ---------------------------------------------------------------------------
# create_hwpx_from_paragraphs (Markdown 경유)
# ---------------------------------------------------------------------------

class TestCreateFromMarkdownFile:
    def test_from_sample_md(self, tmp_hwpx, sample_md):
        from hwp_create import parse_markdown_to_structure

        with open(sample_md, encoding="utf-8") as f:
            md_text = f.read()
        struct = parse_markdown_to_structure(md_text)
        create_hwpx_from_paragraphs(
            tmp_hwpx, title="샘플", paragraphs=struct["paragraphs"], tables=struct["tables"]
        )
        assert os.path.exists(tmp_hwpx)
        assert os.path.getsize(tmp_hwpx) > 1000


# ---------------------------------------------------------------------------
# create_hwpx_from_markdown_via_node (Node.js 필요, 선택적 실행)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not os.path.exists(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "node_modules", "md2hwp")
    ),
    reason="md2hwp Node.js 모듈 없음",
)
class TestCreateViaMd2Hwp:
    def test_basic_creation(self, tmp_hwpx):
        create_hwpx_from_markdown_via_node(tmp_hwpx, "# 제목\n본문 내용", title="테스트")
        assert os.path.exists(tmp_hwpx)
        assert zipfile.is_zipfile(tmp_hwpx)

    def test_from_sample_md(self, tmp_hwpx, sample_md):
        with open(sample_md, encoding="utf-8") as f:
            md_text = f.read()
        create_hwpx_from_markdown_via_node(tmp_hwpx, md_text, title="샘플", author="이영준")
        assert os.path.exists(tmp_hwpx)

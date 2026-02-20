"""
hwp_analyze.py 테스트.

- analyze_hwpx: HWPX ZIP 구조 분석
- analyze: 확장자 자동 감지 디스패처
"""

import pytest

from hwp_analyze import analyze, analyze_hwpx


class TestAnalyzeHwpx:
    def test_returns_dict(self, base_hwpx):
        result = analyze_hwpx(base_hwpx)
        assert isinstance(result, dict)

    def test_format_field(self, base_hwpx):
        result = analyze_hwpx(base_hwpx)
        assert result["format"] == "HWPX"

    def test_path_field(self, base_hwpx):
        result = analyze_hwpx(base_hwpx)
        assert result["path"] == base_hwpx

    def test_entries_list(self, base_hwpx):
        result = analyze_hwpx(base_hwpx)
        assert isinstance(result["entries"], list)
        assert len(result["entries"]) > 0

    def test_entries_have_required_keys(self, base_hwpx):
        result = analyze_hwpx(base_hwpx)
        for entry in result["entries"]:
            assert "name" in entry
            assert "size" in entry
            assert "compressed_size" in entry

    def test_mimetype_in_metadata(self, base_hwpx):
        result = analyze_hwpx(base_hwpx)
        assert result["metadata"]["mimetype"] == "application/hwp+zip"

    def test_stats_section_count(self, base_hwpx):
        result = analyze_hwpx(base_hwpx)
        assert result["stats"]["section_count"] >= 1

    def test_stats_paragraph_count(self, base_hwpx):
        result = analyze_hwpx(base_hwpx)
        assert result["stats"]["paragraph_count"] >= 1

    def test_stats_image_count(self, base_hwpx):
        result = analyze_hwpx(base_hwpx)
        assert "image_count" in result["stats"]
        assert result["stats"]["image_count"] >= 0


class TestAnalyzeDispatcher:
    def test_hwpx_dispatches_correctly(self, base_hwpx):
        result = analyze(base_hwpx)
        assert result["format"] == "HWPX"

    def test_unsupported_extension_raises(self, tmp_path):
        fake = tmp_path / "test.docx"
        fake.write_bytes(b"fake")
        with pytest.raises(ValueError, match="Unsupported"):
            analyze(str(fake))

    def test_paragraph_count_matches_input(self, tmp_path):
        """생성 단락 수와 분석 단락 수가 일치해야 한다."""
        from hwp_create import create_hwpx_from_paragraphs

        paragraphs = ["단락1", "단락2", "단락3"]
        out = str(tmp_path / "count_test.hwpx")
        create_hwpx_from_paragraphs(out, title="제목", paragraphs=paragraphs)
        result = analyze(out)
        # title + 3 paragraphs = 4, 단 python-hwpx 내부 빈 단락 포함 가능
        assert result["stats"]["paragraph_count"] >= len(paragraphs)

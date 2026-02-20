"""
hwp_convert.py 테스트.

- convert_to_markdown: HWPX → Markdown  (pyhwp2md 필요)
- convert_to_text: HWPX → 일반 텍스트
- convert_to_html: HWPX → HTML          (pyhwp2md 필요)
- convert_to_pdf: HWPX → PDF            (pyhwp2md + WeasyPrint 필요)
"""

import os

import pytest

from hwp_convert import convert_to_text


def _pyhwp2md_available() -> bool:
    try:
        import pyhwp2md  # noqa: F401
        return True
    except Exception:
        return False


def _weasyprint_available() -> bool:
    try:
        import weasyprint  # noqa: F401
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# convert_to_markdown  (pyhwp2md 필요)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _pyhwp2md_available(), reason="pyhwp2md 미설치")
class TestConvertToMarkdown:
    def test_returns_string(self, base_hwpx):
        from hwp_convert import convert_to_markdown
        result = convert_to_markdown(base_hwpx)
        assert isinstance(result, str)

    def test_content_nonempty(self, base_hwpx):
        from hwp_convert import convert_to_markdown
        result = convert_to_markdown(base_hwpx)
        assert result.strip()

    def test_contains_known_text(self, base_hwpx):
        from hwp_convert import convert_to_markdown
        result = convert_to_markdown(base_hwpx)
        assert "테스트 문서" in result or "단락" in result

    def test_roundtrip_create_and_convert(self, tmp_path):
        """생성 → Markdown 변환 왕복 테스트."""
        from hwp_convert import convert_to_markdown
        from hwp_create import create_hwpx_from_paragraphs

        paragraphs = ["라운드트립 테스트", "두 번째 줄"]
        out = str(tmp_path / "roundtrip.hwpx")
        create_hwpx_from_paragraphs(out, paragraphs=paragraphs)
        md = convert_to_markdown(out)
        assert "라운드트립 테스트" in md


# ---------------------------------------------------------------------------
# convert_to_text
# ---------------------------------------------------------------------------

class TestConvertToText:
    def test_returns_string(self, base_hwpx):
        result = convert_to_text(base_hwpx)
        assert isinstance(result, str)

    def test_content_nonempty(self, base_hwpx):
        result = convert_to_text(base_hwpx)
        assert result.strip()


# ---------------------------------------------------------------------------
# convert_to_html  (pyhwp2md 필요)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _pyhwp2md_available(), reason="pyhwp2md 미설치")
class TestConvertToHtml:
    def test_returns_string(self, base_hwpx):
        from hwp_convert import convert_to_html
        result = convert_to_html(base_hwpx)
        assert isinstance(result, str)

    def test_is_html_document(self, base_hwpx):
        from hwp_convert import convert_to_html
        result = convert_to_html(base_hwpx)
        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "</html>" in result

    def test_has_body_content(self, base_hwpx):
        from hwp_convert import convert_to_html
        result = convert_to_html(base_hwpx)
        assert "<body>" in result
        assert "</body>" in result

    def test_charset_utf8(self, base_hwpx):
        from hwp_convert import convert_to_html
        result = convert_to_html(base_hwpx)
        assert 'charset="utf-8"' in result or "charset=utf-8" in result.lower()

    def test_korean_font_in_style(self, base_hwpx):
        from hwp_convert import convert_to_html
        result = convert_to_html(base_hwpx)
        assert "Noto Sans KR" in result or "Malgun Gothic" in result

    def test_save_to_file(self, base_hwpx, tmp_path):
        from hwp_convert import convert_to_html
        out = str(tmp_path / "output.html")
        result = convert_to_html(base_hwpx)
        with open(out, "w", encoding="utf-8") as f:
            f.write(result)
        assert os.path.exists(out)
        assert os.path.getsize(out) > 100


# ---------------------------------------------------------------------------
# convert_to_pdf  (pyhwp2md + WeasyPrint 필요)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not _pyhwp2md_available() or not _weasyprint_available(),
    reason="pyhwp2md 또는 WeasyPrint 미설치",
)
class TestConvertToPdf:
    def test_pdf_created(self, base_hwpx, tmp_path):
        from hwp_convert import convert_to_pdf

        out = str(tmp_path / "output.pdf")
        convert_to_pdf(base_hwpx, out)
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_pdf_header(self, base_hwpx, tmp_path):
        from hwp_convert import convert_to_pdf

        out = str(tmp_path / "output.pdf")
        convert_to_pdf(base_hwpx, out)
        with open(out, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"

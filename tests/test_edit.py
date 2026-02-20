"""
hwp_edit.py 테스트.

- replace_text: 텍스트 치환
- add_paragraph: 단락 추가
- add_table: 표 추가
"""

import os
import zipfile

import pytest

from hwp_edit import replace_text, add_paragraph, add_table
from hwp_read import read_file
from hwp_analyze import analyze


class TestReplaceText:
    def test_output_exists(self, base_hwpx, tmp_path):
        out = str(tmp_path / "replaced.hwpx")
        replace_text(base_hwpx, out, "첫 번째", "수정된")
        assert os.path.exists(out)

    def test_output_is_valid_hwpx(self, base_hwpx, tmp_path):
        out = str(tmp_path / "replaced.hwpx")
        replace_text(base_hwpx, out, "첫 번째", "수정된")
        assert zipfile.is_zipfile(out)

    def test_replaced_text_appears_in_content(self, base_hwpx, tmp_path):
        out = str(tmp_path / "replaced.hwpx")
        replace_text(base_hwpx, out, "첫 번째", "수정된")
        content = read_file(out, "md")
        assert "수정된" in content

    def test_replace_with_empty_string(self, base_hwpx, tmp_path):
        """빈 문자열로 치환 (삭제 효과)."""
        out = str(tmp_path / "deleted.hwpx")
        replace_text(base_hwpx, out, "두 번째", "")
        assert os.path.exists(out)

    def test_source_file_unchanged(self, base_hwpx, tmp_path):
        """원본 파일은 변경되지 않아야 한다."""
        import shutil

        backup = str(tmp_path / "backup.hwpx")
        shutil.copy2(base_hwpx, backup)
        out = str(tmp_path / "replaced.hwpx")
        replace_text(base_hwpx, out, "단락", "paragraph")

        original_content = read_file(backup, "md")
        current_content = read_file(base_hwpx, "md")
        assert original_content == current_content

    def test_nonexistent_text_no_crash(self, base_hwpx, tmp_path):
        """존재하지 않는 텍스트 치환 시 크래시 없이 파일 생성."""
        out = str(tmp_path / "noop.hwpx")
        replace_text(base_hwpx, out, "절대없는텍스트XYZ123", "대체")
        assert os.path.exists(out)


class TestAddParagraph:
    def test_output_exists(self, base_hwpx, tmp_path):
        out = str(tmp_path / "added.hwpx")
        add_paragraph(base_hwpx, out, "새로 추가된 단락")
        assert os.path.exists(out)

    def test_output_is_valid_hwpx(self, base_hwpx, tmp_path):
        out = str(tmp_path / "added.hwpx")
        add_paragraph(base_hwpx, out, "새로 추가된 단락")
        assert zipfile.is_zipfile(out)

    def test_added_text_in_content(self, base_hwpx, tmp_path):
        out = str(tmp_path / "added.hwpx")
        add_paragraph(base_hwpx, out, "추가된고유텍스트UNIQUE")
        content = read_file(out, "md")
        assert "추가된고유텍스트UNIQUE" in content

    def test_paragraph_count_increases(self, base_hwpx, tmp_path):
        out = str(tmp_path / "added.hwpx")
        before = analyze(base_hwpx)["stats"]["paragraph_count"]
        add_paragraph(base_hwpx, out, "추가 단락")
        after = analyze(out)["stats"]["paragraph_count"]
        assert after > before


class TestAddTable:
    def test_output_exists(self, base_hwpx, tmp_path):
        out = str(tmp_path / "tabled.hwpx")
        add_table(base_hwpx, out, ["열1", "열2"], [["A", "B"], ["C", "D"]])
        assert os.path.exists(out)

    def test_output_is_valid_hwpx(self, base_hwpx, tmp_path):
        out = str(tmp_path / "tabled.hwpx")
        add_table(base_hwpx, out, ["열1", "열2"], [["A", "B"]])
        assert zipfile.is_zipfile(out)

    def test_single_column_table(self, base_hwpx, tmp_path):
        out = str(tmp_path / "single_col.hwpx")
        add_table(base_hwpx, out, ["단일열"], [["값1"], ["값2"]])
        assert os.path.exists(out)

    def test_empty_rows_table(self, base_hwpx, tmp_path):
        """헤더만 있고 행이 없는 표."""
        out = str(tmp_path / "header_only.hwpx")
        add_table(base_hwpx, out, ["A", "B", "C"], [])
        assert os.path.exists(out)

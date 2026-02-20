"""
공통 pytest 픽스처 및 설정.
"""

import os
import sys
import pytest

# scripts/ 디렉토리를 import 경로에 추가
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)


@pytest.fixture(scope="session")
def scripts_dir():
    return SCRIPTS_DIR


@pytest.fixture(scope="session")
def samples_dir():
    return SAMPLES_DIR


@pytest.fixture(scope="session")
def sample_md(samples_dir):
    """tests/samples/sample.md 경로."""
    return os.path.join(samples_dir, "sample.md")


@pytest.fixture()
def tmp_hwpx(tmp_path):
    """테스트용 임시 HWPX 출력 경로."""
    return str(tmp_path / "output.hwpx")


@pytest.fixture(scope="session")
def base_hwpx(tmp_path_factory, sample_md):
    """세션 전체에서 재사용할 기본 HWPX 파일 (hwp_create로 생성)."""
    from hwp_create import create_hwpx_from_paragraphs

    out = str(tmp_path_factory.mktemp("session") / "base.hwpx")
    create_hwpx_from_paragraphs(
        out,
        title="테스트 문서",
        author="pytest",
        paragraphs=["첫 번째 단락입니다.", "두 번째 단락입니다.", "세 번째 단락입니다."],
    )
    return out

from __future__ import annotations

import atexit
import os
import shutil
import sys
import tempfile
from io import BytesIO
from pathlib import Path
import jpype

from typing import TYPE_CHECKING
from zipfile import ZipFile

import pytest
import requests
import scyjava
import scyjava.config

if TYPE_CHECKING:
    from collections.abc import Iterator

URL = "https://www.dropbox.com/scl/fi/d3ape29urgt15iaue73om/bioformats_test_data.zip?rlkey=3j0bl9ef0rolb2k7pydr3jvw7&st=ylf7g4oh&dl=1"
TEST_DATA = Path(__file__).parent / "data"
SKIP_EXTENSIONS = {".sldy"}
URL_TXT = TEST_DATA / "url.txt"


def download() -> None:
    if URL_TXT.exists():
        if URL_TXT.read_text() == URL:
            return
        URL_TXT.unlink()

    print("Downloading test data...")
    TEST_DATA.mkdir(exist_ok=True, parents=True)
    response = requests.get(URL, stream=True)
    total_length = response.headers.get("content-length")

    f = BytesIO()
    if total_length is None:  # no content length header
        f.write(response.content)
    else:
        dl = 0
        total_length_i = int(total_length)
        for data in response.iter_content(chunk_size=total_length_i // 100):
            dl += len(data)
            f.write(data)
            done = int(50 * dl / total_length_i)
            sys.stdout.write(f"\r[{'=' * done}{' ' * (50 - done)}]")
            sys.stdout.flush()

    shutil.rmtree(TEST_DATA, ignore_errors=True)
    with ZipFile(f) as zf:
        zf.extractall(str(TEST_DATA.parent))
    shutil.rmtree(TEST_DATA / "__MACOSX", ignore_errors=True)
    URL_TXT.write_text(URL)


download()
DATA_FILES = sorted([x for x in TEST_DATA.iterdir() if x != URL_TXT])


@pytest.fixture(scope="session", params=DATA_FILES, ids=lambda x: x.name)
def test_file(request: pytest.FixtureRequest) -> Path:
    """
    Fixture to provide a test file from the data folder.
    """
    filename: Path = request.param
    if filename.suffix in SKIP_EXTENSIONS:
        pytest.skip(f"Skipping {filename.suffix} files")

    return filename


def pytest_sessionstart() -> None:
    # https://jpype.readthedocs.io/en/latest/userguide.html#errors-reported-by-python-fault-handler
    if os.name == "nt":
        import faulthandler

        faulthandler.enable()
        faulthandler.disable()


# register pytest --allow-cache option
def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--allow-cache",
        action="store_true",
        default=False,
        help="Allow cache to be used for tests",
    )


@pytest.fixture(autouse=True, scope="session")
def cache_dirs(request: pytest.FixtureRequest) -> Iterator[Path | None]:
    """Ensure we test on a clean cache, and don't pollute the user's cache."""
    # caching significantly speeds up tests, but we want to ensure that
    # we test on a clean cache, and don't pollute the user's cache.
    # If the user has set ALLOW_CACHE, we will use the actual cache directories.
    # Otherwise, we will use a temporary directory.
    if request.config.getoption("--allow-cache") or os.getenv("ALLOW_CACHE", ""):
        print("Reading/writing to actual user cache directories")
        yield None
        return

    tmp_path = Path(tempfile.mkdtemp())
    os.environ["CJDK_CACHE_DIR"] = str(tmp_path / "cjdk")

    os.environ["JGO_CACHE_DIR"] = jgo = str(tmp_path / "jgo")
    scyjava.config.set_cache_dir(jgo)

    m2_repo = tmp_path / "m2" / "repository"
    m2_repo.mkdir(parents=True, exist_ok=True)
    os.environ["M2_REPO"] = _m2_repo = str(m2_repo)
    os.environ["MAVEN_OPTS"] = f"-Dmaven.repo.local={_m2_repo}"
    scyjava.config.set_m2_repo(_m2_repo)

    yield tmp_path

    # doing manual cleanup here to avoid windows file locks on jars during teardown
    @atexit.register
    def _cleanup() -> None:
        if jpype.isJVMStarted():
            jpype.shutdownJVM()
        shutil.rmtree(tmp_path, ignore_errors=True)

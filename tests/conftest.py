from pathlib import Path
from re import U
import pytest
import shutil
import sys
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import requests


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
        total_length = int(total_length)
        for data in response.iter_content(chunk_size=total_length // 100):
            dl += len(data)
            f.write(data)
            done = int(50 * dl / total_length)
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

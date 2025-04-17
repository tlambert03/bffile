from pathlib import Path

import pytest

from bffile import BioFile

DATA_FILES = sorted((Path(__file__).parent / "data").iterdir())
SKIP_EXTENSIONS = {".sldy"}


@pytest.mark.parametrize("filename", DATA_FILES, ids=lambda p: p.name)
def test_bffile(filename: Path) -> None:
    if filename.suffix in SKIP_EXTENSIONS:
        pytest.skip(f"Skipping {filename.suffix} files")

    with BioFile(filename) as bf:
        assert bf.to_numpy() is not None
        assert bf.to_dask() is not None
        assert bf.shape

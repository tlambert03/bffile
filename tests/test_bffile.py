from pathlib import Path

from bffile import BioFile


def test_bffile(test_file: Path) -> None:
    with BioFile(test_file) as bf:
        assert bf.to_numpy() is not None
        assert bf.to_dask() is not None
        assert bf.shape

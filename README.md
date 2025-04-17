# bffile

[![License](https://img.shields.io/pypi/l/bffile.svg?color=green)](https://github.com/tlambert03/bffile/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/bffile.svg?color=green)](https://pypi.org/project/bffile)
[![Python Version](https://img.shields.io/pypi/pyversions/bffile.svg?color=green)](https://python.org)
[![CI](https://github.com/tlambert03/bffile/actions/workflows/ci.yml/badge.svg)](https://github.com/tlambert03/bffile/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tlambert03/bffile/branch/main/graph/badge.svg)](https://codecov.io/gh/tlambert03/bffile)

Yet another Bio-Formats wrapper for python

## Installation

```bash
pip install git+https://github.com/tlambert03/bffile
```

## Usage

```python
from bffile import BioFile

with BioFile("tests/data/ND2_dims_p4z5t3c2y32x32.nd2") as bf:
    print(bf.ome_metadata)  # ome_types.OME object
    print(bf.shape)  # shows full shape
    data = bf.to_numpy(series=1)
    print(data.shape, data.dtype)
```

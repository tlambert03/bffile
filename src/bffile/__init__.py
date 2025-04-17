"""Yet another Bio-Formats wrapper for Python."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("bffile")
except PackageNotFoundError:
    __version__ = "uninstalled"

from ._biofile import BioFile

__all__ = ["BioFile"]

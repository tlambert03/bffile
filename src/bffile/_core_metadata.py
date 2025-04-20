from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, NamedTuple

if TYPE_CHECKING:
    import loci.formats
    import numpy as np
    from typing_extensions import Self


class OMEShape(NamedTuple):
    """NamedTuple with OME metadata shape."""

    t: int
    c: int
    z: int
    y: int
    x: int
    rgb: int

    def __repr__(self) -> str:
        return (
            f"(t={self.t}, c={self.c}, z={self.z}, "
            f"y={self.y}, x={self.x}, rgb={self.rgb})"
        )


@dataclass
class CoreMetadata:
    dtype: np.dtype
    shape: OMEShape
    rgb_count: int = 0
    thumb_size_x: int = 0
    thumb_size_y: int = 0
    bits_per_pixel: int = 0
    image_count: int = 0
    modulo_z: Any = None
    modulo_c: Any = None
    modulo_t: Any = None
    dimension_order: str = ""
    is_order_certain: bool = False
    is_rgb: bool = False
    is_little_endian: bool = False
    is_interleaved: bool = False
    is_indexed: bool = False
    is_false_color: bool = True
    is_metadata_complete: bool = False
    is_thumbnail_series: bool = False
    series_metadata: dict[str, Any] = field(default_factory=dict)
    resolution_count: int = 1

    @classmethod
    def from_java(cls, meta: loci.formats.CoreMetadata) -> Self:
        from ._jimports import pixtype2dtype

        if size_zt := meta.sizeZ * meta.sizeT:
            eff_size_c = meta.imageCount // size_zt
        else:
            eff_size_c = 1

        if eff_size_c == 0:
            rgb_count = 1
        else:
            rgb_count = meta.sizeC // eff_size_c

        return cls(
            dtype=pixtype2dtype(meta.pixelType, meta.littleEndian),
            shape=OMEShape(
                x=meta.sizeX,
                y=meta.sizeY,
                z=meta.sizeZ,
                c=eff_size_c,
                t=meta.sizeT,
                rgb=rgb_count,
            ),
            thumb_size_x=meta.thumbSizeX,
            thumb_size_y=meta.thumbSizeY,
            bits_per_pixel=meta.bitsPerPixel,
            image_count=meta.imageCount,
            modulo_z=meta.moduloZ,
            modulo_c=meta.moduloC,
            modulo_t=meta.moduloT,
            dimension_order=meta.dimensionOrder,
            is_order_certain=meta.orderCertain,
            is_rgb=meta.rgb,
            is_little_endian=meta.littleEndian,
            is_interleaved=meta.interleaved,
            is_indexed=meta.indexed,
            is_false_color=meta.falseColor,
            is_metadata_complete=meta.metadataComplete,
            is_thumbnail_series=meta.thumbnail,
            series_metadata=dict(meta.seriesMetadata),
            resolution_count=meta.resolutionCount,
        )

from numpy import stack, uint8
from tifffile import imwrite

__all__ = ["SaveMaskBigtiff"]


def SaveMaskBigtiff(pathMask, mask):
    """Save array as BigTiff file format.

    Parameters
    ----------
    pathMask : string
        Save file path

    mask : 2-D Array
        Boolean type mask array

    Returns
    -------
    None

    Example
    -------
    >>> import numpy as np

    >>> mask = np.zeros((10000, 10000), dtype=bool)
    >>> SaveMaskBigtiff("test.tif", mask)
    """
    mask = (mask*255).astype(uint8)
    imwrite(pathMask, stack([mask, mask, mask], 2), compression="lzw", bigtiff=True, tile=(256, 256))

    return None

# <Lixx_TIF, a model for Image transformation.>
# Copyright (C) <2018>  <Xiaowei Li, Xixiang Zhu>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# @Email: Xiaowei Li<lixiaowei7@live.cn>
# @Email: Xixiang Zhu<hixxzhu@gmail.com>

import math
import numpy as np

def bytescale(data, cmin=None, cmax=None, high=255, low=0):
    """
    Byte scales an array (image).

    Byte scaling means converting the input image to uint8 dtype and scaling
    the range to ``(low, high)`` (default 0-255).
    If the input image already has dtype uint8, no scaling is done.

    Parameters
    ----------
    data : ndarray
        PIL image data array.
    cmin : scalar, optional
        Bias scaling of small values. Default is ``data.min()``.
    cmax : scalar, optional
        Bias scaling of large values. Default is ``data.max()``.
    high : scalar, optional
        Scale max value to `high`.  Default is 255.
    low : scalar, optional
        Scale min value to `low`.  Default is 0.

    Returns
    -------
    img_array : uint8 ndarray
        The byte-scaled array.

    Examples
    --------
    >>> from scipy.misc import bytescale
    >>> img = np.array([[ 91.06794177,   3.39058326,  84.4221549 ],
    ...                 [ 73.88003259,  80.91433048,   4.88878881],
    ...                 [ 51.53875334,  34.45808177,  27.5873488 ]])
    >>> bytescale(img)
    array([[255,   0, 236],
           [205, 225,   4],
           [140,  90,  70]], dtype=uint8)
    >>> bytescale(img, high=200, low=100)
    array([[200, 100, 192],
           [180, 188, 102],
           [155, 135, 128]], dtype=uint8)
    >>> bytescale(img, cmin=0, cmax=255)
    array([[91,  3, 84],
           [74, 81,  5],
           [52, 34, 28]], dtype=uint8)

    """
    if data.dtype == np.uint8:
        return data

    if high > 255:
        raise ValueError("`high` should be less than or equal to 255.")
    if low < 0:
        raise ValueError("`low` should be greater than or equal to 0.")
    if high < low:
        raise ValueError("`high` should be greater than or equal to `low`.")

    if cmin is None:
        cmin = data.min()
    if cmax is None:
        cmax = data.max()

    cscale = cmax - cmin
    if cscale < 0:
        raise ValueError("`cmax` should be larger than `cmin`.")
    elif cscale == 0:
        cscale = 1

    scale = float(high - low) / cscale
    bytedata = (data - cmin) * scale + low
    return (bytedata.clip(low, high) + 0.5).astype(np.uint8)

def _bilinear(p_00, p_01, p_10, p_11, frac_w, frac_h):
    return (1 - frac_w) * (1 - frac_h) * p_00 + (1 - frac_w) * frac_h * p_01 + frac_w * (1 - frac_h) * p_10 + frac_w * frac_h * p_11

def bilinear_interpolation(img, multiple=1):
    """resize the img with multiple"""

    if img.dtype != np.uint8:
        raise ValueError("The array's dtype must be uint8.")

    srcHeight, srcWidth = img.shape
    dstWidth = math.floor(srcWidth * multiple)
    dstHeight = math.floor(srcHeight * multiple)

    dst_img = np.zeros((dstHeight, dstWidth), dtype=np.uint8)

    for dst_h in range(len(dst_img)):
        for dst_w in range(len(dst_img[dst_h])):
            src_h = dst_h * srcHeight / dstHeight
            src_w = dst_w * srcWidth / dstWidth
            
            inte_h = math.floor(src_h)
            inte_w = math.floor(src_w)
            frac_h = src_h - inte_h
            frac_w = src_w - inte_w

            p_00 = img[inte_h][inte_w]
            p_01 = img[inte_h][inte_w + 1 < srcWidth and inte_w + 1 or inte_w]
            p_10 = img[inte_h + 1 < srcHeight and inte_h + 1 or inte_h][inte_w]
            p_11 = img[inte_h + 1 < srcHeight and inte_h + 1 or inte_h][inte_w + 1 < srcWidth and inte_w + 1 or inte_w]

            dst_img[dst_h][dst_w] = _bilinear(p_00, p_01, p_10, p_11, frac_w, frac_h)
    
    return dst_img
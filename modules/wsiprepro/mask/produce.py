from cv2 import cvtColor, fillPoly, inRange, split, GaussianBlur, Laplacian, COLOR_RGB2HSV_FULL, CV_8U
from numpy import array, ones, uint8, zeros

__all__ = ["CvtHSVLDic", "RangeSelecter", "RegionMasking", "CorrdinateMasking"]


def CvtHSVLDic(img):
    """Split and convert RGB chennel uint8 array to Hue, Saturation, Value, Laplacian.

    Parameters
    ----------
    img : 3-D Array
        Original RGB chennel array will convert and split

    Returns
    -------
    hsvlDic : Dictionary
        Contained Hue, Saturation, Value, Laplacian array
        {'h' : Hue 2-D Array,
        's' : Saturation 2-D Array,
        'v' : Value 2-D Array,
        'l' : Laplacian 2-D Array}

    Example
    -------
    >>>import matplotlib.pyplot as plt
    >>>import numpy as np
    >>> import cv2

    >>> img = np.ones((4, 4, 3))
    >>> img = np.random.normal(img, 1)*255
    >>> img = cv2.resize(img, dsize=(64, 64))
    >>> img = img.astype(np.uint8)
    >>> hsvlDic = CvtHSVLDic(img)

    >>> plt.imshow(hsvlDic['h'], "hsv")
    >>> plt.show()
    >>> plt.imshow(hsvlDic['s'], "gray")
    >>> plt.show()
    >>> plt.imshow(hsvlDic['v'], "binary")
    >>> plt.show()
    >>> plt.imshow(hsvlDic['l'], "gray")
    >>> plt.show()
    """
    imgH, imgS, imgV = split(cvtColor(img, COLOR_RGB2HSV_FULL))
    imgL = Laplacian(imgV, CV_8U, ksize=3)

    return {'h' : imgH, 's' : imgS, 'v' : imgV, 'l' : imgL}

def RangeSelecter(hsvlDic, rangeSelectDic):
    """Get color range and divid color in or out range.
    
    And calculate intersection region each case.
    
    Parameters
    ----------
    hsvlDic : Dictionary
        Contained Hue, Saturation, Value, Laplacian array
        {'h' : Hue 2-D Array,
        's' : Saturation 2-D Array,
        'v' : Value 2-D Array,
        'l' : Laplacian 2-D Array}

    rangeSelectDic : Dictionary
        Contained Hue, Saturation, Value, Laplacian selection range
        {'h' : (start, end),
        's' : (start, end),
        'v' : (start, end),
        'l' : (start, end)}
    
    Returns
    -------
    imgT : 2-D Array
        Intersection array with each 'h', 's', 'v', 'l' color range selected region

    See Also
    --------
    CvtHSVLDic : Split and convert RGB chennel uint8 array to Hue, Saturation, Value, Laplacian.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> import cv2

    >>> img = np.ones((4, 4, 3))
    >>> img = np.random.normal(img, 1)*255
    >>> img = cv2.resize(img, dsize=(64, 64))
    >>> img = img.astype(np.uint8)
    >>> hsvlDic = CvtHSVLDic(img)

    >>> rangeSelectDic = {'h' : (64, 255), 's' : (64, 255), 'v' : (64, 255), 'l' : (0, 64)}
    >>> mask = RangeSelecter(hsvlDic, rangeSelectDic)

    >>> plt.imshow(mask)
    >>> plt.show()
    """
    imgT = ones((hsvlDic['h'].shape[0], hsvlDic['h'].shape[1]), dtype=uint8)
    # Calculate intersection as boolean multuple
    for _type in ('h', 's', 'v', 'l'):
        imgT *= inRange(hsvlDic[_type], rangeSelectDic[_type][0], rangeSelectDic[_type][1])

    return imgT.astype(float)

def RegionMasking(hsvlDic, rangeSelectList, gauthSelect):
    """Make color range selected specific region as Mask.

    Process
    1. Make empty mask array as same as input image size.
    2. Calculate specific region by using RangeSelecter function.
    3. Add region to mask like union until all use rangeSelectList.
    4. Use Gaussian blurring and Thresholding in mask.

    Parameters
    ----------
    hsvlDic : Dictionary
        Contained Hue, Saturation, Value, Laplacian array.
        {'h' : Hue 2-D Array,
        's' : Saturation 2-D Array,
        'v' : Value 2-D Array,
        'l' : Laplacian 2-D Array}

    rangeSelectList : List
        List of color range dictionary.
        Each dictionary contained Hue, Saturation, Value, Laplacian selection range.
        {'h' : (start, end),
        's' : (start, end),
        'v' : (start, end),
        'l' : (start, end)}

    gauthSelect : Dictionary
        Gaussian blurring x, sigma value and thresholding value.
        {"gX" : x value, "gS" : sigma value, "th" : threshold value}

    Returns
    -------
    mask : 2-D Array
        Color selected region mask array.

    See Also
    --------
    CvtHSVLDic : Split and convert RGB chennel uint8 array to Hue, Saturation, Value, Laplacian.
    RangeSelecter : Get color range and divid color in or out range.

    Examples
    --------
    >>> import numpy as np
    >>> import openslide

    >>> rangeSelectList = [{'h' : (128, 250), 's' : (20, 250), 'v' : (60, 240), 'l' : (20, 255)}]
    >>> gauthSelect = {"gX" : 31,"gS" : 21, "th" : 0.2}

    >>> handleWSI = openslide.OpenSlide(WSI file path)
    >>> img = np.array(handleWSI.read_region((0, 0), 2, handleWSI.level_dimensions[2]).convert("RGB"))

    >>> hsvlDic = CvtHSVLDic(img)
    >>> ShowSelectHistogram(hsvlDic, rangeSelectList[0])
    >>> maskSpec = RegionMasking(hsvlDic, rangeSelectList, gauthSelect)
    """
    # Process 1
    mask = zeros((hsvlDic['h'].shape[0], hsvlDic['h'].shape[1]))
    # Process 2 (for), 3 (+=)
    for rangeSelectDic in rangeSelectList:
        mask += RangeSelecter(hsvlDic, rangeSelectDic)
    # Process 4
    mask = inRange(GaussianBlur(mask, (gauthSelect["gX"], gauthSelect["gX"]), gauthSelect["gS"]), gauthSelect["th"], 1).astype(bool)

    return mask

def CorrdinateMasking(sizes, downsample, coordinates):
    """Make annotation region as Mask.

    Draw each polygon from coordinates data into mask array.
    Coordinates have downsampling referred on downsample parameter.

    Parameters
    ----------
    sizes : Tuple
        Mask size. (y, x)

    downsample : Float
        Coordinates downsample value.
        Each corrdinate will be divided this parameter.

    coordinates : List
        List of multi ploygon.
        First list has polygon list.
        Second list is just outer list to easily use cv2.fill polygon function.

    Returns
    -------
    mask : 2-D Array
        Annotation region mask array.

    Examples
    --------
    >>> import matplotlib.pyplot as plt

    >>> coor1 = [[10,10], [10,20], [20,10]]
    >>> coor2 = [[30,30], [30,40], [40,40], [40,30]]
    >>> coorTot = [[coor1], [coor2]]
    >>> size = (6, 6)

    >>> mask = CorrdinateMasking(size, 10, coorTot)
    >>> plt.imshow(mask)
    >>> plt.show()
    """
    mask = zeros((sizes[0], sizes[1]), dtype=uint8)
    for coordinatesParts in coordinates:
        coordinatesMini = (array(coordinatesParts[0]) / downsample).astype(int)
        mask = fillPoly(mask, pts=[coordinatesMini], color=1)
    mask = mask.astype(bool)

    return mask

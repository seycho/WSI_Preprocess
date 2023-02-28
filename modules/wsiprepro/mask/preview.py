from cv2 import cvtColor, fillPoly, imwrite, inRange, resize, COLOR_BGR2RGB
from matplotlib.pyplot import axis, axvspan, figure, imshow, plot, show, subplot, title, yscale
from numpy import histogram, hstack, uint8
from numpy.linalg import norm

__all__ = ["DiagnoalNormalize", "ShowSelectHistogram", "ShowOverlapMask"]


def DiagnoalNormalize(lengthX, lengthY):
    """Calculate normalized diagnoal length.

    Parameters
    ----------
    lengthX : Float

    lengthY : Float

    Returns
    -------
    normalizeX, normalizeY : Tuple
        Normalized X, Y value. (normalizeX**2 + normalizeY**2 = 1)

    Examples
    --------
    >>> norX, norY = DiagnoalNormalize(4, 3)
    >>> print(norX, norY)
    0.8 0.6
    >>> print(norX**2 + norY**2)
    1
    """
    lengthDiagonal = norm([lengthX, lengthY])
    normalizeX = lengthX/lengthDiagonal
    normalizeY = lengthY/lengthDiagonal

    return normalizeX, normalizeY

def ShowSelectHistogram(hsvlDic, rangeSelectDic):
    """Show process step of RangeSelecter function.

    This function just show process of color range selection in using RangeSelecter process.
    First figures are splited and converted chennel mask about "Hue", "Saturation", "Value", "Laplacian".
    Second figures show histogram of color value and selected color range.
    Final figures selected region at each chennel.
    
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
    None

    See Also
    --------
    RangeSelecter : Get color range and divid color in or out range.
    """
    yImg, xImg = hsvlDic['h'].shape

    xHisto = 10
    yHisto = 6
    
    typeDic = {'h':"Hue",'s':"Saturation",'v':"Value",'l':"Laplacian"}
    cmapDic = {'h':"hsv",'s':"gray",'v':"binary",'l':"gray"}

    imgXNor, imgYNor = DiagnoalNormalize(xImg, yImg)
    histoXNor, histoYNor = DiagnoalNormalize(xHisto, yHisto)

    figsizeX, figsizeY = DiagnoalNormalize(4*imgXNor, imgYNor)
    figure(figsize=(20*figsizeX, 20*figsizeY))
    for _num, _type in enumerate(('h', 's', 'v', 'l')):
        subplot(1,4,_num+1)
        title("%s Image"%typeDic[_type])
        imshow(hsvlDic[_type],cmapDic[_type])
        axis("off")
    show()
    
    figsizeX, figsizeY = DiagnoalNormalize(4*histoXNor, histoYNor)
    figure(figsize=(20*figsizeX, 20*figsizeY))
    for _num, _type in enumerate(('h', 's', 'v', 'l')):
        histo, x = histogram(hstack(hsvlDic[_type]), bins=64, range=(0, 255))
        subplot(1,4,_num+1)
        title("Histogram")
        plot(x[:-1], histo, "blue")
        yscale("log")
        axvspan(rangeSelectDic[_type][0], rangeSelectDic[_type][1], alpha=0.5, color='red')
    show()

    figsizeX, figsizeY = DiagnoalNormalize(4*imgXNor, imgYNor)
    figure(figsize=(20*figsizeX, 20*figsizeY))
    for _num, _type in enumerate(('h', 's', 'v', 'l')):
        subplot(1,4,_num+1)
        title("Selected Mask")
        imshow(inRange(hsvlDic[_type], rangeSelectDic[_type][0], rangeSelectDic[_type][1]))
        axis("off")
    show()

    return None

def ShowOverlapMask(img, mask, ratio=1/4, pathSave=None):
    """Show masked region on original image.

    Parameters
    ----------
    img : 3-D Array
        Original RGB chennel array.

    mask : 2-D Array
        Boolean type mask array will overlapping.

    ratio : Float
        Draw overlapped image's downsample ratio.

    pathSave : String, default: None
        Save overlapped image's path. if None, it will be not saved.
    """
    y, x, _ = img.shape
    preVimg = resize(img.astype(float), dsize=(int(x*ratio), int(y*ratio)))
    preVmask = resize(mask.astype(float), dsize=(int(x*ratio), int(y*ratio)))
    preVmask = preVmask.round().astype(bool)
    preVimg[preVmask == False] /= 2
    preVimg = preVimg.astype(uint8)

    imshow(preVimg)
    show()

    if pathSave:
        imwrite(pathSave, cvtColor(preVimg, COLOR_BGR2RGB))

    return None
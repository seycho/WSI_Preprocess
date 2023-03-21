from cv2 import resize
from openslide import OpenSlide
from numpy import  arange, array, log10, meshgrid, uint8, stack
from numpy.random import shuffle
from tifffile import imread, imwrite

__all__ = ["SaveMaskBigtiff", "GetBoundsDic", "GetMppDic", "GetRandomCoordinates", "WSIPatchImporter"]


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

def GetBoundsDic(properties):
    """Make bounds informations dictionary from WSI properties.

    Parameters
    ----------
    properties : openslide._PropertyMap
        WSI properties, like dictionary type.

    Returns
    -------
    boundsDic : Dictionary
        bounds x, y, width, height dictionary.
    """
    boundsDic = {}
    if "openslide.bounds-x" in properties:
        boundsDic['x'] = int(properties["openslide.bounds-x"])
        boundsDic['y'] = int(properties["openslide.bounds-y"])
        boundsDic['w'] = int(properties["openslide.bounds-width"])
        boundsDic['h'] = int(properties["openslide.bounds-height"])
    else:
        boundsDic['x'] = 0
        boundsDic['y'] = 0
        boundsDic['w'] = int(properties["openslide.level[0].width"])
        boundsDic['h'] = int(properties["openslide.level[0].height"])

    return boundsDic

def GetMppDic(properties):
    """Make micron per pixel informations dictionary from WSI properties.

    Parameters
    ----------
    properties : openslide._PropertyMap
        WSI properties, like dictionary type.

    Returns
    -------
    mppDic : Dictionary
        mpp x, y, min dictionary.
    """
    mppDic = {}
    _x = float(properties["openslide.mpp-x"])
    _y = float(properties["openslide.mpp-y"])
    mppDic['x'] = _x
    mppDic['y'] = _y
    mppDic["min"] = min(_x, _y)

    return mppDic

def GetRandomCoordinates(sizePatch, sizeFull):
    """Make random coordinates of patch images.

    Divide WSI's width and height by patch size.
    Consist coordination by using combination each x, y coordinate value.
    Finally return randomize coordinates array.

    Parameters
    ----------
    sizePatch : 2-D Array
        Pixel size of each patch image's width and height.

    sizeFull : 2-D Array
        Entire size of full image.
    
    Returns
    -------
    combinations : 3-D Array
        Randomized patch image's coordinates array.

    Examples
    --------
    >>> import numpy as np

    >>> GetRandomCoordinates(np.array([5, 5]), np.array([20, 20]))
    array([[10,  0],
           [ 5, 10],
           [10, 10],
           [ 0,  5],
           [ 0, 10],
           [ 0,  0],
           [10,  5],
           [ 5,  5],
           [ 5,  0]])
    """
    patchX, patchY = sizePatch
    fullX, fullY = sizeFull

    xArange = arange(0, fullX - patchX, patchX)
    yArange = arange(0, fullY - patchY, patchY)
    combinations = array(meshgrid(xArange, yArange)).T.reshape(-1,2)
    shuffle(combinations)

    return combinations, len(xArange), len(yArange)

class WSIPatchImporter:
    """WSI patch image and mask import class.

    This class to easily load WSi patch image and masking region.
    When declarate class, Initialize patch size at 500 micron and 250 interval size.
    Set default WSI slide level as fit on 128 pixel resizing image.

    Parameters
    ----------
    pathWSI : String
        WSI file path.
    pathSpec : String
        Specific mask file path.
    pathAnno : String
        Annotation mask file path.

    Attributes
    ----------
    handle : Dictionary
        Bigtiff handle value, it has "WSI", "spec", "anno" keys
        WSI = openslide handle
        spec, anno = tifffile mask handle
    boundsDic : Dictionary
        WSI boundary information dictionary
        'x' (x axis boundary coordinate), 'y' (y axis boundary coordinate),
        'w' (whole slide image width), 'h' (whole slide image height)
    mppDic : Dictionary
        Micron per pixel parameters abour slide image.
        'x' (x mpp), 'y' (y mpp), "min" (minimun value in x, y)
    downsampleDic : Dictionary
        Level 0 slide image size / some of image size value.
    level : Int
        Current import slide level.
    sizePixelXY : Dictionary
        Current patch image import pixel size.
    sizeRePixelXY
        Current patch image resizing pixel size.

    Method
    ------
    SetProperties(self)
        Initial method of set Whole Slide Image's properties as easily readable value.
    SetDownsamples(self)
        Initial method of calculate downsample ratio of WSI and mask.
    MakePatchCoordinates(self, sizeMicronXY, intervalMicronXY, sizeRePixelXY)
        Create patch image coordinates and set default import size.
    LoadImage(self, coordinate, level=None, size=None, sizeRe=None)
        WSI patch image import.
    LoadMask(self, maskType, coordinate, size=None)
        Mask array import.
    IsUsfulMask(self, maskType, coordinatesList, ratioPass=0.5, size=None)
        Check mask array usable.
    """
    def __init__(self, pathWSI, pathSpec, pathAnno):

        self.maskTypeList = ["spec", "anno"]
        self.handle = {}
        self.handle["WSI"] = OpenSlide(pathWSI)
        self.handle["spec"] = imread(pathSpec)
        self.handle["anno"] = imread(pathAnno)

        self.SetProperties()
        self.SetDownsamples()
        self.MakePatchCoordinates(array([500, 500]), array([250, 250]), array([128, 128]))

    def SetProperties(self):
        """Initial method of set Whole Slide Image's properties as easily readable value.

        bounds x, y parameters are start coordinate of WSI.
        bounds w, h parameters are pixel size of WSI
        bounds parameters are based on level 0 slide image.

        mpp parameters will use convert micron size to pixel value.
        In many case mpp paramter's x and y values are same.
        But if they have different values, Default mpp paramter is set minimum case.
        """
        properties = self.handle["WSI"].properties
        self.boundsDic = GetBoundsDic(properties)
        self.mppDic = GetMppDic(properties)
        return None

    def SetDownsamples(self):
        """Initial method of calculate downsample ratio of WSI and mask.

        Set WSI level downsample list as ndarray type.
        Calcuate and set mask downsample value by (mask size / level 0 slide image size).
        """
        self.downsampleDic = {}
        self.downsampleDic["WSI"] = array(self.handle["WSI"].level_downsamples)
        for maskType in self.maskTypeList:
            _h, _w, _ = self.handle[maskType].shape
            self.downsampleDic[maskType] = array([self.boundsDic['w'] / _w, self.boundsDic['h'] / _h]).mean()
        return None

    def MakePatchCoordinates(self, sizeMicronXY, intervalMicronXY, sizeRePixelXY):
        """Create patch image coordinates and set default import size.

        Calculate apt slide level for import image from WSI file.
        Selected level is which has (image pixel size / double resizing pixel size) ratio nearest at 1.
        Pixel size is calculated by (micron size / minimum mpp parameter).
        Import image's pixel size and resizing pixel size will be saved Attributes parameter as sizePixelXY and sizeRePixelXY.
        Also each mask's import pixel size are saved sizePixelXY parameter.

        After that, When image importing by LoadMask Method and if not input size and level parameter,
        Automatically use default pixel size parameter which set on this Method.

        Parameters
        ----------
        sizeMicronXY : 2-D Array
            Micrometer patch size array [x, y].
        intervalMicronXY : 2-D Array
            Micrometer interval size array [x, y].
        sizeRePixelXY : 2-D Array
            Pixel image resizing array [x, y].

        Returns
        -------
        coordinates : 3-D Array
            Patch image start coordinates [x, y] array in slide level 0.

        See Also
        --------
        GetRandomCoordinates : Make random coordinates of patch images.
        LoadImage : WSI patch image import.
        LoadMask : Mask array import.
        """
        sizePixelXY = sizeMicronXY / self.mppDic['min']
        sizePixelLevel = sizePixelXY.mean() / self.downsampleDic["WSI"]
        sizeRatio = sizePixelLevel / 2 / sizeRePixelXY.mean()
        self.level = log10(sizeRatio).__abs__().argmin()
        self.sizePixelXY = {}
        self.sizePixelXY["WSI"] = (sizePixelXY / self.downsampleDic["WSI"][self.level]).round().astype(int)
        self.sizeRePixelXY = sizeRePixelXY

        for maskType in self.maskTypeList:
            downsampleMask = self.downsampleDic["WSI"][self.level] / self.downsampleDic[maskType]
            self.sizePixelXY[maskType] = (self.sizePixelXY["WSI"] * downsampleMask).round().astype(int)

        self.intervalPixelXY = (intervalMicronXY / self.mppDic['min']).astype(int)
        sizeFull = array([self.boundsDic['w'], self.boundsDic['h']])
        coordinates, lenX, lenY = GetRandomCoordinates(self.intervalPixelXY, sizeFull)
        self.numPatch = array([lenX, lenY])

        return coordinates

    def LoadImage(self, coordinate, level=None, size=None, sizeRe=None):
        """WSI patch image import.

        Using openslide read_region, patch image extract from WSI file.

        Parameters
        ----------
        coordinate : 2-D Array
            Start coordinate of patch image in slide level 0.
        level : Int, default: None
            Import slide level. Actually default parameter is self.level Attribute.
        size : 2-D Array, default: None
            Import slide pixel size. Actually default parameter is self.sizePixelXY["WSI"] Attribute.
        sizeRe : 2-D Array, default: None
            Patch image resizing size. Actually default parameter is self.sizeRePixelXY Attribute.

        Returns
        -------
        img : 3-D Array
            Imported patch image array.
        """
        x, y = coordinate
        x += self.boundsDic['x']
        y += self.boundsDic['y']
        if type(level) == type(None):
            level = self.level
        if type(size) == type(None):
            size = self.sizePixelXY["WSI"]
        if type(sizeRe) == type(None):
            sizeRe = self.sizeRePixelXY
        img = resize(array(self.handle["WSI"].read_region((x, y), level, size).convert("RGB")), dsize=sizeRe)

        return img

    def LoadMask(self, maskType, coordinate, size=None, sizeRe=None):
        """Mask array import.

        Import mask array from bigtiff mask file.
        Convert coordinate of WSI to downsample adjusted coordinate of mask.
        Just return one chennel array from tiff.

        Parameters
        ----------
        maskType : String
            Mask type ["spec", "anno"].
        coordinate : 2-D Array
            Start coordinate of patch image in slide level 0.
        size : 2-D Array, default: None
            Import mask size. Actually default parameter is self.sizePixelXY[maskType] Attribute.
        sizeRe : 2-D Array, default: None
            Patch image resizing size. Actually default parameter is self.sizeRePixelXY Attribute.

        Returns
        -------
        mask : 2-D Array
            Imported mask array.

        See Also
        --------
        IsUsfulMask : Check mask array usable.
        """
        coordinate = (coordinate / self.downsampleDic[maskType]).round().astype(int)
        if type(size) == type(None):
            size = self.sizePixelXY[maskType]
        if type(sizeRe) == type(None):
            sizeRe = self.sizeRePixelXY
        xSta = coordinate[1]
        xEnd = coordinate[1] + size[1]
        ySta = coordinate[0]
        yEnd = coordinate[0] + size[0]

        return resize(self.handle[maskType][xSta:xEnd,ySta:yEnd,0], dsize=sizeRe)

    def IsUsfulMask(self, maskType, coordinatesList, ratioPass=0.5, size=None):
        """Check mask array usable.

        Import mask array from LoadMask Method.
        Calculate ratio of (average of mask value / 255) and check this over ratioPass or not.

        Parameters
        ----------
        maskType : String
            Mask type ["spec", "anno"].
        coordinate : 2-D Array
            Start coordinate of patch image in slide level 0.
        ratioPass : Float, default: 0.5
            Passing score ratio.
        size : 2-D Array, default: None
            Import mask size. Actually default parameter is self.sizePixelXY[maskType] Attribute.

        Returns
        -------
        booleanArray : 1-D Array
            True / False array about coordinatesList parameter.
        """
        boolList = []
        for coordinate in coordinatesList:
            mask = self.LoadMask(maskType, coordinate, size)
            ratioUseful = mask.mean() / 255
            if ratioUseful > ratioPass:
                boolList.append(True)
            else:
                boolList.append(False)

        return array(boolList)

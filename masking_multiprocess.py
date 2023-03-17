import openslide, argparse, pickle, sys, os
import numpy as np

from multiprocessing import Pool
from modules import *


def MakeFolderTree(filePath, last=-1):
    accuPath = "/"
    for subPath in filePath.split('/')[:last]:
        accuPath = os.path.join(accuPath, subPath)
        if bool(subPath) and not os.path.isdir(accuPath):
            os.system("mkdir %s"%accuPath)
    return None

def MaskingProcess(parameterDic):
    wsiID = parameterDic["wsiID"]
    pathWSI = parameterDic["pathWSI"]
    downsample = parameterDic["downsample"]
    optionSpec = parameterDic["optionSpec"]
    coordinates = parameterDic["coordinates"]
    pathRootSave = parameterDic["pathRootSave"]
    del parameterDic
    print(wsiID)

    # Declare Save Path
    pathMaskSpec = os.path.join(pathRootSave, "spec/mask/%s.tif"%wsiID)
    pathDumpSpec = os.path.join(pathRootSave, "spec/dump/%s.dump"%wsiID)
    pathPreVSpec = os.path.join(pathRootSave, "spec/preview/%s.png"%wsiID)
    pathMaskAnno = os.path.join(pathRootSave, "anno/mask/%s.tif"%wsiID)
    pathDumpAnno = os.path.join(pathRootSave, "anno/dump/%s.dump"%wsiID)
    pathPreVAnno = os.path.join(pathRootSave, "anno/preview/%s.png"%wsiID)
    MakeFolderTree(pathMaskSpec)
    MakeFolderTree(pathDumpSpec)
    MakeFolderTree(pathPreVSpec)
    MakeFolderTree(pathMaskAnno)
    MakeFolderTree(pathDumpAnno)
    MakeFolderTree(pathPreVAnno)

    # Prepare Parameters
    handleWSI = openslide.OpenSlide(pathWSI)
    boundsDic = GetBoundsDic(handleWSI.properties)
    level = np.log10(downsample/np.array(handleWSI.level_downsamples)).__abs__().argmin()
    downsampleApt = handleWSI.level_downsamples[level]
    w = np.round(boundsDic['w'] / downsampleApt).astype(int)
    h = np.round(boundsDic['h'] / downsampleApt).astype(int)

    # Make Mask
    img = np.array(handleWSI.read_region((boundsDic['x'], boundsDic['y']), level, (w, h)).convert("RGB"))
    hsvlDic = CvtHSVLDic(img)
    rangeSelectList = optionSpec["rangeSelectList"]
    gauthSelect = optionSpec["gauthSelect"]
    maskSpec = RegionMasking(hsvlDic, rangeSelectList, gauthSelect)
    maskAnno = CorrdinateMasking(img.shape[:2], downsampleApt, coordinates)

    # Export and Record
    ShowOverlapMask(img, maskSpec, 1/4, pathSave=pathPreVSpec)
    ShowOverlapMask(img, maskAnno, 1/4, pathSave=pathPreVAnno)
    SaveMaskBigtiff(pathMaskSpec, maskSpec)
    SaveMaskBigtiff(pathMaskAnno, maskAnno)
    pickle.dump(optionSpec, open(pathDumpSpec, "wb"))
    pickle.dump(coordinates, open(pathDumpAnno, "wb"))
    return None

def main():
    parser = argparse.ArgumentParser(description="Preprocess multi threading code.")
    parser.add_argument("--tsv", type=str, help="parameters recorded tsv text file path.")
    args = parser.parse_args()

    variables = dict(np.loadtxt(args.tsv, dtype=str, delimiter="\t"))
    pathRootSave = variables["pathRootSave"]
    optionSpec = variables["optionSpec"]
    downsample = variables["downsample"]
    numProcess = variables["numProcess"]
    del variables, args

    cur = LoginWSIViewer()
    wsiInfos = GetWSIInfos(cur, "wsiluadinfo")

    optionSpec = pickle.load(open(optionSpec, "rb"))

    poolVariables = []
    for wsiID in wsiInfos.keys():
        parameterDic = {}
        parameterDic["wsiID"] = wsiID
        parameterDic["pathWSI"] = wsiInfos[wsiID]["filepath"]
        parameterDic["downsample"] = 12
        parameterDic["optionSpec"] = optionSpec
        parameterDic["coordinates"] = wsiInfos[wsiID]["corrdihuman"]["coordinates"]
        parameterDic["pathRootSave"] = pathRootSave
        poolVariables.append(parameterDic)

    with Pool(4) as p:
        p.map(MaskingProcess, poolVariables)
    return None

if __name__ == "__main__":
    main()

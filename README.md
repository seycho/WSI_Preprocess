# Whole Slide Image (WSI) Preprocessing Module
   

Extract Data From Mysql Database
===========
To easily load data from database, Make database load module by using pymysql package.   
It also return organized WSI informations as python dictionary.   
   
Make Region Mask Array And Export
===========
Calculate color ranged region at Hue, Saturation, Value, Laplacian chennels.   
Make intersection region for each chennel, Also it can consider multiple color range set.   
Final mask array is union of mask arrays which calculated own color range set.   
   
[To Do 1]   
   
For easy to see color range selecter's performance,   
There are show image and plot color histogram function in preview.py   
   
WSI Patch Image Importer
===========
WSI data have much of properties and parameters. Also their image load modules required slide level 0's coordinates.   
Each WSIs sometimes have different micron per pixels (mpp), It needs resizing process to fit same absolute size.   
For these reasion not to easy to see and use slide image's data.   
   
WSI importer class have micron to pixel converter.   
Input datas are must have micron values and resizing pixel value.   
Process find apt import slide level to optimizing extract process.   
   
[To Do 2]   
   
After that, Set default pixel size of WSI and each mask,   
For when user can get patch image and mask even just input coordinates value.   
   
Importer class also can determine some patch image is usable or not by referencing same located mask.   
   
[To Do 3]   
   
To Do
===========
1. Draw algorithm and image of image masking preprocessing.
2. Write apt import slide level finder formula.
3. Make reference image of load process.
   
Also prepare and upload reference WSI image link and annotation coordinates.

$Level_{apt} = \frac{Pixel Size_{patch}} / {y}$

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
   
![image](./readme_image/algo.png)   
   
For easy to see color range selecter's performance,   
There are show image and plot color histogram function in preview.py   
   
![image](./readme_image/range_selecter_0.png)   
   
![image](./readme_image/range_selecter_1.png)   
   
WSI get from https://portal.gdc.cancer.gov/cases/595fc3ad-f603-421b-b130-52f1f617050b.   
   
WSI Patch Image Importer
===========
WSI data have much of properties and parameters. Also their image load modules required slide level 0's coordinates.   
Each WSIs sometimes have different micron per pixels (mpp), It needs resizing process to fit same absolute size.   
For these reasion not to easy to see and use slide image's data.   
   
WSI importer class have micron to pixel converter.   
Input datas are must have micron values and resizing pixel value.   
Process find apt import slide level to optimizing extract process.   
   
$f_{L} = \Big| log\left(\frac{S_{L}}{2\times S_{R}}\right) \Big| $   
Each level ratio factors $f_{L}$ are defined this equation.   
$S_{L}$ is patch pixel size at each level, $S_{R}$ is resizing pixel size.   
Apt import slide level is decided which have minimum of $f_{L}$.
   
After that, Set default pixel size of WSI and each mask,   
For when user can get patch image and mask even just input coordinates value.   
   
Importer class also can determine some patch image is usable or not by referencing same located mask.   
   
To Do
===========
Make multiple masking process with multiprocessing.   
   
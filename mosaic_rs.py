from osgeo import gdal
import os
import glob
import math
def GetExtent(in_fn):
    ds=gdal.Open(in_fn)
    geotrans=list(ds.GetGeoTransform())
    xsize=ds.RasterXSize
    ysize=ds.RasterYSize
    min_x=geotrans[0]
    max_y=geotrans[3]
    max_x=geotrans[0]+xsize*geotrans[1]
    min_y=geotrans[3]+ysize*geotrans[5]
    ds=None
    return min_x,max_y,max_x,min_y
outname='S2.tif'
path=r"D:\S2"
os.chdir(path)
in_files=glob.glob("*.tif")
in_fn=in_files[0]
min_x,max_y,max_x,min_y=GetExtent(in_fn)
for in_fn in in_files[1:]:
    minx,maxy,maxx,miny=GetExtent(in_fn)
    min_x=min(min_x,minx)
    min_y=min(min_y,miny)
    max_x=max(max_x,maxx)
    max_y=max(max_y,maxy)
in_ds=gdal.Open(in_files[0])
im_bands=4 #bands count
geotrans=list(in_ds.GetGeoTransform())
width=geotrans[1]
height=geotrans[5]
columns=math.ceil((max_x-min_x)/width)
rows=math.ceil((max_y-min_y)/(-height))
in_band=in_ds.GetRasterBand(1)
driver=gdal.GetDriverByName('GTiff')
out_ds=driver.Create(outname,columns,rows,im_bands,in_band.DataType)
out_ds.SetProjection(in_ds.GetProjection())
geotrans[0]=min_x
geotrans[3]=max_y
out_ds.SetGeoTransform(geotrans)
inv_geotrans=gdal.InvGeoTransform(geotrans)
for in_fn in in_files:
    in_ds=gdal.Open(in_fn)
    in_gt=in_ds.GetGeoTransform()
    offset=gdal.ApplyGeoTransform(inv_geotrans,in_gt[0],in_gt[3])
    x,y=map(int,offset)
    print(x,y)
    trans=gdal.Transformer(in_ds,out_ds,[])
    success,xyz=trans.TransformPoint(False,0,0)
    x,y,z=map(int,xyz)
    print(x,y,z)
    for i in range(im_bands):
        print(i)
        data = in_ds.GetRasterBand(i + 1).ReadAsArray()
        out_ds.GetRasterBand(i + 1).WriteArray(data,x,y)

del in_ds,out_ds

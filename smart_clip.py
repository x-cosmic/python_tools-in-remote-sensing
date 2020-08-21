import gdal
import ogr
import fnmatch
import os
import sys
num=0
imagepath="T:/daqinghe18data/"
ptShp="T:/dqhshp/dapall.shp"
dirs_box = r"T:/daqinghe18data"
outpath="T:/dqh0018/"
box_list = fnmatch.filter(os.listdir(dirs_box), '*.tif')
num1 = 0


def write_img(filename, im_proj, im_geotrans, im_data):

    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
    if len(im_data.shape) == 3:  # len(im_data.shape)表示矩阵的维数
        im_bands, im_height, im_width = im_data.shape  # （维数，行数，列数）
    else:
        im_bands, (im_height, im_width) = 1, im_data.shape  # 一维矩阵

    #         创建文件
    driver = gdal.GetDriverByName('GTiff')  # 数据类型必须有，因为要计算需要多大内存空间
    data = driver.Create(filename, im_width, im_height, im_bands, datatype)
    data.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
    data.SetProjection(im_proj)  # 写入投影
    if im_bands == 1:
        data.GetRasterBand(1).WriteArray(im_data)  # 写入数组数据
    else:
        for i in range(im_bands):
            data.GetRasterBand(i + 1).WriteArray(im_data[i])
    del data

def cliping(fname,img_file,shp_file):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataset = gdal.Open(img_file)
    im_geotrans = dataset.GetGeoTransform()
    im_proj = dataset.GetProjection()
    ds = ogr.Open(shp_file, 0)  # 以只读方式打开矢量文件
    if ds == None:
        print("open shapefile false")
        sys.exit(1)
    layer = ds.GetLayer()
    feature = layer.GetNextFeature()
    count=0
    while feature:
        # 获取要素几何
        count+=1
        geom = feature.GetGeometryRef()
        geoX = geom.GetX() # 读取xy坐标,转为字符串，方便TXT写入
        geoY = geom.GetY()
        g0=float(im_geotrans[0])
        g1 = float(im_geotrans[1])
        g2 = float(im_geotrans[2])
        g3 = float(im_geotrans[3])
        g4 = float(im_geotrans[4])
        g5 = float(im_geotrans[5])
        x=((geoY-g3)*g2-(geoX-g0)*g5)/(g2*g4-g1*g5)
        y=(geoY-g3-g4*geoX)/g5
        x=int(x)
        y=int(y)
        im_data = dataset.ReadAsArray(x-500, y-500, x+500, y+500)
        im_geot=im_geotrans
        geox2=g0+g1*(x-500)+g2*(y-500)
        geoy2=g3+g4*(x-500)+g5*(y-500)
        im_geot[0]=str(geox2)

        im_geot[3] = str(geoy2)
        strname=fname+'_'+str(count)+'.tif'
        write_img(strname,im_proj,im_geot,im_data)
        feature.Destroy()
        feature = layer.GetNextFeature()
    # 清除DataSource缓存并关闭TXT文件
    ds.Destroy()


for box in box_list:
    (shpname, extension) = os.path.splitext(box)
    image = imagepath + shpname + ".tif"
    print(image, ptShp)
    fname=outpath+'dqh'+str(num1)
    cliping(fname,image,ptShp)


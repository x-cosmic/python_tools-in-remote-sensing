import gdal
import ogr
import fnmatch
import os
import sys



imagepath="T:/daqinghe19data/"
ptShp="D:/YOLO/data_pre/shptrain/shpt.shp"
outpath="D:/YOLO/data_pre/fortrain800/"
box_list = fnmatch.filter(os.listdir(imagepath), '*.tif')
datasize=800
adatasize=int(datasize/2)

num1 = 0


def write_img(filename, im_proj, im_geotrans, im_data):


    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
       
    if len(im_data.shape) == 3:  
        im_bands, im_height, im_width = im_data.shape  
    else:
        im_bands, (im_height, im_width) = 1, im_data.shape 


    im_bands=3
    driver = gdal.GetDriverByName('GTiff')  
    data = driver.Create(filename, datasize, datasize, 3, datatype)
    data.SetGeoTransform(im_geotrans)  
    data.SetProjection(im_proj)  
    if im_bands == 1:
        data.GetRasterBand(1).WriteArray(im_data) 
    else:
        for i in range(im_bands):
            data.GetRasterBand(i + 1).WriteArray(im_data[i])
    del data

def cliping(fname,img_file,shp_file):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataset = gdal.Open(img_file)
    im_geotrans = dataset.GetGeoTransform()
    #print(im_geotrans)
    im_proj = dataset.GetProjection()
    im_width = dataset.RasterXSize 

    im_height = dataset.RasterYSize  
    print(im_width, im_height)
    ds = ogr.Open(shp_file, 0) 
    if ds == None:
        print("open shapefile false")
        sys.exit(1)
    layer = ds.GetLayer()
    feature = layer.GetNextFeature()
    count=0

    while feature:

        geom = feature.GetGeometryRef()
        geoX = geom.GetX() 
        geoY = geom.GetY()
        g0=float(im_geotrans[0])
        g1 = float(im_geotrans[1])
        g2 = float(im_geotrans[2])
        g3 = float(im_geotrans[3])
        g4 = float(im_geotrans[4])
        g5 = float(im_geotrans[5])
        #x=((geoY-g3)*g2-(geoX-g0)*g5)/(g2*g4-g1*g5)
        #y=(geoY-g3-g4*geoX)/g5
        x=(geoX-g0)/g1
        y = (geoY - g3 ) / g5
        #print(geoX)
       # print(g0)
        x=int(x)
        y=int(y)
        a1=x-adatasize
        a2=y-adatasize
        a3=x+adatasize
        a4=y+adatasize
        #print(a3,im_width)
        #print(a4,im_height)

        if a1>=0 and a2>=0 and a3>0 and a4>0 and a3<=im_width and a4<=im_height:
            count += 1
            geox2 = g0 + g1 * (a1) + g2 * (a2)
            geoy2 = g3 + g4 * (a1) + g5 * (a2)
            im_data = dataset.ReadAsArray(a1, a2, datasize, datasize)
            im_geot= list(im_geotrans)
            im_geot[0] = geox2
            im_geot[3] = geoy2
            strname = fname + '_' + str(count) + '.tif'
            write_img(strname, im_proj, im_geot, im_data)
            print("right!")

        feature.Destroy()
        feature = layer.GetNextFeature()
 

    ds.Destroy()


for box in box_list:
    (shpname, extension) = os.path.splitext(box)
    image = imagepath + shpname + ".tif"
    num1+=1

    fname=outpath+'dqh'+str(num1)
    print(image, ptShp,fname)
    cliping(fname,image,ptShp)


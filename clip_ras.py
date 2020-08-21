import gdal
import numpy as np
import fnmatch
import os

img_path="T:/earthquake/jzg18"
clip_path="T:/earthquake/jzgall"
leixing="jzg"
count=1
dsize=20000
gdal.AllRegister()
def write_img(filename, im_proj, im_geotrans, im_data):
    if 'uint8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands, (im_height, im_width) = 1, im_data.shape
    driver = gdal.GetDriverByName('GTiff')
    data = driver.Create(filename, im_width, im_height, im_bands, datatype)
    data.SetGeoTransform(im_geotrans)
    data.SetProjection(im_proj)
    if im_bands == 1:
        data.GetRasterBand(1).WriteArray(im_data)
    else:
        for i in range(im_bands):
            data.GetRasterBand(i + 1).WriteArray(im_data[i])
    del data
img_list = fnmatch.filter(os.listdir(img_path), '*.tif')


if not os.path.exists(clip_path):
    os.mkdir(clip_path)
for img in img_list:
    print(img)
    p_img=img_path+'/'+img
    dataset = gdal.Open(p_img)
    im_geotrans = dataset.GetGeoTransform()
    im_proj = dataset.GetProjection()
    lie = dataset.RasterXSize
    hang = dataset.RasterYSize
    rsize1 = dsize
    rsize2 = dsize
    mi = int(hang / rsize1) + 1
    mj = int(lie / rsize2) + 1
    for ni in range(0, mi):
        for nj in range(0, mj):
            print(count)
            out_name=clip_path+'/'+leixing+"_"+str(count)+".tif"
            k = rsize2 * nj
            m = rsize1 * ni
            k1 = dsize
            m1 = dsize
            if (k+k1<lie and m+m1 <hang):
                count += 1
                timg = dataset.ReadAsArray(k, m, k1, m1)
            else:
                if k+k1>=lie:
                    k1=lie-k
                if m+m1>=hang:
                    m1=hang-m
                count += 1

                timg0 = dataset.ReadAsArray(k, m, k1, m1)
                typea = timg0.dtype
                timg = np.zeros((3, dsize, dsize),dtype = typea)
                timg[:,0:m1,0:k1]=timg0[:,0:m1,0:k1]
            geot = list(im_geotrans)
            geot[0] = im_geotrans[0] + k * im_geotrans[1] + m * im_geotrans[2]
            geot[3] = im_geotrans[3] + k * im_geotrans[4] + m * im_geotrans[5]
            write_img(out_name, im_proj, geot, timg)

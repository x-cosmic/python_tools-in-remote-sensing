import numpy as np
import gdal
from skimage.filters import threshold_otsu
from skimage.morphology import square, white_tophat
from skimage.transform import rotate
import os
import fnmatch
#  读取tif数据集
def readTif(fileName, xoff = 0, yoff = 0, data_width = 0, data_height = 0):
    dataset = gdal.Open(fileName)
    if dataset == None:
        print(fileName + "文件无法打开")
    #  栅格矩阵的列数
    width = dataset.RasterXSize
    #  栅格矩阵的行数
    height = dataset.RasterYSize
    #  波段数
    bands = dataset.RasterCount
    #  获取数据
    if(data_width == 0 and data_height == 0):
        data_width = width
        data_height = height
    data = dataset.ReadAsArray(xoff, yoff, data_width, data_height)
    #  获取仿射矩阵信息
    geotrans = dataset.GetGeoTransform()
    #  获取投影信息
    proj = dataset.GetProjection()
    return width, height, bands, data, geotrans, proj

#  保存tif文件函数
def writeTiff(im_data, im_geotrans, im_proj, path):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    elif len(im_data.shape) == 2:
        im_data = np.array([im_data])
        im_bands, im_height, im_width = im_data.shape

    #创建文件
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path, int(im_width), int(im_height), int(im_bands), datatype)
    if(dataset!= None):
        dataset.SetGeoTransform(im_geotrans) #写入仿射变换参数
        dataset.SetProjection(im_proj) #写入投影
    for i in range(im_bands):
        dataset.GetRasterBand(i+1).WriteArray(im_data[i])
    del dataset




#  计算MBI
#  s_min: 结构元素大小最小值
#  s_max: 结构元素大小最大值
#  delta_s: 颗粒测定的间隔
def CalculationMBI(filePath, MBIPath, s_min, s_max, delta_s):
    #  读取图像的相关信息
    width, height, bands, image, geotrans, proj = readTif(filePath)
    #  多光谱带的最大值对应于具有高反射率的特征->取光谱带最大值作为后续计算数据
    gray = np.max(image, 0)
    #  为消除白帽边缘效应，进行边缘补零
    gray = np.pad(gray, ((s_min, s_min), (s_min, s_min)), 'constant', constant_values=(0, 0))
    #  形态学剖面集合
    MP_MBI_list = []
    #  差分形态学剖面DMP集合
    DMP_MBI_list = []

    #  计算形态学剖面
    for i in range(s_min, s_max + 1, 2 * delta_s):
        print("s = ", i)
        #  大小为i×i的单位矩阵
        SE_intermediate = square(i)
        #  只保留中间一行为1,其他设置为0
        SE_intermediate[: int((i - 1) / 2), :] = 0
        SE_intermediate[int(((i - 1) / 2) + 1):, :] = 0

        #  SE_intermediate表示结构元素，用于设定局部区域的形状和大小
        #  旋转0 45 90 135°
        for angle in range(0, 180, 45):
            SE_intermediate = rotate(SE_intermediate, angle, order=0, preserve_range=True).astype('uint8')
            #  多角度形态学白帽重构
            MP_MBI = white_tophat(gray, selem=SE_intermediate)
            MP_MBI_list.append(MP_MBI)

    #  计算差分形态学剖面DMP
    for j in range(4, len(MP_MBI_list), 1):
        #  差的绝对值
        DMP_MBI = np.absolute(MP_MBI_list[j] - MP_MBI_list[j - 4])
        DMP_MBI_list.append(DMP_MBI)

    #  计算MBI
    MBI = np.sum(DMP_MBI_list, axis=0) / (4 * (((s_max - s_min) / delta_s) + 1))
    #  去除多余边缘结果
    MBI = MBI[s_min: MBI.shape[0] - s_min, s_min: MBI.shape[1] - s_min]
    #  写入文件
    writeTiff(MBI, geotrans, proj, MBIPath)

def BuildingExtraction_otsu(MBIPath, buildingPath):
    width, height, bands, image, geotrans, proj = readTif(MBIPath)
    thresh = threshold_otsu(image) #返回一个阈值
    image[image>thresh] = 255
    image[image<=thresh] = 0
    image = image.astype(np.uint8)
    writeTiff(image, geotrans, proj, buildingPath)


input_path = 'D:/DinkNetRS/dataset/up/testimgup'
output_path = 'D:/DinkNetRS/dataset/up/testimgup_m'
output_path2 = 'D:/DinkNetRS/dataset/up/testimgup_mbi'
inputfile = fnmatch.filter(os.listdir(input_path), '*.tif')
if not os.path.exists(output_path):
    os.mkdir(output_path)
if not os.path.exists(output_path2):
    os.mkdir(output_path2)

for file in inputfile:
    input_tif = os.path.join(input_path, file)
    output_tif = os.path.join(output_path, file)
    output_tif2 = os.path.join(output_path2, file)
    #  结构元素大小最小值
    s_min = 3
    #  结构元素大小最大值
    s_max = 20
    #  测定的间隔
    delta_s = 1
    #  计算MBI
    CalculationMBI(input_tif, output_tif, s_min, s_max, delta_s)
    #  otsu自动计算阈值提取建筑物
    BuildingExtraction_otsu(output_tif, output_tif2)




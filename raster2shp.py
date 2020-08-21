import gdal
import ogr
import osr
import fnmatch
import os
ogr.RegisterAll()
img_path="D:/image"
shape_path="D:/shp"
if not os.path.exists(shape_path):
    os.mkdir(shape_path)
img_list = fnmatch.filter(os.listdir(img_path), '*.tif')
for img in img_list:
    p_img=img_path+'/'+img
    outfilename = shape_path+'/'+img[:-4]+".shp"
    dataset = gdal.Open(p_img)
    oDriver = ogr.GetDriverByName('ESRI Shapefile')
    oDS = oDriver.CreateDataSource(outfilename)
    srs = osr.SpatialReference(wkt=dataset.GetProjection())
    geocd = dataset.GetGeoTransform()
    oLayer = oDS.CreateLayer("polygon", srs, ogr.wkbPolygon)
    oDefn = oLayer.GetLayerDefn()
    lie = dataset.RasterXSize
    hang = dataset.RasterYSize
    geoxmin = geocd[0]
    geoymin = geocd[3]
    geoxmax = geocd[0] + (lie) * geocd[1] + (hang) * geocd[2]
    geoymax = geocd[3] + (lie) * geocd[4] + (hang) * geocd[5]
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(geoxmin, geoymin)
    ring.AddPoint(geoxmax, geoymin)
    ring.AddPoint(geoxmax, geoymax)
    ring.AddPoint(geoxmin, geoymax)
    ring.CloseRings()
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    outfeat = ogr.Feature(oDefn)
    outfeat.SetGeometry(poly)
    oLayer.CreateFeature(outfeat)
    outfeat = None
    oDS.Destroy()




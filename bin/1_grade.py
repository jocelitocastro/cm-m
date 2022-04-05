#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Created by Jocelito B. C. da Cruz
jocelitocastro@gmail.com
Started in: 2020/06/05

__version__: 0.1
Date: 2021/06/25
'''

import os, sys
import geopandas as gpd
from shapely.geometry import Polygon, box
import numpy as np
from pyproj import CRS
import submodules as sm
crs_project = CRS.from_epsg(sm.EPSG)

def main(xmin, xmax, ymin, ymax, res_y, res_x, raster_dem):

    project_name = sm.project_name()
    output_path = os.path.join(sm.path_project, "Database", "Maps", "Vector")

    # convert sys.argv to float
    xmin = float(xmin)
    xmax = float(xmax)
    ymin = float(ymin)
    ymax = float(ymax)
    res_x = float(res_x)
    res_y = float(res_y)
    
    cols = np.arange(xmin, xmax, res_x)
    num_columns = len(cols)
    rows = np.arange(ymin, ymax+res_y, res_y)[::-1]

    '''
    Creates the graticulate (fishnet)
    '''
    polygons = []
    for x in cols:
        for y in rows:
            polygons.append(box(x, y, x+res_x, y+res_y, ccw=False))
    
    grid = gpd.GeoDataFrame({'geometry': polygons})
    grid.crs = crs_project
    grid.to_crs('+proj=cea').centroid.to_crs(grid.crs)
    grid_centroids = grid.to_crs('+proj=cea').centroid.to_crs(grid.crs)
    grid['lat'] = grid_centroids.geometry.y.round(3)
    lat_max = np.abs(grid.lat.min())
    grid['lon'] = grid_centroids.geometry.x.round(3)
    lon_max = np.abs(grid.lon.min())
    raster_file = os.path.join(sm.path_project, "Database", "Maps", "Raster", "Dem", raster_dem)
    grid = sm.main_zonal_stats(grid, raster_file, 'elevation', 2)

    #To create the index based on lat and lon
    grid['grid_id'] = ((grid['lat'].astype(float) + lat_max)/res_y*num_columns + \
                           (grid['lon'].astype(float) + lon_max)/res_x+1).round(0)
    grid['gridcel'] = grid['lat'].round(3).astype(str) + grid['lon'].round(3).astype(str) + \
                      "+" + grid['elevation'].round(1).astype(str) + "m"

    sm.saving_shape(grid, 'graticulate', output_path, project_name)

    
if __name__ == "__main__":
   if len( sys.argv ) != 8:
       print("[ ERROR ] must input 6 arguments: xmin xmax ymin ymax res_y res_x raster_dem_file_name.tif")
       sys.exit( 1 )

   main( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7] )
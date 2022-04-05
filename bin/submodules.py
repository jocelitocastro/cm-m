#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 21:57:58 2020

@author: Jocelito Cruz
"""

import os, re, glob
import geopandas as gpd
import pandas as pd
from rasterstats import zonal_stats
import platform
import pyproj
import yaml # to open and save crop information


#### PARAMETERS ####

# Defining the projection to the project
EPSG = 4326  # WGS84

# Defining CRS to extract soilgrids maps
crs = "http://www.opengis.net/def/crs/EPSG/0/152160"

# Defining Homolosine projection
crs_homolosine = pyproj.CRS("""PROJCS["Homolosine", 
    GEOGCS["WGS 84", 
        DATUM["WGS_1984", 
            SPHEROID["WGS 84",6378137,298.257223563, 
                AUTHORITY["EPSG","7030"]], 
   AUTHORITY["EPSG","6326"]], 
        PRIMEM["Greenwich",0, 
            AUTHORITY["EPSG","8901"]], 
        UNIT["degree",0.0174532925199433, 
            AUTHORITY["EPSG","9122"]], 
        AUTHORITY["EPSG","4326"]], 
    PROJECTION["Interrupted_Goode_Homolosine"], 
    UNIT["Meter",1]]""")

# Resolução final das imagens do soilgrids (em graus)
soilgrids_res = 0.0024699875253998624

#### END OF PARAMETERS ####

path_project = os.path.dirname(os.getcwd())

def project_name():
    if platform.system() != 'Linux':
        return path_project.split('\\')[-1]
    else:
        return path_project.split('/')[-1]


def main_zonal_stats(grid, rasterfile, variavel, arredondamento):
    stats = zonal_stats(grid, rasterfile, all_touched=True, stats="mean")
    df = gpd.GeoDataFrame.from_dict(stats).round(arredondamento)
    df.rename(columns={'mean': variavel}, inplace=True)
    pointInPolys = pd.merge(grid, df, how='left', left_index=True, right_index=True)
    return pointInPolys


def saving_shape(geodf, tipo, output_path, filename):
    # Função para salvar o arquivo no formato shapefile
    geodf.to_file(os.path.join(output_path, "{0}_{1}.shp".format(filename, tipo)))


def extract_graticulate_bounds(shapefile):
    bounds = gpd.read_file(shapefile).to_crs(crs_homolosine).bounds
    # Lower left corner
    idx_minimum = bounds.minx.idxmin()
    # bounds.minx.loc[idx_minimum]
    # bounds.miny.loc[idx_minimum]

    # Upper right corner
    idx_maximum = bounds.maxx.idxmax()
    # bounds.maxx.loc[idx_maximum]
    # bounds.maxy.loc[idx_maximum]

    return [('X', int(bounds.minx.loc[idx_minimum]), int(bounds.maxx.loc[idx_maximum])),
            ('Y', int(bounds.miny.loc[idx_minimum]), int(bounds.maxy.loc[idx_maximum]))]


def zonal_soilgrids(project_name, map_path, rasterfile):
    # print("Opening polygons shapefile")
    return zonal_stats(os.path.join(map_path, f"{project_name}_graticulate.shp"),
                       rasterfile, all_touched=True, stats="mean")


def reading_soilgrids_attributes(project_name, map_path):

    files = glob.glob(os.path.join(path_project, 'Database', 'Soil', 'soilgrids', '*tif'))
    polygons = gpd.GeoDataFrame(
        gpd.read_file(os.path.join(map_path, f"{project_name}_graticulate.shp"), geometry='geometry'))

    # Criando o padrão de expressão regular
    patternVarName = re.compile(r"4326_([A-Za-z0-9]*)_([0-9-a-z_]*)cm")

    conversao_soil_grids = {'bdod': 0.01, 'phh2o': 0.1, 'cec': 0.1,
                            'sand': 0.1, 'soc': 0.01, 'clay': 0.1}

    depths = {"0-5": 0, "5-15": 1, "15-30": 2, "30-60": 3, "60-100": 4, "100-200": 5}

    for n, file in enumerate(files):
        # print(n, file)
        reMatchVar = re.search(patternVarName, file)
        select_depth = reMatchVar.group(2).split("cm")[0]
        # print(select_depth)
        variavel = reMatchVar.group(1)
        # print(variavel)

        var_header = f"{variavel}_{depths[select_depth]}"
        print(f"Extracting: {variavel}_{select_depth}cm")

        polygons[var_header] = 0.
        stats_return = zonal_soilgrids(project_name, map_path, file)
        for i, value in enumerate(stats_return):
            converted_value = value['mean'] * conversao_soil_grids[variavel]
            # print(i, converted_value)
            # print(value['mean'], variavel, conversao_soil_grids[variavel], value['mean'] * conversao_soil_grids[variavel])
            polygons.loc[i, var_header] = converted_value
    return polygons


def openYamlFile(file_name):
    with open(file_name, 'r') as f:
        output_vars = yaml.safe_load(f)
    return output_vars

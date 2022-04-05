#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 17:23:02 2020

Created by Jocelito B. C. da Cruz
jocelitocastro@gmail.com
"""

__version__: 0.1

import numpy as np
import geopandas as gpd
import os, sys, time
from configparser import ConfigParser
import submodules as sm
from collections import deque

########## DEFINITIONS ##########----------##########----------##########----------
# Don't change these paths
project_name = sm.project_name()
database_path = os.path.join(sm.path_project, "Database")
###### END OF DEFINITIONS ########----------##########----------##########----------


def paramsIniFile(params):
    # instantiate
    paramParser = ConfigParser()
    for key in params.keys():
        # print(key)
        paramParser.add_section(key)    
        for param in params[key]:
            # print(param)
            # params[key][param]
            paramParser.set(key, param, str(params[key][param]))
    return paramParser


def textFile(dic, f, i=1, header=0):
    """
    This function reads the dictionary with rotation parameters and creates the 
    ".rot, .crp and .CropSyst_scenario" files for all crops, rotations and scenarios parameters.
    """
    
    if (header!= 0):
        #This is applied to the cropUpdate function insert in the inherit line.
        f.write(header)
        
    for ea in (sorted(dic, reverse=True)):
        if (ea != "sowing"):
            f.write("\n[{0}]\n".format(ea))
        else:
            f.write("\n[{0}:{1}]\n".format(ea, i))
        for ea2 in dic[ea]:
            if ea2 != "sowing":
                f.write("{0}={1}\n".format(ea2, dic[ea][ea2]))
            else:
                f.write("sowing:{0}\n".format(dic[ea][ea2]))


def criarDiretorio(saida):
    if not os.path.exists(saida):
        os.makedirs(saida)


def scenariosFileCreation(parametros):
    centroide, doy = parametros
    # diretorio = os.path.join(sm.path_project, "Scenarios", centroide, f'{doy:03d}')
    standardParser = ConfigParser()
    standardParser.read(os.path.join(database_path, "Format", "Scenario.CropSyst_scenario"), encoding='latin1')
    # standardParser.keys
    # standardParser.sections()
    standardParser.set('parameter_filenames', 'soil', str(f"^\\Database\\Soil\\{centroide}.sil"))
    standardParser.set('parameter_filenames', 'weather_database', str(f"^\\Database\\Weather\\UED\\{centroide}.UED"))
    standardParser.set('scenario', 'description', str(f"{centroide}_{doy:03d}"))
    return standardParser


def rotationLocalCreation(parametros):

    centroide, csParams, yearsRotation, doys = parametros

    for doy in doys:
        # doy = 105
        print(doy)
        csParams['rotation']['rotation']['description'] = f"{centroide}_doy={doy}"
        crop_rotation = csParams['rotation'].copy()

        diretorio = os.path.join(sm.path_project, "Scenarios", centroide, f'{doy:03d}')
        criarDiretorio(diretorio)
        
        with open(os.path.join(diretorio, "rotation.rot"), "w") as f:
                textFile(crop_rotation, f)

        rotation_sowing = deque()

        sow_count = 0
        for year in yearsRotation:

            csParams["sowing"]["sowing"]["ID"] = year
            eventDOY = f"{year}{doy:03d}"
            csParams["sowing"]["sowing"]["event_date"] = eventDOY
            csParams["sowing"]["sowing"]["date"] = eventDOY

            rotation_sowing.append(csParams['sowing'])

            with open(os.path.join(diretorio, "rotation.rot"), "a+") as f:
                sow_count += 1
                textFile(rotation_sowing.popleft(), f, sow_count)
    
        params = centroide, doy
        scenIni = scenariosFileCreation(params)

        with open(os.path.join(diretorio, "Scenario.CropSyst_scenario"), 'w') as f:
                scenIni.write(f, space_around_delimiters=False)

    print(f"Created rotation and scenarios files for centroid {centroide}")        


def main(rotation_start, rotation_end, sowing_doy_start, sowing_doy_end, sowing_interval):

    csParams = sm.openYamlFile(os.path.join(database_path, "Format", "configCS.yml"))
    yearsRotation = np.arange(int(rotation_start), int(rotation_end)+1)
    doys = np.arange(int(sowing_doy_start), (int(sowing_doy_end) + int(sowing_interval)), int(sowing_interval))

    # Graticulate file with centroids lat/lon
    centroides = gpd.read_file(os.path.join(database_path, "Maps", "Vector", f"{sm.project_name()}_graticulate.shp"))

    #%% This aims to create the simulation folders with config files
    # =============================================================================
    i = 0
    totalCentroides = len(centroides)

    for i, row in centroides.iterrows():
        centroide = row['gridcel']
        parametros = centroide, csParams, yearsRotation, doys
        print(f"Criado cenário {i} de {totalCentroides}")
        rotationLocalCreation(parametros)
        i += 1

'''
rotation_start rotation_end sowing_doy_start sowing_doy_end sowing_interval
'''
# rotation_start = 1961
# rotation_end = 2019
# sowing_doy_start = 150
# sowing_doy_end = 200
# sowing_interval = 10



if __name__ == "__main__":
   if len( sys.argv ) != 6:
       print("[ ERROR ] must input 5 arguments: rotation_start rotation_end sowing_doy_start sowing_doy_end sowing_interval")
       sys.exit( 1 )

   main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

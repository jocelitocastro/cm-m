#!/usr/bin/env python3
'''
Created by Jocelito B. C. da Cruz
jocelitocastro@gmail.com
'''

import os, sys
from owslib.wcs import WebCoverageService
from osgeo import gdal
import submodules as sm

# Partially adapted from: https://maps.isric.org/

def attributeConnectionDownload(parameterSoilGrid, subsets, project_name):
    # Parameters
    attribute = parameterSoilGrid[0] # clay, pH, sand, SOC, ...
    depth = parameterSoilGrid[1] # 0-5cm, 5-15cm
    specification = parameterSoilGrid[2] # mean

    print("Dowloading now: {0}_{1}_{2}".format(attribute, depth, specification))
    path_output = os.path.join(sm.path_project, "Database", "Soil", "soilgrids",\
                               '{0}_{1}cm_{2}_{3}.tif'.format(attribute, depth, specification, project_name))

    # Configurando conexão
    URL = "http://maps.isric.org/mapserv?map=/map"
    wcs = WebCoverageService('{0}/{1}.map'.format(URL, attribute), version='2.0.1')
    cov_id = '{0}_{1}cm_{2}'.format(attribute, depth, specification)
    variable = wcs.contents[cov_id]

    # Função para obter o arquivo do servidor SoilGrids
    response = wcs.getCoverage(
        identifier=[cov_id], 
        crs=sm.crs,
        subsets=subsets, 
        resx=250, resy=250, 
        format=variable.supportedFormats[0])
    
    # Operação para salvar o arquivo na projeção Homolosine
    with open(path_output, 'wb') as file:
        file.write(response.read())

def main():

    project_name = sm.project_name()
    graticulate_path = os.path.join(sm.path_project, "Database", "Maps", "Vector", f"{project_name}_graticulate.shp")

    # Define the subset from the generated Project Graticulate shapefile
    subsets = sm.extract_graticulate_bounds(graticulate_path)

    # Soil Attributes to be downloaded from SoilGrids server
    params = ['clay', 'bdod', 'cec', 'sand', 'soc', 'phh2o']

    # Profundidades desejadas para baixar do servidor
    profs = ['0-5', '5-15', '15-30', '30-60', '60-100', '100-200']

    # Função para extração do valor (ex.: mean, median)
    especs = ['mean']

    # Criação de lista combinando atributos, profundidade e especificação de valor
    pastasSimulacoes = [(param, prof, espec) 
                        for param in params 
                        for prof in profs
                        for espec in especs]

    # Loop para chamar a rotina de aquisição de cada mapa de atributo do solo
    for mapa in pastasSimulacoes[:]:
        print(mapa)
        attributeConnectionDownload(mapa, subsets, project_name)

        # Função para reprojetar o mapa de atributo do solo de Homolosine para o EPSG desejado
        soilgrids_path = os.path.join(sm.path_project, "Database", "Soil", "soilgrids")
        ds = gdal.Warp(os.path.join(soilgrids_path, f'{sm.EPSG}_{mapa[0]}_{mapa[1]}cm_{mapa[2]}_{project_name}.tif'),\
                       os.path.join(soilgrids_path, f'{mapa[0]}_{mapa[1]}cm_{mapa[2]}_{project_name}.tif'),\
                       dstSRS=f'EPSG:{sm.EPSG}', outputType=gdal.GDT_Int16, xRes=sm.soilgrids_res, yRes=sm.soilgrids_res)
        ds = None
        try:
            os.remove(os.path.join(soilgrids_path,f'{mapa[0]}_{mapa[1]}cm_{mapa[2]}_{project_name}.tif'))
        except:
            print('File not found : ' + os.path.join(soilgrids_path,f'{mapa[0]}_{mapa[1]}cm_{mapa[2]}_{project_name}.tif'))

    print("Files successfully downloaded!")

if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("[ ERROR ] This program needs no arguments")
        sys.exit(1)

    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 17:23:02 2020

@author: jocelito
"""
# __version__: 0.1

import sys, re, os, time
import numpy as np
import base_ptfs_module as soilhydros
import submodules as sm
import configparser


########## DEFINITIONS ##########----------##########----------##########----------

# Don't change these paths
project_name = sm.project_name()
map_path = os.path.join(sm.path_project, "Database", "Maps", "Vector")
soil_path = os.path.join(sm.path_project, "Database", "Soil")
soilgrids_path = os.path.join(soil_path, "soilgrids")
saida_atributos_solo = f"pontos_com_atributos_solo_{sm.project_name()}"

##########----------##########----------##########----------##########----------


def defineSoilFileName(df):
    lat = df[0]
    lon = df[1]
    elev = df[2]
    print(f"{lat:.2f}{lon:.2f}+{elev:.1f}m.sil")
    return f"{lat:.2f}{lon:.2f}+{elev:.1f}m.sil"

def createSoilFiles(soil_attributes, centroides):

    """
    This function aims to create the soil files to CropSyst, using the
    array created previously with soilhydros.hodnett_tomasella_2002 module
    Parameters
    ----------
    soil_attributes : using soil_attributes array
        DESCRIPTION.
    Inputs --> theta_s[0], theta_fc[1], theta_pwp[2], Ksm[3], rho_s[4], Sa[5], 
    Si[6], Cl[7], pH[8], CEC[9], OM[10]
    Returns
    -------
    None.

    """
    soilAttributesDict = {'saturation': 0, 'field_capacity': 1, 'perm_wilt_point': 2,
                          'sat_hydraul_cond': 3, 'bulk_density': 4, 'sand': 5,
                          'silt': 6, 'clay': 7, 'pH': 8, 'cation_exchange_capacity': 9,
                          'organic_matter': 10}

    file_standard = os.path.join(sm.path_project, "Database", "Format", "standard.sil")
    standardParser = configparser.ConfigParser()
    standardParser.read(file_standard, encoding='latin1')

    for row in range(soil_attributes.shape[1]):
        # print(row)
        # soilFileName = defineSoilFileName(soil_attributes[0, row, :3])
        soilFileName = f"{centroides.loc[row, 'gridcel']}.sil"
        for depthId, depth in enumerate(soilhydros.soil_layers):
            depthCS = str(depthId+1)
            for keyParam in soilAttributesDict:
                valueToUpdate = soil_attributes[depthId, row, soilAttributesDict[keyParam]+3]
                standardParser.set(keyParam, depthCS, str(valueToUpdate))

        if not os.path.exists(soil_path):
            os.makedirs(soil_path)
        # save to the final soil file format *.sil
        with open(os.path.join(soil_path, soilFileName), 'w') as f:
            standardParser.write(f, space_around_delimiters=False)


def main():

    variaveis_soil_grids = ['bdod', 'cec', 'clay', 'phh2o', 'sand', 'soc']

    # Load all soildgrids values (mean value)
    shapefile_graticulate = sm.reading_soilgrids_attributes(project_name, map_path)
    sm.saving_shape(shapefile_graticulate, "soil_attributes", map_path, project_name)

    dataSoilAttributes = np.zeros((len(soilhydros.soil_layers), len(shapefile_graticulate),
                                   len(variaveis_soil_grids)+3))

    dataSoilAttributes[:, :, 0] = shapefile_graticulate['lat']
    dataSoilAttributes[:, :, 1] = shapefile_graticulate['lon']
    dataSoilAttributes[:, :, 2] = shapefile_graticulate['elevation']


    for depthId in soilhydros.soil_layers_int.keys():
        print(depthId)
        for idx, indexVar in enumerate(variaveis_soil_grids):
            # print(idx, "indexVar: ", indexVar)
            variavel = f"{indexVar}_{depthId}"
            dataSoilAttributes[depthId, :, idx+3] = shapefile_graticulate[variavel].values

    # Salvando os atributos por pontos - formato padrão do SoilGrids
    np.save(os.path.join(soilgrids_path, f"Atributos_solos_pontos_{project_name}.npy"), dataSoilAttributes)

    # Carregando os atributos salvos - formato padrão do SoilGrids
    # dataSoilAttributes = np.load(os.path.join(soilgrids_path, "{0}.npy".format(saida_solo)))

    # Outputs --> alpha, n, theta_s, theta_r, theta_fc, theta_pwp, KsOttoni, Ks --> 8 columns
    HodnettvG = np.zeros((len(soilhydros.soil_layers), len(dataSoilAttributes[0]), 14))
    parametrosAjustados = np.zeros((len(soilhydros.soil_layers), len(dataSoilAttributes[0]), 9))

    # ========================================================================
    for depthId in soilhydros.soil_layers_int.keys():

        # Positions for dataSoilAttributes: rho_s[3], CEC[4], Cl[5], pH[6], Sa[7], OC[8]

        # Calculates the van Genuchten parameters, water contents based on Hodnett & Tomasella (2002)
        # and Ks based on Ottoni et. al (2019)
        HodnettvG[depthId, :, :3] = dataSoilAttributes[depthId, :, :3]
        parametrosAjustados[depthId, :, :2] = dataSoilAttributes[depthId, :, :2]
        # HodnettvG:
        # Outputs --> lat[0], lon[1], elev[2], theta_s[3], theta_fc[4], theta_pwp[5],
        #             Ksm[6], rho_s[7], Sa[8], Si[9], Cl[10], pH[11], CEC[12], OM[13]
        # ParametrosAjustados:
        # Outputs --> alpha[2], n[3], theta_s[4], theta_330[5], theta_pwp[6], theta_r[7], Ks[8]
        HodnettvG[depthId, :, 3:], parametrosAjustados[depthId, :, 2:] = soilhydros.hodnett_tomasella_2002(dataSoilAttributes[depthId, :, :])

        # Salvando os parâmetros por pontos em todas as profundidades
    np.save(os.path.join(soilgrids_path, f"pontos_com_atributos_solo_Hodnett_{project_name}.npy"), HodnettvG)
    np.save(os.path.join(soilgrids_path, f"parametros_solos_ajustados_{project_name}.npy"), parametrosAjustados)
    # Salvando todos os pontos na profundidade 0
    #vGAdjustedParams = np.asarray([alpha, n, theta_s, theta_330, theta_pwp, theta_r, Ksm])

    # HodnettvG = np.load(os.path.join(soilgrids_path, "{0}.npy".format(saida_atributos_solo)))
    # parametrosAjustados = np.load(os.path.join(soilgrids_path, "parametros_ajustados_{0}.npy".format(saida_atributos_solo)))

    createSoilFiles(HodnettvG, shapefile_graticulate)


if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("[ ERROR ] This program needs no arguments")
        sys.exit(1)

    main()


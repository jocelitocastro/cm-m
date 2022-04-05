# -*- coding: utf-8 -*-

'''

Modified by Jocelito Cruz from Alexandre Cândido Xavier
Support to netCDF by: Alexandre C. Xavier
Support to UED by: Roger Nelson

https://github.com/AlexandreCandidoXavier/ExemplosPython/blob/master/expor_dados_csv2.py

'''

import numpy as np
import xarray as xr
import pandas as pd
import time
import geopandas as gpd
import os
import subprocess  # to run ASCII_to_UED.exe that must be on the same folder
import submodules as sm

########## DEFINITIONS ##########----------##########----------##########----------

# Don't change these paths
project_name = sm.project_name()
map_path = os.path.join(sm.path_project, "Database", "Maps", "Vector")
weather_path = os.path.join(sm.path_project, "Database", "Weather")

##########----------##########----------##########----------##########----------


#Graticulate file with centroids lat/lon
pts = gpd.read_file(os.path.join(map_path, f"{sm.project_name()}_graticulate.shp"))

#.geometry
#pts.rename(columns={'pr_elev_el': 'elevation'}, inplace=True)

# Extracting the centroids list: lat and lon
lat = pts.lat
lon = pts.lon
elev = pts.elevation.round(1)

# variables names - available at netCDF file
var_names = ['Rs', 'u2','Tmax', 'Tmin', 'RH', 'pr', 'ETo']

# function to read the netcdf files
def rawData(var2get_xr, var_name2get):
    return var2get_xr[var_name2get].sel(longitude=xr.DataArray(lon, dims='z'),
                                          latitude=xr.DataArray(lat, dims='z'),
                                          method='nearest').values

# getting data from netCDF files
for n, var_name2get in enumerate(var_names):
    print(n, 'Reading ', var_name2get)
    var2get_xr = xr.open_mfdataset(os.path.join(weather_path, "gridded", f'{var_name2get}_*.nc'),
                                    combine='by_coords')
    
    if n == 0:
        var_ar = rawData(var2get_xr, var_name2get)
        n_lines = var_ar.shape[0]
        time = var2get_xr.time.values
    elif var_name2get != var_names[5]:
        var_ar = np.c_[var_ar, rawData(var2get_xr, var_name2get)]
    else:
        prec = rawData(var2get_xr, var_name2get)
        prec_size_var_ar = np.zeros((var_ar.shape[0], len(lon))) * np.nan
        prec_size_var_ar[:prec.shape[0], :] = prec
        var_ar = np.c_[var_ar, prec_size_var_ar]


#  saving the ASCII files
with open(os.path.join(weather_path,'pontos_ok.txt'), 'a') as textFile:
    for n, row in pts.iterrows():
        print('file #{0} from a total of {1}'.format(n+1, len(lat)))
        # name_file = f'{lat[n]:0.{res}f}{lon[n]:0.{res}f}+{elev[n]:0.1f}m'  # Here was added the elevation in the name
        name_file = row['gridcel']
        
        if ~np.isnan(var_ar[0, n]):
            textFile.write('{0:0.2f},{1:0.2f}, ok\n'.format(lat[n], lon[n])) # This adds to the pontos_ok.txt file the coordinates with created weather file
            file = var_ar[:, n::len(lon)]
            # pd.DataFrame(file, index=time, columns=var_names).to_csv(os.path.join(output, name_file), float_format='%.1f', sep='\t', index_label='Date')
            df_clima = pd.DataFrame(file, index=time, columns=var_names)
            df_clima.to_csv(os.path.join(weather_path, name_file), float_format='%.1f', sep='\t', index_label='Date')
        else:
            textFile.write('{0:0.2f},{1:0.2f}, not ok\n'.format(lat[n], lon[n])) # This adds to the pontos_ok.txt file with the missing points


os.chdir(weather_path)
subprocess.run(['ASCII_to_UED.exe'])
os.chdir(os.path.join(sm.path_project, "bin"))

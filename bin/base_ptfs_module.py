# -*- coding: utf-8 -*-
"""
Created on 2021
@author: Jocelito Cruz
email: jocelitocastro@gmail.com


"""
__version__: 0.1

import numpy as np

# Tension means water potential
potentialFc = 10  #Value must be module (positive) (hPa)
potential330 = 330  #Value must be module (positive) (hPa)
potentialPwp = 15000  #Value must be module (positive) (hPa)
'''
# 1 J/kg = 1 kPa --> Energy per unit volume is dimensionally equivalent to pressure
# 1 J/kg = 1 kPa = 10 hPa = 10.1972 cmH2O = 0.101972 mH2O
# 1 kPa = 10.1972 cm H2O = 10 hPa - You must multiply the variable
'''
kPa_to_cm = 10.197162129779
'''

'''
particleDensity = 2650.0

# Flux density for infiltration at field capacity (mm/day)
qfc = 4.0  # mm/day

soil_layers_int = {0: 0.05, 1: 0.15, 2: 0.30, 3: 0.60, 4: 1.00, 5: 2.00}
soil_layers = {0.05: '0-5', 0.15: '5-15', 0.30: '15-30', 0.60: '30-60', 1.00: '60-100', 2.00: '100-200'}

arrHodnett = np.array([[-2.2940e+00,  6.2986e+01,  8.1799e+01,  2.2733e+01],
                       [ 0.0000e+00,  0.0000e+00,  0.0000e+00, -1.6400e-01],
                       [-3.5260e+00,  0.0000e+00,  0.0000e+00,  0.0000e+00],
                       [ 0.0000e+00, -8.3300e-01,  9.9000e-02,  0.0000e+00],
                       [ 2.4400e+00, -5.2900e-01,  0.0000e+00,  0.0000e+00],
                       [ 0.0000e+00,  0.0000e+00, -3.1420e+01,  0.0000e+00],
                       [-7.6000e-02,  0.0000e+00,  1.8000e-02,  2.3500e-01],
                       [-1.1331e+01,  5.9300e-01,  4.5100e-01, -8.3100e-01],
                       [ 1.9000e-02,  0.0000e+00,  0.0000e+00,  0.0000e+00],
                       [ 0.0000e+00,  7.0000e-03,  0.0000e+00,  1.8000e-03],
                       [ 0.0000e+00, -1.4000e-02,  0.0000e+00,  0.0000e+00],
                       [ 0.0000e+00,  0.0000e+00,  5.0000e-04,  2.6000e-03]])

# This array intends to convert SoilGrids attributes to apply to Hodnett & Tomasella (2002)
# soilgridsAttributesFactor = np.asarray([1, 1, 1, 0.01, 0.1, 0.1, 0.1, 0.1, 0.01])


def vGenucthen(tension, alpha, n, theta_s, theta_r):
    """
    Returns: float
       theta --> soil water content at specific tension (m3 m-3)
    Calculates the van Genuchten parameters based on Hodnett & Tomasella (2002) DOI: 10.2136/sssaj2000.641327x
    """
    m = 1 - np.divide(1, n)

    return theta_r + np.divide((theta_s-theta_r), np.power(1+np.power(alpha*tension, n), m))


def hodnett_tomasella_2002(soilAttributesValues):
    '''
    id - point identification
    0 - lat
    1 - lon
    2 - elev
    3 - bdod
    4 - cec
    5 - clay
    6 - phh2o
    7 - sand
    8 - soc

    Hodnett_Header = ['ln_alpha', 'ln_n', 'theta_s', 'theta_r']
    Hodnett_Index = ['ai', 'Sa', 'Si', 'Cl', 'OC', 'rho_s', 'CEC', 'pH', 'Si2', 'Cl2', 'SaSi', 'SaCl']

    '''

    ai = np.ones(len(soilAttributesValues))
    Sa = soilAttributesValues[:, 7]  # Sand %
    Cl = soilAttributesValues[:, 5]  # Clay %
    Si = 100 - (Sa + Cl)  # Silt %
    OC = soilAttributesValues[:, 8]  # Organic Carbon%
    rho_s = soilAttributesValues[:, 3]  # Bulk density Mg/m3
    CEC = soilAttributesValues[:, 4]  # CEC cmolc kg-1
    pH = soilAttributesValues[:, 6]  # pH

    # Loading soil attributes to the Hodnett & Tomasella (2002) structure
    variablesHodnett = np.asarray([ai, Sa, Si, Cl, OC, rho_s, CEC, pH, Si**2, Cl**2, Sa*Si, Sa*Cl]).T

    # Apply the dot product to get the van Genuchten coefficients
    vGParams = np.divide(np.dot(variablesHodnett, arrHodnett), 100.)
    vGParams[:, [0, 1]] = np.exp(vGParams[:, [0, 1]])  #Apply exponential transformation to alpha and n

    # van Genuchten equation parameters
    # vGenucthen(tension, alpha, n, theta_s, theta_r)

    # Water contents
    alpha = vGParams[:, 0]
    n = vGParams[:, 1]
    theta_s = vGParams[:, 2]  #m3/m3
    theta_r = vGParams[:, 3]  #m3/m3
    theta_pwp = vGenucthen(potentialPwp, alpha, n, theta_s, theta_r)  #m3/m3
    theta_330 = vGenucthen(potential330, alpha, n, theta_s, theta_r)  #m3/m3
    OM = OC * 1.72  # To convert organic carbon to organic matter (%)

   # Saturated Hydraulic Conductivity - mm/day
    KsOttoni = KsOttoni2019(theta_s, theta_330)  # cm/day

    # Kscm = KsOttoni  # cm/day
    Ksm = np.divide(KsOttoni, 100.)  # m/day

    # Field capacity moisture (m3/me)
    theta_fc = theta_fc_Twarakawi_2009(theta_s, theta_r, n, KsOttoni)  #m3/m3

    # Air entry potential (Saxton (1986) DOI: 10.2136/sssaj1986.03615995005000040039x)
    bubble = airEntryPotential(theta_s)  # kPa

    vGAdjustedParams = np.asarray([alpha, n, theta_s, theta_330, theta_pwp, theta_r, Ksm])

    return (np.asarray([theta_s, theta_fc, theta_pwp, Ksm, rho_s, Sa, Si, Cl, pH, CEC, OM]).T, vGAdjustedParams.T)


def porosity(bulk_density, particle_density=particleDensity):
    """
    Parameters
    ----------
    bulk_density : float
        DESCRIPTION: Soil Bulk density in kg/m3
    particle_density : float, optional
        DESCRIPTION: Soil particle density. The default is 2650 kg/m3.
    Returns
    -------
    Soil Porosity approximately equal moisture content at saturation (m3/m3)
    """
    return 1.0-(bulk_density / particle_density)


def airEntryPotential(theta_s):
    """
    Parameters
    ----------
    theta_s : float
        Soil water content at saturation (m3/m3)
    Returns
    -------
    TYPE
        The air entry potential (cm)
        Is also called bubbling pressure of the soil
        Source: Saxton (1986) DOI: 10.2136/sssaj1986.03615995005000040039x
    """
    return 100.0 * (-0.108 + 0.341 * theta_s) #* kPa_to_cm # 10.197162129779 is to convert from kPa to cm H2O


def theta_fc_Twarakawi_2009(theta_s, theta_r, n, Ks):
    """
    Parameters
    ----------
    theta_s : TYPE
        DESCRIPTION.
    theta_r : TYPE
        DESCRIPTION.
    n : TYPE
        DESCRIPTION.
    Ks : TYPE
        DESCRIPTION.
    Source: Twarakawi et al. (2009), doi: 10.1029/2009WR007944, 2009
    Returns
    -------
    Soil moisture at field capacity - theta_fc (m3/m3)

    """
    return theta_r + (theta_s - theta_r) * n ** (0.6 * np.log10(np.divide(qfc, Ks)))


def KsOttoni2019(theta_s, theta_330):
    """
    Ottoni et. al (2019)
    Returns:
        Saturated Hydraulic Conductivity in cm/day
    """
    # return 1931 * np.power((theta_s - theta_330), 1.948)
    return 1931 * ((theta_s - theta_330)**1.948)

import numpy as np
from py_wake.site import UniformWeibullSite

# GWA4 GWC: lon = 11.60° E, lat = 54.55° N
# Condizioni generalizzate: superficie d'acqua, altezza = 100 m
# Settori centrati su 0°, 30°, ..., 330°

frequency_percent = np.array([
    3.76, 2.88, 5.34, 9.17, 8.70, 6.13,
    6.58, 11.31, 13.47, 15.15, 11.84, 5.66
])

weibull_A = np.array([
    7.51, 7.75, 10.05, 10.57, 9.94, 9.37,
    9.97, 11.45, 12.37, 11.88, 10.79, 8.33
])

weibull_k = np.array([
    2.240, 2.611, 2.447, 2.838, 2.777, 2.784,
    2.452, 3.009, 3.055, 2.579, 2.563, 2.215
])

p_wd = frequency_percent / frequency_percent.sum()

Roedsand2NystedSite = UniformWeibullSite(
    p_wd=p_wd,
    a=weibull_A,
    k=weibull_k,
    ti=0.07
)
from py_wake.wind_turbines import WindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular

u = [
    4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23, 24, 25
]

power = [
    42, 136, 276, 470, 727, 1043, 1394, 1738, 2015, 2183, 2260,
    2288, 2297, 2299, 2300, 2300, 2300, 2300, 2300, 2300, 2300, 2300
]

ct = [
    0.856, 0.851, 0.838, 0.858, 0.886, 0.861, 0.763, 0.666,
    0.592, 0.455, 0.347, 0.271, 0.221, 0.179, 0.152, 0.129,
    0.109, 0.095, 0.082, 0.073, 0.063, 0.056
]

bonus_2p3 = WindTurbine(
    name="Bonus-2.3-82.4",
    diameter=82.4,
    hub_height=69.0,
    powerCtFunction=PowerCtTabular(u, power, "kW", ct, ws_cutin=4.0, ws_cutout=25.0)
)

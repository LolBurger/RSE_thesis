from py_wake.examples.data.lillgrund import power_curve, ct_curve
from py_wake.wind_turbines import WindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular


swt_2p3_93 = WindTurbine(
    name="SWT-2.3-93-RoedsandII",
    diameter=92.6,
    hub_height=68.5,
    powerCtFunction=PowerCtTabular(
        ws=power_curve[:, 0],
        power=power_curve[:, 1],
        power_unit="kW",
        ct=ct_curve[:, 1],
        ws_cutin=4.0,
        ws_cutout=25.0
    )
)
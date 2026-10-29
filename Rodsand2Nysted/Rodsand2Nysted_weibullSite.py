import numpy as np

from py_wake.wind_turbines import WindTurbines
from farm_data.Roedsand2Nysted_site import Roedsand2NystedSite
from py_wake.deficit_models.noj import NOJ
from py_wake.superposition_models import SquaredSum

from farm_data.turbines.Nysted_turbine import bonus_2p3
from farm_data.turbines.Roedsand2_turbine import swt_2p3_93

from farm_data.geometria.nysted import wt_x as ny_wt_x, wt_y as ny_wt_y
from farm_data.geometria.roedsand2 import wt_x as ro_wt_x, wt_y as ro_wt_y

ny_x = np.asarray(ny_wt_x, dtype=float)
ny_y = np.asarray(ny_wt_y, dtype=float)
ro_x = np.asarray(ro_wt_x, dtype=float)
ro_y = np.asarray(ro_wt_y, dtype=float)

# Combine both layouts
x = np.concatenate([ro_x, ny_x])
y = np.concatenate([ro_y, ny_y])

# Assign a turbine type to each position: type 0 = Siemens (Rødsand II), type 1 = Bonus (Nysted)
type_array = np.concatenate([
    np.zeros(len(ro_x), dtype=int),
    np.ones(len(ny_x), dtype=int),
])

turbines = WindTurbines.from_WindTurbine_lst([swt_2p3_93, bonus_2p3])
site = Roedsand2NystedSite()
noj = NOJ(site,turbines,k=0.04,superpositionModel=SquaredSum())

# Simulazione del cluster completo
result = noj(x, y, type=type_array)
aep_both = result.aep()
aep_total = aep_both.sum().item()

# AEP delle sole turbine di Nysted nel cluster completo
aep_ny_with_rodsand = aep_both.isel(wt=slice(len(ro_x), None)).sum().item()

# Simulazione di Nysted da sola
# Nysted è il secondo tipo nella lista turbines: type = 1
result_ny_only = noj(ny_x, ny_y, type=1)
aep_ny_only = result_ny_only.aep().sum().item()

# Perdita di Rødsand II dovuta a Nysted
aep_loss = aep_ny_only - aep_ny_with_rodsand
aep_loss_percent = 100 * aep_loss / aep_ny_only

print(f"Total AEP both [GWh]: {aep_total:.3f}")

print("\n--- Effect of Rødsand II on Nysted ---")
print(f"AEP Nysted da sola [GWh]: {aep_ny_only:.3f}")
print(f"AEP Nysted con Rødsand II [GWh]: {aep_ny_with_rodsand:.3f}")
print(f"Perdita AEP di Nysted [GWh]: {aep_loss:.3f}")
print(f"Perdita percentuale [%]: {aep_loss_percent:.3f}")
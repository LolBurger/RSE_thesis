import matplotlib.pyplot as plt
import numpy as np

from py_wake.deficit_models.noj import NOJ
from py_wake.site import UniformSite
from py_wake.superposition_models import SquaredSum
from py_wake.wind_turbines import WindTurbines

# Import the turbine objects
from farm_data.Nysted_turbine import bonus_2p3
from farm_data.Roedsand2_turbine import swt_2p3_93

# Import turbine coordinates
from farm_data.nysted import wt_x as ny_wt_x, wt_y as ny_wt_y
from farm_data.roedsand2 import wt_x as ro_wt_x, wt_y as ro_wt_y

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
site = UniformSite(ti=0.07)

# Configure the NOJ wake model:
k = 0.04
noj = NOJ(site, turbines, k = k, superpositionModel=SquaredSum())

# Define the single flow case:
wind_direction = 278.0
wind_speed = 11.0

# Simulate both wind farms together
result = noj(x, y, type=type_array, wd=[wind_direction], ws=[wind_speed])

print(f"Nysted: {len(ny_x)} turbine")
print(f"Rodsand II: {len(ro_x)} turbine")
print(f"Totale: {len(x)} turbine")
print(f"Condizione: wd = {wind_direction:g} deg, ws = {wind_speed:g} m/s")

# Figure 1: plot the wake velocity field
flow_map = result.flow_map(wd=wind_direction,ws=wind_speed)
plt.figure(figsize=(12, 5))
flow_map.plot_wake_map()

plt.xlim(flow_map.x.min().item(), flow_map.x.max().item())
plt.ylim(flow_map.y.min().item(), flow_map.y.max().item())
plt.gca().set_aspect("equal", adjustable="box")
plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.title(f"Rødsand II + Nysted, wind from {wind_direction:g}°, "f"{wind_speed:g} m/s, NOJ, k = {k:g}")
plt.tight_layout()
plt.legend()

## Effect of Rødsand II on Nysted
# Simulate Nysted without Rødsand II
result_ny_only = noj(ny_x, ny_y,type=1,wd=[wind_direction],ws=[wind_speed])
# Select only Nysted turbines from the combined simulation.
ny_in_cluster = result.isel(wt=slice(len(ro_x), None))

risultati = [result, result_ny_only]
titoli = ["Rødsand II + Nysted", "Solo Nysted"]

fig, axes = plt.subplots(2, 1, figsize=(12, 7),sharex=True, sharey=True, layout="constrained")

for i in range(2):
    ax = axes[i]
    sim = risultati[i]

    ax.scatter(x, y, s=30, facecolors="none", edgecolors="gray")

    ws_rotor = sim.WS_eff.sel(wd=wind_direction, ws=wind_speed).values
    points = ax.scatter(sim.x.values, sim.y.values, c=ws_rotor, cmap="viridis", vmin=5, vmax=wind_speed, s=30)

    ax.set_title(titoli[i])
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.grid(alpha=0.3)

fig.colorbar(points, ax=axes, label="Velocità efficace al rotore [m/s]", shrink=0.8)
fig.suptitle(f"Vento da {wind_direction:g}°, {wind_speed:g} m/s, NOJ, k = {k:g}")

# Compare the power of the same wind farm in both configurations [MW]
power_ny_only = result_ny_only.Power.sum().item() / 1e6
power_ny_cluster = ny_in_cluster.Power.sum().item() / 1e6
power_loss = power_ny_only - power_ny_cluster
power_loss_percent = 100 * power_loss / power_ny_only

print("\n--- Effect of Rødsand II on Nysted---")
print(f"Nysted power without Rødsand II: {power_ny_only:.3f} MW")
print(f"Nysted power with Rødsand II:    {power_ny_cluster:.3f} MW")
print(f"Power loss due to Rødsand II:       {power_loss:.3f} MW")
print(f"Relative power loss:           {power_loss_percent:.2f}%")

plt.show()
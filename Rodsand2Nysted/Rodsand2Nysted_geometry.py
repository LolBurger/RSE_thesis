from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from farm_data.nysted import wt_x as ny_wt_x, wt_y as ny_wt_y
from farm_data.roedsand2 import wt_x as ro_wt_x, wt_y as ro_wt_y


script_dir = Path(__file__).resolve().parent

ny_x = np.asarray(ny_wt_x, dtype=float)
ny_y = np.asarray(ny_wt_y, dtype=float)
ro_x = np.asarray(ro_wt_x, dtype=float)
ro_y = np.asarray(ro_wt_y, dtype=float)

print("Nysted:")
print(f"  Number of turbines read: {len(ny_x)}")
print(f"  x min = {ny_x.min():.1f} m, x max = {ny_x.max():.1f} m")
print(f"  y min = {ny_y.min():.1f} m, y max = {ny_y.max():.1f} m")

print("\nRødsand II:")
print(f"  Number of turbines read: {len(ro_x)}")
print(f"  x min = {ro_x.min():.1f} m, x max = {ro_x.max():.1f} m")
print(f"  y min = {ro_y.min():.1f} m, y max = {ro_y.max():.1f} m")

plt.figure(figsize=(12, 7))

plt.scatter(ny_x, ny_y, s=30, color="tab:orange", label=f"Nysted ({len(ny_x)} turbines)")
plt.scatter(ro_x, ro_y, s=30, color="tab:blue", label=f"Rødsand II ({len(ro_x)} turbines)")

plt.axis("equal")
plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.title("Nysted and Rødsand II wind farm geometry")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

output_file = script_dir / "Nysted_RodsandII_layout.png"
plt.savefig(output_file, dpi=300)
print(f"\nFigure saved to: {output_file}")

plt.show()
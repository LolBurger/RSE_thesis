import matplotlib.pyplot as plt
import numpy as np
from py_wake.site import UniformWeibullSite
from pathlib import Path

class Roedsand2NystedSite(UniformWeibullSite):
    def __init__(self, ti=.07, shear=None):
        # global wind atlas 50 metri
        f = [3.76, 2.88, 5.34, 9.17, 8.70, 6.13,
            6.58, 11.31, 13.47, 15.15, 11.84, 5.66]
        a = [7.09, 7.34, 9.48, 9.88, 9.29, 8.63,
            9.08, 10.47, 11.38, 11.03, 10.13, 7.85]
        k = [2.407, 2.847, 2.586, 2.998, 2.997, 2.976,
            2.539, 3.092, 3.097, 2.625, 2.681, 2.351]

        UniformWeibullSite.__init__(self, np.array(f) / np.sum(f), a, k, ti=ti, shear=shear)

def main():
    site = Roedsand2NystedSite()
    site.plot_wd_distribution(n_wd=12, ws_bins=[0,5,10,15,20,25])

    plt.title(
        "Rødsand II and Nysted — Wind frequency rose\n"
        "GWA4 generalized marine climate, 50 m",
        pad=25
    )

    plt.savefig(
        Path(__file__).resolve().parent / "WindFrequencyRose_Roedsand2Nysted_GWA4_50m.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

if __name__ == '__main__':
    main()
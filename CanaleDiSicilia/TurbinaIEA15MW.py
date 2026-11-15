import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from py_wake.wind_turbines import WindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
Path_dir = Path(__file__).resolve().parent

def crea_turbina_IEA_15MW():
    file_excel = Path_dir / "data" / "iea15mw" / "IEA-15-240-RWT_tabular.xlsx"
    colonne = ["Wind [m/s]", "Power [MW]", "Thrust Coefficient [-]"]
    tabella = pd.read_excel(file_excel, sheet_name="Rotor Performance", usecols=colonne)
    # Elimino righe vuote e la nota testuale in fondo al foglio
    tabella = tabella.apply(pd.to_numeric, errors="coerce").dropna()
    # Ordino i dati per velocità crescente
    tabella = tabella.sort_values("Wind [m/s]")

    # Estraggo le tre curve
    ws = tabella["Wind [m/s]"].to_numpy()
    potenza = tabella["Power [MW]"].to_numpy()
    ct = tabella["Thrust Coefficient [-]"].to_numpy()
    
    # Creo la funzione tabulata di potenza e coefficiente di spinta
    power_ct = PowerCtTabular(ws=ws, power=potenza, power_unit="MW", ct=ct, ws_cutin=3.0, ws_cutout=25.0, method="linear")

    # Creo la turbina con le dimensioni riportate nell'Excel
    turbina = WindTurbine(name="IEA 15 MW", diameter=241.35064632, hub_height=150.0, powerCtFunction=power_ct)
    return turbina

def grafici_turbina(turbina, save=False, show=True):
    # Calcolo potenza in watt e C_T per ogni velocità per velocità da 0 a 30 m/s con passo di 0.5 m/s
    velocita = np.arange(0, 30 + 0.5, 0.5)
    potenza_W = turbina.power(velocita)
    potenza_MW = potenza_W / 1_000_000
    ct = turbina.ct(velocita)

    # Creo una figura con due grafici affiancati
    fig, (ax_potenza, ax_ct) = plt.subplots(1, 2, figsize=(12, 5))

    # Grafico della potenza
    ax_potenza.plot(velocita, potenza_MW)
    ax_potenza.set_xlabel("Velocità del vento [m/s]")
    ax_potenza.set_ylabel("Potenza [MW]")
    ax_potenza.set_title("Curva di potenza IEA 15 MW")
    ax_potenza.grid(True)

    # Grafico del coefficiente di spinta
    ax_ct.plot(velocita, ct)
    ax_ct.set_xlabel("Velocità del vento [m/s]")
    ax_ct.set_ylabel("C_T [-]")
    ax_ct.set_title("Curva di C_T IEA 15 MW")
    ax_ct.grid(True)

    fig.tight_layout()
    if save:
        fig.savefig(Path_dir / "data" / "iea15mw" / "grafici_turbina_IEA_15MW.png", dpi=200)
        print(f"Figura salvata: {Path_dir / "data" / "iea15mw" / "grafici_turbina_IEA_15MW.png"}")
    if show:
        plt.show()
    plt.close(fig)
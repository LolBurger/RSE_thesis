import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from py_wake.site import UniformWeibullSite
from matplotlib.ticker import PercentFormatter
from scipy.optimize import brentq, least_squares
from scipy.special import gammaln
from scipy.stats import weibull_min
from statsmodels.distributions.empirical_distribution import ECDF
Path_dir = Path(__file__).resolve().parent

def trova_file(tipo, id_parco):
    modello = f"{tipo}_project_{id_parco}.0_*.csv"
    cartella = Path_dir / "data" / "project_wind_data"
    trovati = list(Path(cartella).rglob(modello))

    if len(trovati) == 0:
        raise FileNotFoundError(f"Nessun file {tipo} trovato per il parco {id_parco}.")
    if len(trovati) > 1:
        raise ValueError(f"Trovati più file {tipo} per il parco {id_parco}: {trovati}")
    return trovati[0]

def leggi_serie(file, variabile):
    tabella = pd.read_csv(file)
    tabella["datetime"] = pd.to_datetime(tabella["datetime"], errors="raise")
    
    if tabella.empty or tabella["datetime"].isna().any():
        raise ValueError(f"{file.name}: file vuoto o date mancanti.")
    
    tabella = tabella.set_index("datetime").sort_index()

    if tabella.index.has_duplicates:
        raise ValueError(f"{file.name}: ci sono date e ore duplicate.")
    if not (tabella.index == tabella.index.floor("h")).all():
        raise ValueError(f"{file.name}: ci sono orari non allineati all'ora esatta.")

    serie = pd.to_numeric(tabella["speed"], errors="coerce")
    serie.name = variabile

    ore_attese = pd.date_range(start=serie.index.min(), end=serie.index.max(), freq="h")
    ore_mancanti = ore_attese.difference(serie.index)

    # Controllo la serie e sostituisco i valori invalidi con NaN
    validi = np.isfinite(serie) & (serie >= 0)
    if variabile == "wd":
        validi = validi & (serie <= 360)
        serie = serie % 360
    
    serie = serie.where(validi)

    if len(ore_mancanti) > 0 or (~validi).sum() > 0:
        print(f"\n{variabile}: {file.name}")
        print(f"Periodo: {serie.index.min()} -> {serie.index.max()}")
        print(f"Ore mancanti: {len(ore_mancanti)}")
        print(f"Valori non validi: {(~validi).sum()}")
    else:
        print(f"letto la serie in: {file.name}")
    return serie

def MetodoMomenti_weibull(velocita):
    media = float(velocita.mean())
    varianza = float(velocita.var(ddof=0))
    if len(velocita) < 2 or media <= 0 or varianza <= 0:
        return np.nan, np.nan

    rapporto = varianza / media**2
    def equazione(k):
        return gammaln(1 + 2 / k) - 2 * gammaln(1 + 1 / k) - np.log1p(rapporto)

    try: k = brentq(equazione, 0.05, 1000)
    except ValueError: return np.nan, np.nan
    
    A = media / np.exp(gammaln(1 + 1 / k))
    return A, k

def MetodoMinimiQuadrati_weibull(velocita):
    A0, k0 = MetodoMomenti_weibull(velocita)

    if not np.isfinite(A0) or not np.isfinite(k0):
        return np.nan, np.nan

    # Velocità ordinate e cumulativa empirica
    x = np.sort(velocita.to_numpy())
    ecdf = ECDF(x)
    y = ecdf(x)

    # Scarti tra cumulativa teorica ed empirica
    def scarti(parametri):
        A, k = parametri
        return weibull_min.cdf(x, k, loc=0, scale=A) - y

    risultato = least_squares(scarti, x0=[A0, k0], bounds=(1e-8, np.inf))
    if not risultato.success:
        return np.nan, np.nan

    A, k = risultato.x
    return A, k

# Crea un sito PyWake con Weibull separate per settore direzionale
def crea_site_parco(id_parco, n_settori = 12, ti = None):
    file_ws = trova_file("speed", id_parco)
    file_wd = trova_file("direction", id_parco)

    ws = leggi_serie(file_ws, "ws")
    wd = leggi_serie(file_wd, "wd")

    # Tengo solo le ore in cui esistono sia velocità sia direzione
    vento = ws.to_frame().join(wd, how="inner").dropna()
    vento.columns = ["ws", "wd"]
    if vento.empty:
        raise ValueError("Nessuna coppia valida velocità/direzione.")

    # Settori centrati su 0, 30, 60, .. gradi
    ampiezza = 360 / n_settori
    vento["settore"] = ((vento["wd"] + ampiezza / 2) % 360 // ampiezza).astype(int)

    righe = []
    for settore in range(n_settori):
        velocita = vento.loc[vento["settore"] == settore, "ws"]
        A, k = MetodoMinimiQuadrati_weibull(velocita)
        righe.append({"settore": settore, "wd_deg": settore * ampiezza, "n_ore": len(velocita),
                      "p_wd": len(velocita) / len(vento), "A_ms": A, "k": k})
    settori = pd.DataFrame(righe)

    # Individuo i settori con A o k mancanti
    non_calcolabili = settori[["A_ms", "k"]].isna().any(axis=1)
    if non_calcolabili.any():
        direzioni = settori.loc[non_calcolabili, "wd_deg"].tolist()
        raise ValueError(f"Weibull non calcolabile nei settori {direzioni} gradi. Controlla i dati.")

    site = UniformWeibullSite(p_wd=settori["p_wd"].to_numpy(), a=settori["A_ms"].to_numpy(), k=settori["k"].to_numpy(), ti=ti)
    print(f"Site parco {id_parco} creato con successo")
    return site, vento, settori

def disegna_rosa_site(site, vento, settori, id_parco, save = False, show = True):
    velocita_massima = vento["ws"].max()
    limite = int(np.ceil(velocita_massima / 4)) * 4
    classi = np.arange(0, limite + 4, 4)
    site.plot_wd_distribution(n_wd=12, ws_bins=classi)

    ax = plt.gca()
    ax.set_rlabel_position(22.5)
    ax.set_ylim(0, settori["p_wd"].max() + 0.02)
    ax.set_thetagrids([0, 45, 90, 135, 180, 225, 270, 315], labels=["N", "NE", "E", "SE", "S", "SO", "O", "NO"])
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax.legend(title="Velocità", loc="upper left", bbox_to_anchor=(1.15, 1))
    ax.set_title(f"Rosa dei venti parco {id_parco}")
    if save:
        plt.savefig(Path_dir / "Output_vento" / "rose_venti" / f"rosa_venti_parco_{id_parco}.png", dpi=200, bbox_inches="tight")
        print(f"Figura salvata: {Path_dir / "rose_venti" / "Output_vento" / f"rosa_venti_parco_{id_parco}.png"}")
    if show:
        plt.show()
    plt.close()

def ricostruisci_settori(site, vento):
    ds = site.ds.sel(wd=site.ds.wd < 360)
    n_settori = ds.sizes["wd"]
    conteggi = (vento["settore"] .value_counts() .reindex(range(n_settori), fill_value=0))

    return pd.DataFrame({
        "settore": np.arange(n_settori),
        "wd_deg": ds["wd"].values,
        "n_ore": conteggi.to_numpy(),
        "p_wd": ds["Sector_frequency"].values,
        "A_ms": ds["Weibull_A"].values,
        "k": ds["Weibull_k"].values
    })

def disegna_weibull_settoriale(vento, site, id_parco, save = False, show = True):
    settori = ricostruisci_settori(site, vento)
    fig, assi = plt.subplots(4, 3, figsize=(14, 12), sharex=True, sharey=True)
    assi = assi.flatten()

    massimo = int(np.ceil(vento["ws"].max()))
    classi = np.arange(0, massimo + 1)
    x = np.linspace(0, massimo, 500)

    for i in range(12):
        ax = assi[i]
        riga = settori.iloc[i]
        velocita = vento.loc[vento["settore"] == riga["settore"], "ws"]
        A = riga["A_ms"]
        k = riga["k"]

        ax.hist(velocita, bins=classi, density=True, color="skyblue", edgecolor="white", label="Dati osservati")
        ax.plot(x, weibull_min.pdf(x, k, scale=A), color="red", label="Weibull")

        ax.set_title(f"{riga['wd_deg']:.0f}° — {len(velocita)} ore\n" f"A = {A:.2f} m/s; k = {k:.2f}")
        ax.set_xlabel("Velocità [m/s]")
        ax.set_ylabel("Densità")
        ax.grid(alpha=0.3)

    assi[0].legend()
    fig.suptitle(f"Dati osservati e Weibull — parco {id_parco}")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    if save:
        fig.savefig(Path_dir / "Output_vento" / "weibull_settori" / f"weibull_settori_{id_parco}.png", dpi=200, bbox_inches="tight")
        print(f"Figura salvata: {Path_dir / "Output_vento" / "weibull_settori" / f"weibull_settori_{id_parco}.png"}")
    if show:
        plt.show()
    plt.close(fig)

def disegna_weibull_totale(vento, id_parco, save=False, show=True, ax=None):
    figura_propria = ax is None

    if figura_propria:
        fig, ax = plt.subplots(figsize=(9, 6))
    else:
        fig = ax.figure

    velocita = vento["ws"].dropna()
    A, k = MetodoMinimiQuadrati_weibull(velocita)

    massimo = int(np.ceil(velocita.max()))
    classi = np.arange(0, massimo + 0.5, 0.5)
    x = np.linspace(0.001, massimo, 500)

    if figura_propria:
        ax.hist(velocita, bins=classi, density=True, color="skyblue", edgecolor="white", label="Dati osservati")
        ax.plot(x, weibull_min.pdf(x, k, scale=A), color="red", label="Weibull")
        ax.set_title(f"Tutte le direzioni — parco {id_parco} — " f"{len(velocita)} ore\n" f"A = {A:.2f} m/s; k = {k:.2f}")
    else:
        ax.plot(x, weibull_min.pdf(x, k, scale=A))

    ax.set_xlabel("Velocità [m/s]")
    ax.set_ylabel("Densità")
    ax.grid(alpha=0.3)

    if figura_propria:
        ax.legend()
        fig.tight_layout()
        if save:
            fig.savefig(Path_dir / "Output_vento" / "weibul_totali" / f"weibull_totale_{id_parco}.png", dpi=200, bbox_inches="tight")
            print(f"Figura salvata: {Path_dir / "Output_vento" / "weibul_totali" / f"weibull_totale_{id_parco}.png"}")
        if show:
            plt.show()
        plt.close(fig)


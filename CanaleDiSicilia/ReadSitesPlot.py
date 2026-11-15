from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

def leggi_layer(nome, campo_id):
    Path_dir = Path(__file__).resolve().parent
    layer = gpd.read_file(Path_dir / "data" / "eolico_off_sicilia_progetti" / nome)
    layer[campo_id] = pd.to_numeric(layer[campo_id], errors="raise").astype("Int64")
    return layer.to_crs("EPSG:32632")

def crea_layout(id_parco):
    poligoni = leggi_layer("Eolico_offshore_sicilia_polygon.shp", "id_RSE")
    turbine = leggi_layer("Eolico_offshore_sicilia_WTG.shp", "Id_RSE")
    progetti = leggi_layer("eolico_offshore_sicilia_progetti_coord.shp", "id_rse")

    # Nome dal CSV
    Path_dir = Path(__file__).resolve().parent
    file_indice = Path_dir / "data" / "eolico_off_sicilia_progetti" / "indice_parchi.csv"
    nome = ""
    df_indice = pd.read_csv(file_indice, sep=";", keep_default_na=False)
    riga_parco = df_indice[pd.to_numeric(df_indice["id_RSE"]) == id_parco]
    if not riga_parco.empty:
        nome = riga_parco["nome_parco"].iloc[0]
    nome_parco = f"Parco ID {id_parco}" + (f" - {nome}" if nome else "")

    # Selezione del parco
    if id_parco in [77, 123]:
        id_parco = 123
        poly = poligoni[poligoni["id_RSE"] == 77]
        wtg = turbine[turbine["Id_RSE"] == 123]
        proj = progetti[progetti["id_rse"] == 123]
        print("Per i parchi 77 e 123: uso il poligono 77 con le turbine e il punto progetto 123.")
    else:
        poly = poligoni[poligoni["id_RSE"] == id_parco]
        wtg = turbine[turbine["Id_RSE"] == id_parco]
        proj = progetti[progetti["id_rse"] == id_parco]

    # Coordinate metriche
    x = wtg.geometry.x.to_numpy()
    y = wtg.geometry.y.to_numpy()
    print(f"Layout parco {nome_parco} letto con successo")
    return poly, proj, x, y, nome_parco, Path_dir, id_parco

def plot_layout(dati_parco, ax=None, save=False, show=True):
    poly, proj, x, y, nome_parco, Path_dir, id_parco = dati_parco

    fig_autonoma = ax is None  # True if ax is None (figura autonoma) else False (confronto tra parchi)

    if fig_autonoma:
        fig, ax = plt.subplots(figsize=(6, 6))
        # Stile per un singolo parco
        riempimento, bordo, punti, croce = "lightblue", "navy", "crimson", "darkorange"
        etichette = ["Poligono", f"Turbine ({len(x)})", "Punto progetto"]
    else:
        # Stile per il confronto tra parchi: colore scelto automaticamente
        _, nomi_presenti = ax.get_legend_handles_labels()
        colore = f"C{len(nomi_presenti) % 10}"
        riempimento = bordo = punti = croce = colore
        ax.plot([], [], "s", color=colore, label=nome_parco)

    # plot poligono, turbine e punto progetto (se esistono)
    if not poly.empty:
        poly.plot(ax=ax, facecolor=riempimento, edgecolor=bordo, alpha=0.4, label=etichette[0] if fig_autonoma else None)
    if len(x):
        ax.scatter(x, y, s=22, color=punti, zorder=3, label=etichette[1] if fig_autonoma else None)
    if not proj.empty:
        proj.plot(ax=ax, color=croce, marker="x", markersize=65, zorder=4, label=etichette[2] if fig_autonoma else None)

    ax.set(xlabel="Est [m] - UTM 32N", ylabel="Nord [m] - UTM 32N")
    ax.set_aspect("equal")
    ax.ticklabel_format(style="plain", useOffset=False)
    ax.legend(loc="best")
    ax.grid(alpha=0.3)

    if fig_autonoma:
        ax.set_title(nome_parco)
        fig.tight_layout()
        if save:
            fig.savefig(Path_dir / "Layout_parchi" / f"parco_{id_parco}_layout.png", dpi=250)
            print(f"Figura salvata: {Path_dir / "Layout_parchi" / f"parco_{id_parco}_layout.png"}")
        if show:
            plt.show()
        plt.close(fig)
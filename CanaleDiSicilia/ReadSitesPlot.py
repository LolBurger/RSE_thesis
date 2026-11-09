from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

def leggi_layer(nome, campo_id):
    Path_dir = Path(__file__).resolve().parent
    dati = Path(Path_dir/"data/eolico_off_sicilia_progetti")
    file = dati / nome
    layer = gpd.read_file(file)
    layer[campo_id] = pd.to_numeric(layer[campo_id]).astype("Int64")
    
    return layer.to_crs("EPSG:32632")

def main(id_parco):
    poligoni = leggi_layer("Eolico_offshore_sicilia_polygon.shp", "id_RSE")
    turbine = leggi_layer("Eolico_offshore_sicilia_WTG.shp", "Id_RSE")
    progetti = leggi_layer("eolico_offshore_sicilia_progetti_coord.shp", "id_rse")

    # Nome dal CSV
    Path_dir = Path(__file__).resolve().parent
    file_indice = Path_dir / "indice_parchi.csv"
    nome = ""
    df_indice = pd.read_csv(file_indice, sep=";", keep_default_na=False)
    riga_parco = df_indice[pd.to_numeric(df_indice["id_RSE"]) == id_parco]
    if not riga_parco.empty:
        nome = riga_parco["nome_parco"].iloc[0]

    # Selezione del parco
    if id_parco in [77, 123]:
        id_parco = 123
        poly = poligoni[poligoni["id_RSE"] == 77]
        wtg = turbine[turbine["Id_RSE"] == 123]
        proj = progetti[progetti["id_rse"] == 123]

        print("ATTENZIONE: associazione manuale, non confermata.")
        print("Uso il poligono 77 con le turbine e il punto progetto 123.")

    else:
        poly = poligoni[poligoni["id_RSE"] == id_parco]
        wtg = turbine[turbine["Id_RSE"] == id_parco]
        proj = progetti[progetti["id_rse"] == id_parco]

    # Se non ha trovato nulla in nessun layer, lo script si ferma
    if poly.empty and wtg.empty and proj.empty:
        raise SystemExit(f"ID {id_parco} non trovato nei layer disponibili.")

    nome_parco = f"Parco ID {id_parco}" + (f" - {nome}" if nome else "")

    # Coordinate metriche
    x = wtg.geometry.x.to_numpy()
    y = wtg.geometry.y.to_numpy()
    return poly, proj, x, y, nome_parco, Path_dir, id_parco

def grafico(fromMain):
    poly, proj, x, y, nome_parco, Path_dir, id_parco = fromMain
    # Grafico: rappresenta soltanto gli elementi disponibili
    fig, ax = plt.subplots(figsize=(7, 7))
    if not poly.empty:
        poly.plot(ax=ax, facecolor="lightblue", edgecolor="navy", alpha=0.4, label="Poligono")

    if len(x):
        ax.scatter(x, y, s=22, color="crimson", label=f"Turbine ({len(x)})", zorder=3)

    if not proj.empty:
        proj.plot(ax=ax, color="darkorange", marker="x", markersize=65, zorder=4, label="Punto progetto")

    ax.set(title=nome_parco, xlabel="Est [m] - UTM 32N", ylabel="Nord [m] - UTM 32N")
    ax.set_aspect("equal")
    ax.ticklabel_format(style="plain", useOffset=False)
    ax.legend(loc="best")
    ax.grid(alpha=0.3)
    fig.tight_layout()

    fig.savefig(Path_dir / "Layout_parchi" / f"parco_{id_parco}_layout.png", dpi=250)
    print(f"Figura salvata: {Path_dir / "Layout_parchi" / f"parco_{id_parco}_layout.png"}")

    plt.show()

if __name__ == "__main__":
    id_parco = 19  # ID del parco da visualizzare
    poly, proj, x, y, nome_parco, Path_dir, id_parco = main(id_parco)
    grafico(poly, proj, x, y, nome_parco, Path_dir, id_parco)

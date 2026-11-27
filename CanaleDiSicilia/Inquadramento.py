from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pyproj import Transformer
from shapely.geometry import box
from matplotlib.patches import Rectangle
import contextily as ctx
from ReadSitesPlot import crea_layout
Path_dir = Path(__file__).resolve().parent

def ritaglia_e_riproietta_in_utm32n(percorso, xmin, ymin, xmax, ymax):
    dati = gpd.read_file(percorso)
    trasformatore = Transformer.from_crs("EPSG:32632", dati.crs, always_xy=True)
    limiti_ritaglio = trasformatore.transform_bounds(xmin, ymin, xmax, ymax, densify_pts=101)
    ritaglio = gpd.GeoSeries([box(*limiti_ritaglio)], crs=dati.crs)
    dati_locali = gpd.clip(dati, ritaglio)
    return dati_locali.to_crs(epsg=32632)


def plot_inquadramento_cluster(street_map=False, detailed_map= False, save=False):
    xmin, xmax = 655000, 1097000
    ymin, ymax = 3927000, 4250000

    cluster_1 = [110, 112, 111, 109, 26, 21, 67, 35, 115, 71, 27, 118, 79, 42, 40, 84]
    cluster_2 = [19, 108, 106, 123, 96, 41, 82, 116]
    solo_poligono = [40, 84, 116]
    
    offset_etichette = {110: (0, 15000), 112: (0, 14000), 111: (1000, 13000), 109: (-10000, 0), 26: (0, 12000),
                    21: (0, 8000), 67: (0, 11000), 35: (+4000, -15000), 40: (13000, 14000), 115: (22000, 4000),
                    84: (16000, 1000), 71: (-2000, -11000), 27: (-5000, 8000), 118: (0, -12000), 79: (0, 10000),
                    42: (0, 12000), 19: (0, 12000), 108: (-2000, 11000), 106: (0, 11000), 123: (0, 13000), 96: (12000, 0),
                    41: (14000, 0), 82: (0, 30000), 116: (0, 10000)}

    colori_parchi = {110: "#1F77B4", 112: "#D95F02", 111: "#2CA02C", 109: "#D62728", 26: "#9467BD", 21: "#8C564B",
                     67: "#C51B7D", 35: "#666666", 115: "#8C8C00", 71: "#008B8B", 27: "#393B79", 118: "#637939",
                     79: "#8C6D31", 42: "#843C39", 40: "#7B4173", 84: "#3182BD", 19: "#E6550D", 108: "#31A354",
                     106: "#756BB1", 123: "#636363", 96: "#A55194", 41: "#006D77", 82: "#B2182B", 116: "#A6761D", }

    rettangoli_cluster = [{"nome": "cluster 1", "colore": "#2878B5", "xmin": 670000, "xmax": 900000, "ymin": 4085000, "ymax": 4235000},
                          {"nome": "cluster 2", "colore": "#F28E2B", "xmin": 945000, "xmax": 1080000, "ymin": 3945000, "ymax": 4110000}]
    
    if detailed_map:
        inquadramenti = [(rettangoli_cluster[0], [(cluster_1, "#2878B5")], "inquadramento_cluster_1"),
                         (rettangoli_cluster[1], [(cluster_2, "#F28E2B")], "inquadramento_cluster_2")]
    else:
        area_generale = { "nome": "cluster dei parchi eolici", "xmin": xmin, "xmax": xmax, "ymin": ymin, "ymax": ymax }

        inquadramenti = [(area_generale, [(cluster_1, "#2878B5"), (cluster_2, "#F28E2B")], "inquadramento_Canale_di_Sicilia")]

    for area, cluster_da_disegnare, nome_file in inquadramenti:
        fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)

        ax.set_xlim(area["xmin"], area["xmax"])
        ax.set_ylim(area["ymin"], area["ymax"])
        ax.set_aspect("equal")

        if street_map:
            ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs="EPSG:32632", zoom=9, attribution_size=7,
                            zorder=0, headers={"User-Agent": "MappaParchiEoliciSicilia/1.0"})
        else:
            Path_ne_10m_land = Path_dir / "mappe" / "ne_10m_land" / "ne_10m_land.shp"
            ne_10m_land_locale_utm = ritaglia_e_riproietta_in_utm32n(Path_ne_10m_land, xmin, ymin, xmax, ymax)
            ne_10m_land_locale_utm.plot(ax=ax, facecolor="#EFEEEA", edgecolor="none", zorder=1)

        for cluster, colore_cluster in cluster_da_disegnare:
            for id_parco in cluster:
                poly, _, x, y, _, _, _ = crea_layout(id_parco)

                if street_map:
                    colore = colori_parchi[id_parco]
                else:
                    colore = "#808080" if id_parco in solo_poligono else colore_cluster

                poly.boundary.plot(ax=ax, color=colore, linewidth=0.3, zorder=2)

                if id_parco not in solo_poligono:
                    ax.scatter(x, y, color=colore, s=3, edgecolors="none", zorder=3)

                punto = poly.geometry.representative_point().iloc[0]
                offset_x, offset_y = offset_etichette.get(id_parco, (0, 0))

                ax.text(punto.x + offset_x, punto.y + offset_y, str(id_parco), color=colore, fontsize=7,
                        ha="center", va="center", zorder=4, clip_on=True )

        # Rettangoli solo nell'inquadramento generale.
        if not detailed_map:
            for cluster in rettangoli_cluster:
                rettangolo = Rectangle((cluster["xmin"], cluster["ymin"]), width=cluster["xmax"] - cluster["xmin"],
                                       height=cluster["ymax"] - cluster["ymin"], fill=False, edgecolor=cluster["colore"])
                ax.add_patch(rettangolo)

                ax.text(cluster["xmin"] + 4000, cluster["ymax"] + 8000, f"zoom: {cluster['nome']}", color=cluster["colore"],
                        fontsize=8, ha="left", va="top", zorder=5)

        ax.xaxis.set_major_formatter(FuncFormatter(lambda valore, posizione: f"{valore / 1000:.0f}"))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda valore, posizione: f"{valore / 1000:.0f}"))

        ax.set_xlim(area["xmin"], area["xmax"])
        ax.set_ylim(area["ymin"], area["ymax"])
        ax.set_aspect("equal")

        ax.set_xlabel("Est UTM 32N (km)")
        ax.set_ylabel("Nord UTM 32N (km)")
        ax.set_title(f"Canale di Sicilia — {area['nome']}")
        ax.set_facecolor("white")
        ax.tick_params(top=True, right=True, direction="out")

        if save:
            suffisso = "_osm" if street_map else ""
            fig.savefig(Path_dir/ "Layout_parchi" / f"{nome_file}{suffisso}.png", dpi=600, bbox_inches="tight")
            print(f"Figura salvata: {Path_dir/ "Layout_parchi" / f"{nome_file}{suffisso}.png"}")
        plt.show()
        plt.close(fig)

# plot_inquadramento_cluster(street_map=True, detailed_map=False, save= True)
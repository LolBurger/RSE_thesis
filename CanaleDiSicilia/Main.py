from pathlib import Path
import matplotlib.pyplot as plt
from ReadSitesPlot import crea_layout, plot_layout
from VentoSite import crea_site_parco, disegna_rosa_site, disegna_weibull
from TurbinaIEA15MW import crea_turbina_IEA_15MW, grafici_turbina
Path_dir = Path(__file__).resolve().parent

# id_parchi =[19,21,26,27,35,40,41,42,67,71,77,79,82,84,96,106,108,109,110,111,112,115,116,118,123]
# id_parchi = [115, 35, 71, 67, 40, 84]
id_parchi = [118, 27, 79]

# Layout parchi
layout_sites = [crea_layout(id_parco) for id_parco in id_parchi]    # poly, proj, x, y, nome_parco, Path_dir, id_parco = layout_site 
nome_parchi = [layout_site[4] for layout_site in layout_sites]
show_layout = True
save_layout = False

# Dati vento
wind_sites = [crea_site_parco(123 if id_parco == 77 else id_parco, n_settori=12, ti=0.08) for id_parco in id_parchi] # site, vento, settori = wind_site
show_rosa = True
show_weibull = False
save_rosa = True
save_weibull = False

# Dati turbina IEA 15 MW
turbina = crea_turbina_IEA_15MW()
show_turbina = True
save_turbina = False

print("Lettura layout parco/parchi, dati vento e dati turbina avvenuta con successo")

### GRAFICI DATI INPUT ###
# Grafico dei layout dei parchi
if show_layout or save_layout:

    if len(layout_sites) > 1:
        fig, ax = plt.subplots(figsize=(12, 6))

        for layout_site in layout_sites:
            plot_layout(layout_site, ax=ax)

        ax.set_title("Layout parchi")
        ax.legend(loc="best") # ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=9)
        fig.tight_layout()

        if save_layout:
            fig.savefig(Path_dir / "Layout_parchi" / f"Layout_{'_'.join(map(str, id_parchi))}.png", dpi=250)
            print(f"Figura salvata: {Path_dir / "Layout_parchi" / f"Layout_{'_'.join(map(str, id_parchi))}.png"}")

        if show_layout:
            plt.show()

        plt.close(fig)

    elif len(layout_sites) == 1:
        plot_layout(layout_sites[0], save=save_layout, show=show_layout)

# Print dati vento, rosa dei venti e Weibull per ciascun parco
if show_rosa or show_weibull or save_rosa or save_weibull:

    NomePeriodo_parchi = []
    for i in range(len(id_parchi)):
        NomePeriodo_parco = f"{nome_parchi[i]}\n{wind_sites[i][1].index.min().date()} / {wind_sites[i][1].index.max().date()}"
        NomePeriodo_parchi.append(NomePeriodo_parco)
        print(f"\n{NomePeriodo_parco}")
        # print("\nParametri per settore:\n", wind_sites[i][2].to_string(index=False))
        disegna_rosa_site(site=wind_sites[i][0], vento=wind_sites[i][1], settori=wind_sites[i][2], id_parco=id_parchi[i], save=save_rosa, show=show_rosa)
        disegna_weibull(vento=wind_sites[i][1], settori=wind_sites[i][2], id_parco=id_parchi[i], save=save_weibull, show=show_weibull)

# Grafici turbina IEA 15 MW
if show_turbina or save_turbina:
    grafici_turbina(turbina, save=save_turbina, show=show_turbina)

# Simulazione PyWake
# ...
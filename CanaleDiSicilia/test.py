#from pathlib import Path
from ReadSitesPlot import grafico, main
for pfp in [19,21,26,27,35,40,41,42,67,71,77,79,82,84,96,106,108,109,110,111,112,115,116,118,123]:
    id_parco = pfp
    risultato = main(id_parco)
    x = risultato[2]
    # y = risultato[3]
    nome_parco = risultato[4]
    print(f"Turbine disponibili: {len(x)}")
    print(nome_parco)
    grafico(risultato)

grafico(risultato)
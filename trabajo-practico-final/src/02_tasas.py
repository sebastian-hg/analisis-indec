"""
02_tasas.py - Tasas del mercado laboral por trimestre y aglomerado.

Calcula las TRES tasas que pide la consigna, con las definiciones del INDEC y
ponderando por PONDERA, para cada trimestre disponible (2016-2025):

    PEA (activos) = ocupados + desocupados            (ESTADO 1 y 2)
    Tasa de actividad    = PEA        / población total * 100
    Tasa de empleo       = ocupados   / población total * 100
    Tasa de desocupación = desocupados / PEA           * 100

Guarda output/tablas/tasas.csv (por trimestre) y tasas_anual.csv (promedio
anual, para tablas más legibles en el informe).

Uso:  python src/02_tasas.py
"""

import os
import pandas as pd
import comun


def calcular_tasas(panel):
    filas = []
    claves = ["PERIODO", "PERIODO_NUM", "ANIO", "TRIMESTRE", "AGLOMERADO"]
    for vals, g in panel.groupby(claves):
        periodo, periodo_num, anio, trim, aglo = vals
        pt = g["PONDERA"].sum()
        ocupados = g.loc[g["ESTADO"] == comun.ESTADO_OCUPADO, "PONDERA"].sum()
        desocupados = g.loc[g["ESTADO"] == comun.ESTADO_DESOCUPADO, "PONDERA"].sum()
        pea = ocupados + desocupados
        filas.append({
            "PERIODO": periodo, "PERIODO_NUM": periodo_num,
            "ANIO": anio, "TRIMESTRE": trim,
            "AGLOMERADO": comun.AGLOMERADOS[aglo],
            "TASA_ACTIVIDAD": round(pea / pt * 100, 2) if pt else None,
            "TASA_EMPLEO": round(ocupados / pt * 100, 2) if pt else None,
            "TASA_DESOCUPACION": round(desocupados / pea * 100, 2) if pea else None,
        })
    return pd.DataFrame(filas).sort_values(["AGLOMERADO", "PERIODO_NUM"]).reset_index(drop=True)


def main():
    panel = pd.read_parquet(comun.PANEL_PARQUET)
    tasas = calcular_tasas(panel)
    tasas.to_csv(os.path.join(comun.TABLAS, "tasas.csv"), index=False)

    # Promedio anual (para tablas del informe).
    cols = ["TASA_ACTIVIDAD", "TASA_EMPLEO", "TASA_DESOCUPACION"]
    anual = (tasas.groupby(["ANIO", "AGLOMERADO"])[cols].mean().round(2).reset_index())
    anual.to_csv(os.path.join(comun.TABLAS, "tasas_anual.csv"), index=False)

    for col, titulo in [("TASA_ACTIVIDAD", "TASA DE ACTIVIDAD (% , prom. anual)"),
                        ("TASA_EMPLEO", "TASA DE EMPLEO (%)"),
                        ("TASA_DESOCUPACION", "TASA DE DESOCUPACIÓN (%)")]:
        print(f"\n{titulo}")
        print(anual.pivot(index="ANIO", columns="AGLOMERADO", values=col).to_string())

    print(f"\nGuardado: tasas.csv ({len(tasas)} filas trimestrales) y tasas_anual.csv")


if __name__ == "__main__":
    main()

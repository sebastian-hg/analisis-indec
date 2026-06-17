"""
03_ingresos_reales.py - Evolución de los ingresos a precios constantes.

El ingreso nominal no es comparable entre trimestres por la inflación. Se
deflacta con el IPC del INDEC (factor ya calculado en el panel, columna
FACTOR_REAL) y se expresa en pesos del período base (4º trimestre de 2025).

Usa P47T = ingreso total individual, sobre los PERCEPTORES (P47T > 0); el
código -9 (no respuesta) se excluye acá y se modela en el script 07.

Guarda ingresos_reales.csv (por trimestre) e ingresos_anual.csv (prom. anual).

Uso:  python src/03_ingresos_reales.py
"""

import os
import pandas as pd
import comun


def main():
    panel = pd.read_parquet(comun.PANEL_PARQUET)
    perc = panel[panel["P47T"] > 0].copy()
    perc["P47T_REAL"] = perc["P47T"] * perc["FACTOR_REAL"]

    claves = ["PERIODO", "PERIODO_NUM", "ANIO", "TRIMESTRE", "AGLOMERADO"]
    filas = []
    for vals, g in perc.groupby(claves):
        periodo, periodo_num, anio, trim, aglo = vals
        filas.append({
            "PERIODO": periodo, "PERIODO_NUM": periodo_num,
            "ANIO": anio, "TRIMESTRE": trim,
            "AGLOMERADO": comun.AGLOMERADOS[aglo],
            "N_PERCEPTORES": len(g),
            "MEDIANA_NOMINAL": round(g["P47T"].median(), 0),
            "MEDIA_REAL": round(g["P47T_REAL"].mean(), 0),
            "MEDIANA_REAL": round(g["P47T_REAL"].median(), 0),
            "P25_REAL": round(g["P47T_REAL"].quantile(0.25), 0),
            "P75_REAL": round(g["P47T_REAL"].quantile(0.75), 0),
        })
    res = pd.DataFrame(filas).sort_values(["AGLOMERADO", "PERIODO_NUM"]).reset_index(drop=True)
    res.to_csv(os.path.join(comun.TABLAS, "ingresos_reales.csv"), index=False)

    # Promedio anual de la mediana real (para tablas del informe).
    anual = (res.groupby(["ANIO", "AGLOMERADO"])
                .agg(MEDIANA_REAL=("MEDIANA_REAL", "mean"),
                     MEDIANA_NOMINAL=("MEDIANA_NOMINAL", "mean"))
                .round(0).reset_index())
    anual.to_csv(os.path.join(comun.TABLAS, "ingresos_anual.csv"), index=False)

    print("INGRESO MEDIANO REAL (promedio anual, en " + comun.ETIQUETA_PRECIOS + ")")
    print(anual.pivot(index="ANIO", columns="AGLOMERADO", values="MEDIANA_REAL").to_string())
    print(f"\nGuardado: ingresos_reales.csv ({len(res)} filas) e ingresos_anual.csv")


if __name__ == "__main__":
    main()

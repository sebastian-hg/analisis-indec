"""
05_univariado.py - Exploración univariada: no respuesta y outliers (objetivo 1).

  1. NO RESPUESTA a ingresos: % de ocupados que no declararon P21 (= -9), por
     trimestre y aglomerado.
  2. OUTLIERS del ingreso real, por el método del rango intercuartílico (IQR),
     por aglomerado.

Guarda no_respuesta.csv y outliers.csv.

Uso:  python src/05_univariado.py
"""

import os
import pandas as pd
import comun


def no_respuesta(panel):
    ocup = panel[panel["ESTADO"] == comun.ESTADO_OCUPADO]
    claves = ["PERIODO", "PERIODO_NUM", "ANIO", "TRIMESTRE", "AGLOMERADO"]
    filas = []
    for vals, g in ocup.groupby(claves):
        periodo, periodo_num, anio, trim, aglo = vals
        nr = (g["P21"] == comun.NO_RESPUESTA_INGRESO).sum()
        filas.append({
            "PERIODO": periodo, "PERIODO_NUM": periodo_num,
            "ANIO": anio, "TRIMESTRE": trim,
            "AGLOMERADO": comun.AGLOMERADOS[aglo],
            "OCUPADOS": len(g), "NO_RESPUESTA": int(nr),
            "PCT_NO_RESPUESTA": round(nr / len(g) * 100, 1) if len(g) else None,
        })
    return pd.DataFrame(filas).sort_values(["AGLOMERADO", "PERIODO_NUM"])


def outliers(panel):
    df = panel[panel["P47T"] > 0].copy()
    df["P47T_REAL"] = df["P47T"] * df["FACTOR_REAL"]
    filas = []
    for aglo, g in df.groupby("AGLO_NOMBRE"):
        q1, q3 = g["P47T_REAL"].quantile([0.25, 0.75])
        iqr = q3 - q1
        ls = q3 + 1.5 * iqr
        out = g[(g["P47T_REAL"] < q1 - 1.5 * iqr) | (g["P47T_REAL"] > ls)]
        filas.append({
            "AGLOMERADO": aglo, "N": len(g),
            "Q1": round(q1, 0), "MEDIANA": round(g["P47T_REAL"].median(), 0), "Q3": round(q3, 0),
            "LIM_SUP": round(ls, 0), "OUTLIERS": len(out),
            "PCT_OUTLIERS": round(len(out) / len(g) * 100, 1), "MAX": round(g["P47T_REAL"].max(), 0),
        })
    return pd.DataFrame(filas)


def main():
    panel = pd.read_parquet(comun.PANEL_PARQUET)

    nr = no_respuesta(panel)
    nr.to_csv(os.path.join(comun.TABLAS, "no_respuesta.csv"), index=False)
    print("NO RESPUESTA A INGRESOS (P21 == -9), máximo por aglomerado:")
    print(nr.groupby("AGLOMERADO")["PCT_NO_RESPUESTA"].agg(["min", "max", "mean"]).round(1).to_string())

    out = outliers(panel)
    out.to_csv(os.path.join(comun.TABLAS, "outliers.csv"), index=False)
    print("\nOUTLIERS DEL INGRESO REAL (IQR, en " + comun.ETIQUETA_PRECIOS + "):")
    print(out.to_string(index=False))
    print(f"\nTablas guardadas en: {comun.TABLAS}")


if __name__ == "__main__":
    main()

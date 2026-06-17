"""
04_multivariado.py - Análisis multivariado del ingreso (objetivo 2).

Cruza el ingreso laboral REAL de los ocupados con sexo, edad, nivel educativo,
calificación de la tarea (PP04D_COD) y rama de actividad (PP04B_COD).

Usa P21 (ingreso de la ocupación principal) deflactado (columna FACTOR_REAL),
sobre los OCUPADOS con P21 > 0.

  - Foto del último año (todos sus trimestres) para cada cruce.
  - Evolución de la brecha de género por trimestre.

Uso:  python src/04_multivariado.py
"""

import os
import pandas as pd
import comun


def preparar(panel):
    df = panel[(panel["ESTADO"] == comun.ESTADO_OCUPADO) & (panel["P21"] > 0)].copy()
    df["P21_REAL"] = df["P21"] * df["FACTOR_REAL"]
    df["SEXO"] = df["CH04"].map(comun.SEXO)
    df["NIVEL"] = df["NIVEL_ED"].map(comun.NIVEL_ED)
    df["EDAD_GRUPO"] = df["CH06"].apply(comun.rango_etario)
    df["CALIFICACION"] = df["PP04D_COD"].apply(comun.calificacion_tarea)
    df["SECTOR"] = df["PP04B_COD"].apply(comun.sector_actividad)
    return df


def foto(df, anio, dimension, etiqueta, archivo):
    sub = df[df["ANIO"] == anio]
    tabla = (sub.groupby(["AGLO_NOMBRE", dimension])["P21_REAL"]
                .median().round(0).reset_index()
                .rename(columns={"P21_REAL": "INGRESO_REAL_MEDIANO"}))
    tabla.to_csv(os.path.join(comun.TABLAS, archivo), index=False)
    print(f"\n--- INGRESO REAL MEDIANO {anio} por {etiqueta} ---")
    print(tabla.pivot(index=dimension, columns="AGLO_NOMBRE",
                      values="INGRESO_REAL_MEDIANO").to_string())


def brecha_genero(df):
    g = (df.groupby(["PERIODO", "PERIODO_NUM", "AGLO_NOMBRE", "SEXO"])["P21_REAL"]
            .median().reset_index())
    pv = g.pivot_table(index=["PERIODO", "PERIODO_NUM", "AGLO_NOMBRE"],
                       columns="SEXO", values="P21_REAL").reset_index()
    pv["BRECHA_%"] = ((pv["Mujer"] / pv["Varón"] - 1) * 100).round(1)
    pv = pv.sort_values(["AGLO_NOMBRE", "PERIODO_NUM"])
    pv.to_csv(os.path.join(comun.TABLAS, "brecha_genero.csv"), index=False)
    print("\n--- BRECHA DE GÉNERO (promedio del período, %) ---")
    print(pv.groupby("AGLO_NOMBRE")["BRECHA_%"].mean().round(1).to_string())


def main():
    panel = pd.read_parquet(comun.PANEL_PARQUET)
    df = preparar(panel)
    anio = int(df["ANIO"].max())   # último año disponible (todos sus trimestres)

    foto(df, anio, "SEXO", "sexo", "ing_x_sexo.csv")
    foto(df, anio, "NIVEL", "nivel educativo", "ing_x_educacion.csv")
    foto(df, anio, "EDAD_GRUPO", "rango etario", "ing_x_edad.csv")
    foto(df, anio, "CALIFICACION", "calificación de la tarea", "ing_x_calificacion.csv")
    foto(df, anio, "SECTOR", "rama de actividad", "ing_x_rama.csv")
    brecha_genero(df)

    # Guardamos el año de la foto para que el informe lo cite.
    pd.DataFrame([{"ANIO_FOTO": anio}]).to_csv(
        os.path.join(comun.TABLAS, "anio_foto.csv"), index=False)
    print(f"\nFoto multivariada del año {anio}. Tablas guardadas en {comun.TABLAS}")


if __name__ == "__main__":
    main()

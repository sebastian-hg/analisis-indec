"""
05_univariado.py - Analisis univariado: exploracion, no respuesta y outliers (objetivo 1).

Calcula, sobre el ingreso real de la ocupacion principal de los ocupados (P21
deflactado), tomando el ultimo ano disponible como foto:
  1. Estadisticas descriptivas: medidas de tendencia central (media, mediana),
     de dispersion (desvio estandar, coeficiente de variacion, rango
     intercuartilico) y de forma (asimetria de Fisher, curtosis).
  2. NO RESPUESTA a ingresos: % de ocupados que no declararon P21 (= -9).
  3. OUTLIERS: metodo del rango intercuartilico, distinguiendo outliers
     moderados (entre 1.5 y 3 RI) y severos (mas de 3 RI), y metodo del
     z-score (regla de los tres desvios, |z| > 3).

Guarda descriptivas.csv, no_respuesta.csv y outliers.csv.

Uso:  python src/05_univariado.py
"""

import os
import pandas as pd
from scipy import stats
import comun


def ingreso_principal_real(panel):
    """Toma a los ocupados que declararon su ingreso de la ocupacion principal (P21 > 0)
    del ULTIMO ano disponible, y les calcula el ingreso a precios constantes (real).

    Es el mismo recorte que usan el histograma y los cruces: una foto del ultimo ano.
    """
    anio_foto = int(panel["ANIO"].max())
    ocupados = panel[(panel["ESTADO"] == comun.ESTADO_OCUPADO) &
                     (panel["P21"] > 0) & (panel["ANIO"] == anio_foto)].copy()
    ocupados["REAL"] = ocupados["P21"] * ocupados["FACTOR_REAL"]
    return ocupados


def descriptivas(ingresos):
    """Medidas de resumen del ingreso real, por aglomerado."""
    filas_resumen = []
    for aglomerado, grupo in ingresos.groupby("AGLO_NOMBRE"):
        ingreso_del_grupo = grupo["REAL"]
        filas_resumen.append({
            "AGLOMERADO": aglomerado,
            "N": len(ingreso_del_grupo),
            "VARONES": int((grupo["CH04"] == 1).sum()),
            "MUJERES": int((grupo["CH04"] == 2).sum()),
            "SUMA": round(ingreso_del_grupo.sum(), 0),
            "SUMA_VARONES": round(grupo.loc[grupo["CH04"] == 1, "REAL"].sum(), 0),
            "SUMA_MUJERES": round(grupo.loc[grupo["CH04"] == 2, "REAL"].sum(), 0),
            "MEDIA": round(ingreso_del_grupo.mean(), 0),
            "MEDIA_VARONES": round(grupo.loc[grupo["CH04"] == 1, "REAL"].mean(), 0),
            "MEDIA_MUJERES": round(grupo.loc[grupo["CH04"] == 2, "REAL"].mean(), 0),
            "MEDIANA": round(ingreso_del_grupo.median(), 0),
            "DESVIO": round(ingreso_del_grupo.std(), 0),
            "CV": round(ingreso_del_grupo.std() / ingreso_del_grupo.mean() * 100, 1),          # coef. de variacion (%)
            "ASIMETRIA": round(stats.skew(ingreso_del_grupo), 2),              # Fisher (>0 = cola a derecha)
            "CURTOSIS": round(stats.kurtosis(ingreso_del_grupo, fisher=False), 1),  # 3 = normal, >3 = leptocurtica
            "MIN": round(ingreso_del_grupo.min(), 0),
            "Q1": round(ingreso_del_grupo.quantile(0.25), 0),
            "Q3": round(ingreso_del_grupo.quantile(0.75), 0),
            "MAX": round(ingreso_del_grupo.max(), 0),
        })
    return pd.DataFrame(filas_resumen)


def no_respuesta(panel):
    """Cuenta, por trimestre y aglomerado, cuantos ocupados no declararon su ingreso."""
    ocupados = panel[panel["ESTADO"] == comun.ESTADO_OCUPADO]
    claves_de_agrupacion = ["PERIODO", "PERIODO_NUM", "ANIO", "TRIMESTRE", "AGLOMERADO"]
    filas_resumen = []
    for valores_de_clave, grupo in ocupados.groupby(claves_de_agrupacion):
        periodo, periodo_num, anio, trimestre, aglomerado = valores_de_clave
        # P21 == -9 es el codigo de no respuesta al ingreso de la ocupacion principal.
        cantidad_no_respuesta = (grupo["P21"] == comun.NO_RESPUESTA_INGRESO).sum()
        filas_resumen.append({
            "PERIODO": periodo, "PERIODO_NUM": periodo_num,
            "ANIO": anio, "TRIMESTRE": trimestre,
            "AGLOMERADO": comun.AGLOMERADOS[aglomerado],
            "OCUPADOS": len(grupo), "NO_RESPUESTA": int(cantidad_no_respuesta),
            "PCT_NO_RESPUESTA": round(cantidad_no_respuesta / len(grupo) * 100, 1) if len(grupo) else None,
        })
    return pd.DataFrame(filas_resumen).sort_values(["AGLOMERADO", "PERIODO_NUM"])


def outliers(ingresos):
    """Outliers del ingreso real: metodo IQR (moderados/severos) y z-score."""
    filas_resumen = []
    for aglomerado, grupo in ingresos.groupby("AGLO_NOMBRE"):
        ingreso_del_grupo = grupo["REAL"]
        cuartil_1, cuartil_3 = ingreso_del_grupo.quantile([0.25, 0.75])
        rango_intercuartilico = cuartil_3 - cuartil_1
        # IQR: moderados entre 1.5 y 3 RI; severos a mas de 3 RI
        limite_moderado = cuartil_3 + 1.5 * rango_intercuartilico
        limite_severo = cuartil_3 + 3 * rango_intercuartilico
        moderados = ((ingreso_del_grupo > limite_moderado) & (ingreso_del_grupo <= limite_severo)).sum() \
            + (ingreso_del_grupo < cuartil_1 - 1.5 * rango_intercuartilico).sum()
        severos = (ingreso_del_grupo > limite_severo).sum()
        # z-score (regla de los tres desvios)
        puntajes_z = (ingreso_del_grupo - ingreso_del_grupo.mean()) / ingreso_del_grupo.std()
        outliers_por_zscore = (puntajes_z.abs() > 3).sum()
        total_outliers = moderados + severos
        filas_resumen.append({
            "AGLOMERADO": aglomerado, "N": len(ingreso_del_grupo),
            "MEDIANA": round(ingreso_del_grupo.median(), 0), "Q1": round(cuartil_1, 0), "Q3": round(cuartil_3, 0),
            "RI": round(rango_intercuartilico, 0),
            "OUT_MODERADOS": int(moderados), "OUT_SEVEROS": int(severos),
            "PCT_OUTLIERS": round(total_outliers / len(ingreso_del_grupo) * 100, 1),
            "OUT_ZSCORE": int(outliers_por_zscore),
            "MAX": round(ingreso_del_grupo.max(), 0),
        })
    return pd.DataFrame(filas_resumen)


def main():
    panel = pd.read_parquet(comun.PANEL_PARQUET)
    ingresos_reales = ingreso_principal_real(panel)

    tabla_descriptivas = descriptivas(ingresos_reales)
    tabla_descriptivas.to_csv(os.path.join(comun.TABLAS, "descriptivas.csv"), index=False)
    print("ESTADISTICAS DESCRIPTIVAS DEL INGRESO REAL (" + comun.ETIQUETA_PRECIOS + ")")
    print(tabla_descriptivas.to_string(index=False))

    tabla_no_respuesta = no_respuesta(panel)
    tabla_no_respuesta.to_csv(os.path.join(comun.TABLAS, "no_respuesta.csv"), index=False)
    print("\nNO RESPUESTA A INGRESOS (P21 == -9), por aglomerado:")
    print(tabla_no_respuesta.groupby("AGLOMERADO")["PCT_NO_RESPUESTA"].agg(["min", "max", "mean"]).round(1).to_string())

    tabla_outliers = outliers(ingresos_reales)
    tabla_outliers.to_csv(os.path.join(comun.TABLAS, "outliers.csv"), index=False)
    print("\nOUTLIERS DEL INGRESO REAL (IQR moderados/severos y z-score):")
    print(tabla_outliers.to_string(index=False))
    print(f"\nTablas guardadas en: {comun.TABLAS}")


if __name__ == "__main__":
    main()

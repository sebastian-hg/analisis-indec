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
    """Calcula las tres tasas del INDEC para cada combinacion de trimestre y aglomerado.

    Cada persona pesa segun su ponderador PONDERA, asi que en lugar de contar
    personas sumamos sus ponderadores: eso estima a cuanta gente real representa
    cada grupo. La poblacion activa (PEA) es la suma de ocupados y desocupados.
    """
    filas_de_tasas = []
    columnas_agrupadoras = ["PERIODO", "PERIODO_NUM", "ANIO", "TRIMESTRE", "AGLOMERADO"]
    for valores_clave, grupo in panel.groupby(columnas_agrupadoras):
        periodo, periodo_num, anio, trimestre, aglomerado = valores_clave

        poblacion_total = grupo["PONDERA"].sum()
        ocupados = grupo.loc[grupo["ESTADO"] == comun.ESTADO_OCUPADO, "PONDERA"].sum()
        desocupados = grupo.loc[grupo["ESTADO"] == comun.ESTADO_DESOCUPADO, "PONDERA"].sum()
        poblacion_activa = ocupados + desocupados

        # Los "if" evitan dividir por cero cuando un grupo no tiene poblacion o no
        # tiene activos; en ese caso la tasa queda en None en vez de romper.
        filas_de_tasas.append({
            "PERIODO": periodo, "PERIODO_NUM": periodo_num,
            "ANIO": anio, "TRIMESTRE": trimestre,
            "AGLOMERADO": comun.AGLOMERADOS[aglomerado],
            "TASA_ACTIVIDAD": round(poblacion_activa / poblacion_total * 100, 2) if poblacion_total else None,
            "TASA_EMPLEO": round(ocupados / poblacion_total * 100, 2) if poblacion_total else None,
            "TASA_DESOCUPACION": round(desocupados / poblacion_activa * 100, 2) if poblacion_activa else None,
        })
    return pd.DataFrame(filas_de_tasas).sort_values(["AGLOMERADO", "PERIODO_NUM"]).reset_index(drop=True)


def main():
    panel = pd.read_parquet(comun.PANEL_PARQUET)
    tasas = calcular_tasas(panel)
    tasas.to_csv(os.path.join(comun.TABLAS, "tasas.csv"), index=False)

    # Promedio anual (para tablas del informe): promediamos las tasas de los
    # trimestres de cada anio para tener una tabla mas corta y legible.
    columnas_de_tasas = ["TASA_ACTIVIDAD", "TASA_EMPLEO", "TASA_DESOCUPACION"]
    tasas_anuales = (tasas.groupby(["ANIO", "AGLOMERADO"])[columnas_de_tasas]
                     .mean().round(2).reset_index())
    tasas_anuales.to_csv(os.path.join(comun.TABLAS, "tasas_anual.csv"), index=False)

    # Mostramos cada tasa en pantalla como una tabla de anio (filas) por aglomerado (columnas).
    for columna_tasa, titulo in [("TASA_ACTIVIDAD", "TASA DE ACTIVIDAD (% , prom. anual)"),
                                 ("TASA_EMPLEO", "TASA DE EMPLEO (%)"),
                                 ("TASA_DESOCUPACION", "TASA DE DESOCUPACIÓN (%)")]:
        print(f"\n{titulo}")
        print(tasas_anuales.pivot(index="ANIO", columns="AGLOMERADO",
                                  values=columna_tasa).to_string())

    print(f"\nGuardado: tasas.csv ({len(tasas)} filas trimestrales) y tasas_anual.csv")


if __name__ == "__main__":
    main()

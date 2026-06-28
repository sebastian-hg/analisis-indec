"""
04_multivariado.py - Analisis multivariado del ingreso (objetivo 2).

Cruza el ingreso laboral REAL de los ocupados con sexo, edad, nivel educativo,
calificacion de la tarea (PP04D_COD) y rama de actividad (PP04B_COD), y cuantifica
la asociacion con las medidas que ensena la materia:

  - Categorica vs cuantitativa (ingreso por grupo): coeficiente eta al cuadrado
    (proporcion de varianza del ingreso explicada por el grupo).
  - Dos categoricas (nivel educativo vs condicion de actividad): V de Cramer.
  - Dos cuantitativas (edad vs ingreso): correlacion de Pearson y de Spearman.
  - Evolucion de la brecha de genero por trimestre.

Usa P21 (ingreso de la ocupacion principal) deflactado (columna FACTOR_REAL),
sobre los OCUPADOS con P21 > 0.

Uso:  python src/04_multivariado.py
"""

import os
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, pearsonr, spearmanr
import comun

ESTADO_NOMBRE = {1: "Ocupado", 2: "Desocupado", 3: "Inactivo"}


def preparar(panel):
    """Deja solo a los ocupados con ingreso declarado y les agrega columnas legibles.

    Filtramos a quienes estan ocupados y declararon un ingreso mayor a cero, pasamos
    el ingreso nominal a ingreso real (descontando inflacion con FACTOR_REAL) y
    traducimos los codigos de la EPH (sexo, nivel educativo, edad, calificacion de la
    tarea y rama de actividad) a etiquetas en palabras.
    """
    ocupados_con_ingreso = panel[
        (panel["ESTADO"] == comun.ESTADO_OCUPADO) & (panel["P21"] > 0)].copy()
    ocupados_con_ingreso["P21_REAL"] = ocupados_con_ingreso["P21"] * ocupados_con_ingreso["FACTOR_REAL"]
    ocupados_con_ingreso["SEXO"] = ocupados_con_ingreso["CH04"].map(comun.SEXO)
    ocupados_con_ingreso["NIVEL"] = ocupados_con_ingreso["NIVEL_ED"].map(comun.NIVEL_ED)
    ocupados_con_ingreso["EDAD_GRUPO"] = ocupados_con_ingreso["CH06"].apply(comun.rango_etario)
    ocupados_con_ingreso["CALIFICACION"] = ocupados_con_ingreso["PP04D_COD"].apply(comun.calificacion_tarea)
    ocupados_con_ingreso["SECTOR"] = ocupados_con_ingreso["PP04B_COD"].apply(comun.sector_actividad)
    return ocupados_con_ingreso


def foto(ocupados, anio, dimension, etiqueta, archivo):
    """Calcula y guarda el ingreso real mediano de un anio, abierto por aglomerado y dimension.

    Toma una "foto" de un solo anio: agrupa por aglomerado y por la dimension elegida
    (sexo, nivel educativo, etc.), saca la mediana del ingreso real de cada grupo, la
    guarda en un CSV y la muestra en pantalla como una tabla de doble entrada.
    """
    datos_del_anio = ocupados[ocupados["ANIO"] == anio]
    tabla = (datos_del_anio.groupby(["AGLO_NOMBRE", dimension])["P21_REAL"]
                .median().round(0).reset_index()
                .rename(columns={"P21_REAL": "INGRESO_REAL_MEDIANO"}))
    tabla.to_csv(os.path.join(comun.TABLAS, archivo), index=False)
    print(f"\n--- INGRESO REAL MEDIANO {anio} por {etiqueta} ---")
    print(tabla.pivot(index=dimension, columns="AGLO_NOMBRE",
                      values="INGRESO_REAL_MEDIANO").to_string())


def eta2(datos, grupo, columna_valor="P21_REAL"):
    """Coeficiente eta al cuadrado: proporcion de varianza de la columna explicada por el grupo.

    Compara cuanta de la variabilidad total del ingreso queda explicada por las
    diferencias entre grupos. Es el cociente entre la variabilidad entre los grupos
    (suma de cuadrados entre) y la variabilidad total (suma de cuadrados total).
    """
    media_general = datos[columna_valor].mean()
    suma_cuadrados_total = ((datos[columna_valor] - media_general) ** 2).sum()
    suma_cuadrados_entre = datos.groupby(grupo)[columna_valor].apply(
        lambda valores_del_grupo: len(valores_del_grupo) * (valores_del_grupo.mean() - media_general) ** 2).sum()
    return suma_cuadrados_entre / suma_cuadrados_total if suma_cuadrados_total else 0.0


def cramer_v(contingencia):
    """V de Cramer: mide la fuerza de asociacion entre dos variables categoricas.

    Parte del estadistico chi cuadrado de la tabla de contingencia y lo normaliza por
    el total de casos y la dimension mas chica de la tabla, para que el resultado
    quede entre 0 (sin asociacion) y 1 (asociacion total).
    """
    chi_cuadrado = chi2_contingency(contingencia)[0]
    total_casos = contingencia.values.sum()
    cantidad_filas, cantidad_columnas = contingencia.shape
    dimension_menor = min(cantidad_filas, cantidad_columnas)
    if total_casos and dimension_menor > 1:
        return np.sqrt(chi_cuadrado / (total_casos * (dimension_menor - 1)))
    return 0.0


def brecha_genero(ocupados):
    """Calcula la brecha de ingreso entre mujeres y varones para cada trimestre.

    Para cada periodo y aglomerado saca la mediana del ingreso real de cada sexo, las
    pone una al lado de la otra y calcula cuanto gana de mas o de menos la mujer
    respecto del varon, en porcentaje. Guarda el detalle por trimestre y muestra el
    promedio del periodo por aglomerado.
    """
    mediana_por_sexo = (ocupados.groupby(["PERIODO", "PERIODO_NUM", "AGLO_NOMBRE", "SEXO"])["P21_REAL"]
            .median().reset_index())
    brecha = mediana_por_sexo.pivot_table(index=["PERIODO", "PERIODO_NUM", "AGLO_NOMBRE"],
                       columns="SEXO", values="P21_REAL").reset_index()
    brecha["BRECHA_%"] = ((brecha["Mujer"] / brecha["Varón"] - 1) * 100).round(1)
    brecha = brecha.sort_values(["AGLO_NOMBRE", "PERIODO_NUM"])
    brecha.to_csv(os.path.join(comun.TABLAS, "brecha_genero.csv"), index=False)
    print("\n--- BRECHA DE GÉNERO (promedio del período, %) ---")
    print(brecha.groupby("AGLO_NOMBRE")["BRECHA_%"].mean().round(1).to_string())


def main():
    panel = pd.read_parquet(comun.PANEL_PARQUET)
    ocupados = preparar(panel)
    anio_foto = int(ocupados["ANIO"].max())

    # Fotos del ultimo ano (medianas por grupo)
    foto(ocupados, anio_foto, "SEXO", "sexo", "ing_x_sexo.csv")
    foto(ocupados, anio_foto, "NIVEL", "nivel educativo", "ing_x_educacion.csv")
    foto(ocupados, anio_foto, "EDAD_GRUPO", "rango etario", "ing_x_edad.csv")
    foto(ocupados, anio_foto, "CALIFICACION", "calificación de la tarea", "ing_x_calificacion.csv")
    foto(ocupados, anio_foto, "SECTOR", "rama de actividad", "ing_x_rama.csv")
    brecha_genero(ocupados)

    # --- Medidas de asociacion (ultimo ano) ---
    ocupados_ultimo_anio = ocupados[ocupados["ANIO"] == anio_foto]
    asociacion = {
        "ETA2_EDUCACION": round(eta2(ocupados_ultimo_anio, "NIVEL"), 3),
        "ETA2_CALIFICACION": round(eta2(ocupados_ultimo_anio, "CALIFICACION"), 3),
        "ETA2_SEXO": round(eta2(ocupados_ultimo_anio, "SEXO"), 3),
        "ETA2_EDAD": round(eta2(ocupados_ultimo_anio, "EDAD_GRUPO"), 3),
        "ETA2_RAMA": round(eta2(ocupados_ultimo_anio, "SECTOR"), 3),
    }

    # Edad vs ingreso (dos cuantitativas): Pearson y Spearman
    asociacion["PEARSON_EDAD_ING"] = round(pearsonr(ocupados_ultimo_anio["CH06"], ocupados_ultimo_anio["P21_REAL"])[0], 3)
    asociacion["SPEARMAN_EDAD_ING"] = round(spearmanr(ocupados_ultimo_anio["CH06"], ocupados_ultimo_anio["P21_REAL"])[0], 3)

    # Ingreso de la ocupacion principal vs ingreso total (dos cuantitativas): es la
    # correlacion mas fuerte del heatmap, porque el total incluye al de la ocupacion.
    ingresos = ocupados_ultimo_anio[["P21_REAL", "P47T"]].dropna()
    asociacion["PEARSON_INGRESOS"] = round(pearsonr(ingresos["P21_REAL"], ingresos["P47T"])[0], 3)

    # Nivel educativo (ordinal) vs ingreso. Como es ORDINAL, se analiza de dos formas
    # correctas, sin usar Pearson sobre los codigos crudos:
    #  - Spearman, que usa el ORDEN por rangos (antes reordenamos los codigos a la
    #    jerarquia educativa real, porque el 7 = "Sin instruccion" es el mas bajo).
    #  - Parseando el nivel a una variable CUANTITATIVA (anios de educacion): al tener
    #    distancias reales (anios), ya admite la correlacion de Pearson.
    educacion_e_ingreso = ocupados_ultimo_anio[["NIVEL_ED", "P21_REAL"]].copy()
    educacion_e_ingreso["ORDEN"] = educacion_e_ingreso["NIVEL_ED"].map(comun.NIVEL_ED_ORDEN)
    educacion_e_ingreso["ANIOS_EDUCACION"] = educacion_e_ingreso["NIVEL_ED"].map(comun.ANIOS_EDUCACION)
    educacion_e_ingreso = educacion_e_ingreso.dropna(subset=["ORDEN", "ANIOS_EDUCACION"])
    asociacion["SPEARMAN_EDUC_ING"] = round(spearmanr(educacion_e_ingreso["ORDEN"], educacion_e_ingreso["P21_REAL"])[0], 3)
    asociacion["PEARSON_EDUC_ING"] = round(pearsonr(educacion_e_ingreso["ANIOS_EDUCACION"], educacion_e_ingreso["P21_REAL"])[0], 3)

    # Dos categoricas: nivel educativo x condicion de actividad (V de Cramer)
    personas = panel[(panel["ANIO"] == anio_foto) & (panel["CH06"] >= 15) &
                     (panel["ESTADO"].isin([1, 2, 3]))].copy()
    personas["NIVEL"] = personas["NIVEL_ED"].apply(comun.nivel_agrupado)
    personas["CONDICION"] = personas["ESTADO"].map(ESTADO_NOMBRE)
    orden_niveles = ["Sin instrucción", "Primario", "Secundario", "Superior"]
    contingencia = pd.crosstab(personas["NIVEL"], personas["CONDICION"]).reindex(
        [nivel for nivel in orden_niveles if nivel in personas["NIVEL"].unique()])
    asociacion["CRAMER_EDUC_ESTADO"] = round(cramer_v(contingencia), 3)
    contingencia.to_csv(os.path.join(comun.TABLAS, "contingencia_educ_estado.csv"))

    pd.DataFrame([{**asociacion, "ANIO_FOTO": anio_foto}]).to_csv(
        os.path.join(comun.TABLAS, "multivariado_resumen.csv"), index=False)
    pd.DataFrame([{"ANIO_FOTO": anio_foto}]).to_csv(
        os.path.join(comun.TABLAS, "anio_foto.csv"), index=False)

    print("\n--- MEDIDAS DE ASOCIACIÓN (" + str(anio_foto) + ") ---")
    for nombre_medida, valor_medida in asociacion.items():
        print(f"  {nombre_medida}: {valor_medida}")
    print(f"\nTablas guardadas en {comun.TABLAS}")


if __name__ == "__main__":
    main()

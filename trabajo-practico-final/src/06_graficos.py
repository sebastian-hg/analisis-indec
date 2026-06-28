"""
06_graficos.py - Visualizacion de los indicadores (objetivo 3).

Genera todos los graficos del informe a partir de las tablas calculadas y del
panel. El eje temporal usa PERIODO_NUM (ano + fraccion de trimestre), con marcas
en los anos. Incluye los graficos que ensena la materia segun el tipo de dato:
lineas (evolucion temporal), boxplots (distribucion, outliers y cuantitativa por
grupos), histograma (distribucion / asimetria) y heatmap (matriz de correlacion).

Uso:  python src/06_graficos.py   (despues de 02-05)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import comun

plt.rcParams.update({"figure.figsize": (10, 5.2), "axes.grid": True,
                     "grid.alpha": 0.3, "font.size": 11, "text.color": "black",
                     "axes.labelcolor": "black", "xtick.color": "black",
                     "ytick.color": "black", "axes.titlecolor": "black"})
COLORES = {"Gran Rosario": "#1f77b4", "Gran Tucumán": "#d62728"}
PESOS = mticker.FuncFormatter(lambda valor, _: f"${valor/1000:,.0f}k")
ANIOS_TICK = list(range(min(comun.ANIOS), max(comun.ANIOS) + 1))

# Para los graficos de tasas: cada tasa tiene su color (la columna del CSV, el nombre
# legible y el color). Se usa tanto en el grafico de cada aglomerado como en el unificado.
COLOR_POR_TASA = [("TASA_ACTIVIDAD", "Actividad", "#1f77b4"),
                  ("TASA_EMPLEO", "Empleo", "#2ca02c"),
                  ("TASA_DESOCUPACION", "Desocupación", "#d62728")]

# Orden educativo REAL, de menor a mayor nivel. "Sin instruccion" va PRIMERO porque
# es el nivel mas bajo (los graficos por nivel educativo respetan este orden).
ORDEN_EDUC = ["Sin instrucción", "Primario incompleto", "Primario completo",
              "Secundario incompleto", "Secundario completo",
              "Superior/Univ. incompleto", "Superior/Univ. completo"]
ORDEN_CALIF = ["No calificada", "Operativa", "Técnica", "Profesional"]


def leer_tabla(archivo):
    # Lee una de las tablas CSV ya calculadas, desde la carpeta de tablas.
    return pd.read_csv(os.path.join(comun.TABLAS, archivo))


def guardar_grafico(figura, archivo):
    # Ajusta los margenes, guarda la figura como PNG y la cierra para liberar memoria.
    figura.tight_layout()
    figura.savefig(os.path.join(comun.GRAFICOS, archivo), dpi=120)
    plt.close(figura)
    print(f"  -> {archivo}")


def linea(df, valor, titulo, ylabel, archivo, fmt=None):
    # Grafico de lineas en el tiempo: una linea por aglomerado.
    figura, eje = plt.subplots()
    columna_aglomerado = "AGLOMERADO" if "AGLOMERADO" in df else "AGLO_NOMBRE"
    for nombre, datos_grupo in df.groupby(columna_aglomerado):
        datos_grupo = datos_grupo.sort_values("PERIODO_NUM")
        eje.plot(datos_grupo["PERIODO_NUM"], datos_grupo[valor], marker="o", markersize=4,
                 linewidth=1.8, label=nombre, color=COLORES.get(nombre))
    eje.set_title(titulo, fontweight="bold")
    eje.set_xlabel("Año"); eje.set_ylabel(ylabel); eje.set_xticks(ANIOS_TICK)
    if fmt:
        eje.yaxis.set_major_formatter(fmt)
    eje.legend()
    guardar_grafico(figura, archivo)


def boxplot_grupos(sub, col, orden, titulo, archivo):
    """Boxplot de la cuantitativa por grupos (la materia usa boxplot para esto)."""
    figura, eje = plt.subplots(figsize=(11, 5.5))
    sns.boxplot(data=sub, x=col, y="P21_REAL", hue="AGLO_NOMBRE", order=orden,
                showfliers=False, palette=COLORES, ax=eje)
    eje.set_title(titulo, fontweight="bold")
    eje.set_xlabel(""); eje.set_ylabel("Ingreso real (pesos constantes)")
    eje.yaxis.set_major_formatter(PESOS)
    plt.setp(eje.get_xticklabels(), rotation=20, ha="right")
    eje.legend(title="")
    guardar_grafico(figura, archivo)


def boxplot_distribucion(datos_foto, anio_foto):
    """Boxplot del ingreso real por aglomerado, anotado con los cuartiles (Q1, Q3),
    la mediana, la media y los outliers: muestra de un vistazo toda la informacion del
    analisis univariado (la 'anatomia del boxplot' que vemos en la materia)."""
    nombres = list(comun.AGLOMERADOS.values())
    series = [datos_foto.loc[datos_foto["AGLO_NOMBRE"] == nombre, "P21_REAL"] for nombre in nombres]

    figura, eje = plt.subplots(figsize=(11, 6))
    caja = eje.boxplot(series, tick_labels=nombres, patch_artist=True, widths=0.45, showmeans=True,
                       meanprops=dict(marker="D", markerfacecolor="green", markeredgecolor="green", markersize=8),
                       flierprops=dict(marker="o", markersize=3, markerfacecolor="gray", markeredgecolor="gray", alpha=0.3))
    for parche, nombre in zip(caja["boxes"], nombres):
        parche.set_facecolor(COLORES.get(nombre)); parche.set_alpha(0.45)
    for linea_mediana in caja["medians"]:
        linea_mediana.set_color("black"); linea_mediana.set_linewidth(2)

    # Escribimos el valor de cada medida al lado de su caja.
    for posicion, serie in enumerate(series, start=1):
        cuartil_1, mediana, cuartil_3 = serie.quantile([0.25, 0.5, 0.75])
        media = serie.mean()
        for valor, nombre_medida, color in [(cuartil_3, "Q3", "black"), (media, "Media", "green"),
                                            (mediana, "Mediana", "black"), (cuartil_1, "Q1", "black")]:
            eje.annotate(f"{nombre_medida}: {PESOS(valor, 0)}", xy=(posicion + 0.24, valor),
                         va="center", ha="left", fontsize=8.5, color=color)

    eje.set_ylim(0, 3_000_000)
    eje.set_xlim(0.5, 2.9)
    eje.set_title(f"Distribución del ingreso real por aglomerado ({anio_foto})", fontweight="bold")
    eje.set_ylabel("Ingreso real (pesos constantes)")
    eje.yaxis.set_major_formatter(PESOS)
    guardar_grafico(figura, "20_boxplot_distribucion.png")


def grafico_tasas_de_un_aglomerado(tasas, aglomerado, archivo):
    """Las tres tasas (actividad, empleo, desocupacion) de UN aglomerado, en colores."""
    datos = tasas[tasas["AGLOMERADO"] == aglomerado].sort_values("PERIODO_NUM")
    figura, eje = plt.subplots(figsize=(11, 5))
    for columna, nombre_tasa, color in COLOR_POR_TASA:
        eje.plot(datos["PERIODO_NUM"], datos[columna], color=color, linewidth=1.8,
                 marker="o", markersize=3, label=nombre_tasa)
    eje.set_title(f"Tasas del mercado laboral - {aglomerado} (2016-2025)", fontweight="bold")
    eje.set_xlabel("Año"); eje.set_ylabel("%"); eje.set_xticks(ANIOS_TICK); eje.grid(alpha=0.3)
    eje.legend()
    guardar_grafico(figura, archivo)


def grafico_tasas_unificado(tasas):
    """Las tres tasas de los DOS aglomerados en un solo grafico, para compararlos:
    el color indica la tasa y el estilo de linea, el aglomerado. Las referencias van
    FUERA del grafico, separadas en dos (una para el color y otra para la linea)."""
    from matplotlib.lines import Line2D
    nombres = list(comun.AGLOMERADOS.values())
    estilo_por_aglomerado = {nombres[0]: "-", nombres[1]: "--"}

    # Figura mas compacta y con la fuente un punto mas chica que el resto de los graficos.
    with plt.rc_context({"font.size": 10}):
        figura, eje = plt.subplots(figsize=(11, 5.5))
        for columna, nombre_tasa, color in COLOR_POR_TASA:
            for aglomerado in nombres:
                datos = tasas[tasas["AGLOMERADO"] == aglomerado].sort_values("PERIODO_NUM")
                eje.plot(datos["PERIODO_NUM"], datos[columna], color=color, linewidth=1.6,
                         linestyle=estilo_por_aglomerado[aglomerado])
        eje.set_title("Tasas del mercado laboral: comparación de los dos aglomerados (2016-2025)", fontweight="bold")
        eje.set_xlabel("Año"); eje.set_ylabel("%"); eje.set_xticks(ANIOS_TICK); eje.grid(alpha=0.3)

        # Dos referencias separadas, abajo y fuera del grafico: el COLOR es la tasa y el
        # ESTILO de linea es el aglomerado. Asi no se mezcla todo en una sola leyenda.
        referencia_tasas = [Line2D([0], [0], color=color, lw=2.2, label=nombre_tasa)
                            for _, nombre_tasa, color in COLOR_POR_TASA]
        referencia_aglos = [Line2D([0], [0], color="black", lw=2.2, linestyle=estilo, label=aglomerado)
                            for aglomerado, estilo in estilo_por_aglomerado.items()]
        leyenda_color = eje.legend(handles=referencia_tasas, title="Color = tasa", loc="upper left",
                                   bbox_to_anchor=(0.0, -0.10), ncol=3, frameon=True, fontsize=8)
        eje.add_artist(leyenda_color)
        eje.legend(handles=referencia_aglos, title="Estilo de línea = aglomerado", loc="upper right",
                   bbox_to_anchor=(1.0, -0.10), ncol=2, frameon=True, fontsize=8)

        figura.savefig(os.path.join(comun.GRAFICOS, "01_tasas.png"), dpi=120, bbox_inches="tight")
        plt.close(figura)
    print("  -> 01_tasas.png")


def main():
    print("Generando graficos...")
    tasas = leer_tabla("tasas.csv")
    ingresos = leer_tabla("ingresos_reales.csv")
    anio_foto = int(leer_tabla("anio_foto.csv")["ANIO_FOTO"].iloc[0])

    # --- Tasas del mercado laboral: primero una por aglomerado (las tres tasas juntas)
    # y despues el unificado, que compara los dos aglomerados. ---
    nombres_aglomerados = list(comun.AGLOMERADOS.values())
    grafico_tasas_de_un_aglomerado(tasas, nombres_aglomerados[0], "21_tasas_rosario.png")
    grafico_tasas_de_un_aglomerado(tasas, nombres_aglomerados[1], "22_tasas_tucuman.png")
    grafico_tasas_unificado(tasas)

    # --- Ingreso real ---
    linea(ingresos, "MEDIANA_REAL",
          f"Ingreso mediano real ({comun.ETIQUETA_PRECIOS})", "Pesos constantes",
          "04_ingreso_real.png", PESOS)

    # Dos paneles lado a lado: ingreso nominal a la izquierda y real a la derecha.
    figura, (eje_nominal, eje_real) = plt.subplots(1, 2, figsize=(13, 5.2))
    for aglo, datos_grupo in ingresos.groupby("AGLOMERADO"):
        datos_grupo = datos_grupo.sort_values("PERIODO_NUM")
        eje_nominal.plot(datos_grupo["PERIODO_NUM"], datos_grupo["MEDIANA_NOMINAL"], marker="o", markersize=3, label=aglo, color=COLORES.get(aglo))
        eje_real.plot(datos_grupo["PERIODO_NUM"], datos_grupo["MEDIANA_REAL"], marker="o", markersize=3, label=aglo, color=COLORES.get(aglo))
    eje_nominal.set_title("Ingreso mediano nominal", fontweight="bold")
    eje_real.set_title("Ingreso mediano real (precios constantes)", fontweight="bold")
    for eje in (eje_nominal, eje_real):
        eje.set_xlabel("Año"); eje.set_xticks(ANIOS_TICK); eje.legend(); eje.grid(alpha=0.3)
        eje.yaxis.set_major_formatter(PESOS)
    guardar_grafico(figura, "05_nominal_vs_real.png")

    # --- No respuesta ---
    linea(leer_tabla("no_respuesta.csv"), "PCT_NO_RESPUESTA",
          "No respuesta a ingresos entre ocupados (%)", "%", "06_no_respuesta.png")

    # --- Panel para los graficos de distribucion ---
    panel = pd.read_parquet(comun.PANEL_PARQUET)
    ocupados = panel[(panel["ESTADO"] == comun.ESTADO_OCUPADO) & (panel["P21"] > 0)].copy()
    ocupados["P21_REAL"] = ocupados["P21"] * ocupados["FACTOR_REAL"]
    ocupados["NIVEL"] = ocupados["NIVEL_ED"].map(comun.NIVEL_ED)
    # Parseamos el nivel educativo (ordinal) a anios de educacion (cuantitativa),
    # para poder incluirlo en la matriz de correlacion de Pearson.
    ocupados["ANIOS_EDUC"] = ocupados["NIVEL_ED"].map(comun.ANIOS_EDUCACION)
    ocupados["CALIF"] = ocupados["PP04D_COD"].apply(comun.calificacion_tarea)
    datos_anio_foto = ocupados[ocupados["ANIO"] == anio_foto]

    # --- Boxplot del univariado: cuartiles, mediana, media y outliers en un solo grafico ---
    boxplot_distribucion(datos_anio_foto, anio_foto)

    # --- Cruces: boxplots comparativos (cuantitativa por grupos) ---
    boxplot_grupos(datos_anio_foto, "NIVEL", [nivel for nivel in ORDEN_EDUC if nivel in datos_anio_foto["NIVEL"].unique()],
                   f"Ingreso real por nivel educativo ({anio_foto})", "07_ingreso_educacion.png")
    boxplot_grupos(datos_anio_foto, "CALIF", [calificacion for calificacion in ORDEN_CALIF if calificacion in datos_anio_foto["CALIF"].unique()],
                   f"Ingreso real por calificación de la tarea ({anio_foto})", "08_ingreso_calificacion.png")

    # --- Brecha de genero: ingreso mediano de varones vs mujeres ---
    brecha = leer_tabla("brecha_genero.csv")
    figura, ejes = plt.subplots(1, 2, figsize=(13, 5.2), sharey=True)
    for eje, aglo in zip(ejes, comun.AGLOMERADOS.values()):
        datos_grupo = brecha[brecha["AGLO_NOMBRE"] == aglo].sort_values("PERIODO_NUM")
        eje.plot(datos_grupo["PERIODO_NUM"], datos_grupo["Varón"], marker="o", ms=3, color="#1f77b4", label="Varones")
        eje.plot(datos_grupo["PERIODO_NUM"], datos_grupo["Mujer"], marker="o", ms=3, color="#e377c2", label="Mujeres")
        eje.fill_between(datos_grupo["PERIODO_NUM"], datos_grupo["Mujer"], datos_grupo["Varón"], color="gray", alpha=0.18)
        brecha_promedio = abs(datos_grupo["BRECHA_%"].mean())
        eje.set_title(f"{aglo} (mujeres ~{brecha_promedio:.0f}% menos)", fontweight="bold")
        eje.set_xlabel("Año"); eje.set_xticks(ANIOS_TICK); eje.grid(alpha=0.3)
        eje.yaxis.set_major_formatter(PESOS)
    ejes[0].set_ylabel("Ingreso real mediano"); ejes[0].legend()
    figura.suptitle("Brecha de género: ingreso mediano de varones y mujeres", fontweight="bold")
    guardar_grafico(figura, "09_brecha_genero.png")

    # --- Boxplots de distribucion y outliers ---
    perceptores = panel[panel["P47T"] > 0].copy()
    perceptores["REAL"] = perceptores["P47T"] * perceptores["FACTOR_REAL"]

    figura, eje = plt.subplots(figsize=(8, 5.5))
    datos = [perceptores.loc[perceptores["AGLO_NOMBRE"] == nom, "REAL"] for nom in comun.AGLOMERADOS.values()]
    diagrama_caja = eje.boxplot(datos, tick_labels=list(comun.AGLOMERADOS.values()), patch_artist=True,
                                flierprops=dict(marker="o", markersize=3, markerfacecolor="gray", alpha=0.3))
    for parche, nom in zip(diagrama_caja["boxes"], comun.AGLOMERADOS.values()):
        parche.set_facecolor(COLORES.get(nom)); parche.set_alpha(0.6)
    for med in diagrama_caja["medians"]:
        med.set_color("black")
    eje.set_yscale("log")
    eje.set_title("Distribución del ingreso real y outliers (escala logarítmica)", fontweight="bold")
    eje.set_ylabel("Pesos constantes (log)")
    eje.yaxis.set_major_formatter(PESOS)
    guardar_grafico(figura, "10_boxplot_aglomerado.png")

    figura, eje = plt.subplots(figsize=(11, 5.5))
    anios = sorted(perceptores["ANIO"].unique())
    datos = [perceptores.loc[perceptores["ANIO"] == a, "REAL"] for a in anios]
    diagrama_caja = eje.boxplot(datos, tick_labels=anios, patch_artist=True, showfliers=False)
    for parche in diagrama_caja["boxes"]:
        parche.set_facecolor("#4c72b0"); parche.set_alpha(0.6)
    for med in diagrama_caja["medians"]:
        med.set_color("black")
    eje.set_title("Distribución del ingreso real por año (sin outliers extremos)", fontweight="bold")
    eje.set_xlabel("Año"); eje.set_ylabel("Pesos constantes")
    eje.yaxis.set_major_formatter(PESOS)
    guardar_grafico(figura, "11_boxplot_anual.png")

    # --- Histograma del ingreso (asimetria positiva: media > mediana) ---
    ingresos_anio_foto = perceptores.loc[perceptores["ANIO"] == anio_foto, "REAL"]
    tope = ingresos_anio_foto.quantile(0.97)   # recortamos la cola para que se vea la forma
    figura, eje = plt.subplots(figsize=(9, 5))
    eje.hist(ingresos_anio_foto[ingresos_anio_foto <= tope], bins=40, color="#4c72b0", alpha=0.7, edgecolor="white")
    eje.axvline(ingresos_anio_foto.median(), color="green", linewidth=2, label=f"Mediana ({PESOS(ingresos_anio_foto.median(), 0)})")
    eje.axvline(ingresos_anio_foto.mean(), color="red", linewidth=2, label=f"Media ({PESOS(ingresos_anio_foto.mean(), 0)})")
    eje.set_title(f"Distribución del ingreso real ({anio_foto}): asimetría positiva", fontweight="bold")
    eje.set_xlabel("Ingreso real (pesos constantes)"); eje.set_ylabel("Frecuencia")
    eje.xaxis.set_major_formatter(PESOS)
    eje.legend()
    guardar_grafico(figura, "13_histograma_ingreso.png")

    # --- Heatmap de correlacion entre variables CUANTITATIVAS ---
    # Pearson mide relacion lineal entre cantidades. La edad y los ingresos ya son
    # cuantitativos; el nivel educativo es ordinal, pero lo incluimos parseado a
    # anios de educacion (ANIOS_EDUC), que al tener distancias reales (anios) si es
    # cuantitativo y admite Pearson. NO se usan los codigos crudos de NIVEL_ED.
    variables_numericas = datos_anio_foto[["CH06", "ANIOS_EDUC", "P21_REAL", "P47T"]].rename(columns={
        "CH06": "Edad", "ANIOS_EDUC": "Años de educación",
        "P21_REAL": "Ingreso ocup.", "P47T": "Ingreso total"})
    corr = variables_numericas.corr()
    figura, eje = plt.subplots(figsize=(6.5, 5.5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                vmin=-1, vmax=1, square=True, linewidths=0.5, ax=eje,
                cbar_kws={"label": "Correlación de Pearson"})
    eje.set_title(f"Correlación entre variables ({anio_foto})", fontweight="bold")
    plt.setp(eje.get_xticklabels(), rotation=30, ha="right")
    guardar_grafico(figura, "14_heatmap_correlacion.png")

    # --- Evolucion de medidas de posicion (P25, mediana, P75) ---
    figura, ejes = plt.subplots(1, 2, figsize=(13, 5.2), sharey=True)
    for eje, aglo in zip(ejes, comun.AGLOMERADOS.values()):
        datos_grupo = ingresos[ingresos["AGLOMERADO"] == aglo].sort_values("PERIODO_NUM")
        eje.plot(datos_grupo["PERIODO_NUM"], datos_grupo["P75_REAL"], marker="o", ms=3, color="#9ecae1", label="P75 (cuartil superior)")
        eje.plot(datos_grupo["PERIODO_NUM"], datos_grupo["MEDIANA_REAL"], marker="o", ms=3, color="#1f4e79", label="Mediana (Q2)")
        eje.plot(datos_grupo["PERIODO_NUM"], datos_grupo["P25_REAL"], marker="o", ms=3, color="#9ecae1", label="P25 (cuartil inferior)")
        eje.fill_between(datos_grupo["PERIODO_NUM"], datos_grupo["P25_REAL"], datos_grupo["P75_REAL"], color="#1f4e79", alpha=0.08)
        eje.set_title(aglo, fontweight="bold"); eje.set_xlabel("Año"); eje.set_xticks(ANIOS_TICK)
        eje.yaxis.set_major_formatter(PESOS); eje.grid(alpha=0.3)
    ejes[0].set_ylabel("Ingreso real (pesos constantes)"); ejes[0].legend(fontsize=8)
    figura.suptitle("Evolución de las medidas de posición del ingreso real", fontweight="bold")
    guardar_grafico(figura, "17_posicion_evolucion.png")

    # --- Scatter edad vs ingreso (dos cuantitativas) ---
    resumen_multivariado = leer_tabla("multivariado_resumen.csv").iloc[0]
    muestra = datos_anio_foto.sample(min(3000, len(datos_anio_foto)), random_state=42)
    figura, eje = plt.subplots(figsize=(9, 5))
    eje.scatter(muestra["CH06"], muestra["P21_REAL"], s=8, color="gray", alpha=0.3)
    coeficientes_recta = np.polyfit(datos_anio_foto["CH06"], datos_anio_foto["P21_REAL"], 1)
    extremos_edad = np.array([datos_anio_foto["CH06"].min(), datos_anio_foto["CH06"].max()])
    eje.plot(extremos_edad, coeficientes_recta[0] * extremos_edad + coeficientes_recta[1],
             color="black", linewidth=2, label="Tendencia lineal")
    eje.set_ylim(0, datos_anio_foto["P21_REAL"].quantile(0.97))
    pearson_texto = str(resumen_multivariado["PEARSON_EDAD_ING"]).replace(".", ","); spearman_texto = str(resumen_multivariado["SPEARMAN_EDAD_ING"]).replace(".", ",")
    eje.set_title(f"Edad vs ingreso real ({anio_foto}) - Pearson {pearson_texto}, Spearman {spearman_texto}", fontweight="bold")
    eje.set_xlabel("Edad"); eje.set_ylabel("Ingreso real (pesos constantes)")
    eje.yaxis.set_major_formatter(PESOS); eje.grid(alpha=0.3); eje.legend()
    guardar_grafico(figura, "19_scatter_edad_ingreso.png")

    # --- Mosaico: nivel educativo x condicion de actividad (dos categoricas) ---
    from statsmodels.graphics.mosaicplot import mosaic
    personas = panel[(panel["ANIO"] == anio_foto) & (panel["CH06"] >= 15) &
                     (panel["ESTADO"].isin([1, 2, 3]))].copy()
    personas["NIVEL"] = personas["NIVEL_ED"].apply(comun.nivel_agrupado)
    personas["COND"] = personas["ESTADO"].map({1: "Ocupado", 2: "Desocupado", 3: "Inactivo"})
    orden = [n for n in ["Sin instrucción", "Primario", "Secundario", "Superior"] if n in personas["NIVEL"].unique()]
    personas["NIVEL"] = pd.Categorical(personas["NIVEL"], categories=orden, ordered=True)
    cond_color = {"Ocupado": "#2ca02c", "Desocupado": "#d62728", "Inactivo": "#bcbcbc"}
    figura, eje = plt.subplots(figsize=(10, 6))
    mosaic(personas.sort_values("NIVEL"), ["NIVEL", "COND"], ax=eje, gap=0.015,
           properties=lambda k: {"color": cond_color.get(k[1], "#cccccc")},
           labelizer=lambda k: k[1][:3], title="")
    eje.set_title(f"Nivel educativo y condición de actividad ({anio_foto})", fontweight="bold")
    guardar_grafico(figura, "18_mosaico_educacion_estado.png")

    print(f"\nGraficos guardados en: {comun.GRAFICOS}")


if __name__ == "__main__":
    main()

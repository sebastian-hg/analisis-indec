"""
06_graficos.py - Visualización de los indicadores (objetivo 3).

Genera todos los gráficos del informe a partir de las tablas calculadas y del
panel. El eje temporal usa PERIODO_NUM (año + fracción de trimestre), con marcas
en los años. Incluye boxplots para mostrar la distribución y los outliers.

Uso:  python src/06_graficos.py   (después de 02-05)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import comun

plt.rcParams.update({"figure.figsize": (10, 5.2), "axes.grid": True,
                     "grid.alpha": 0.3, "font.size": 11, "text.color": "black",
                     "axes.labelcolor": "black", "xtick.color": "black",
                     "ytick.color": "black", "axes.titlecolor": "black"})
COLORES = {"Gran Rosario": "#1f77b4", "Gran Tucumán": "#d62728"}
PESOS = mticker.FuncFormatter(lambda x, _: f"${x/1000:,.0f}k")
ANIOS_TICK = list(range(min(comun.ANIOS), max(comun.ANIOS) + 1))

ORDEN_EDUC = ["Primario incompleto", "Primario completo", "Secundario incompleto",
              "Secundario completo", "Superior/Univ. incompleto",
              "Superior/Univ. completo", "Sin instrucción"]
ORDEN_CALIF = ["No calificada", "Operativa", "Técnica", "Profesional"]


def t(archivo):
    return pd.read_csv(os.path.join(comun.TABLAS, archivo))


def guardar(fig, archivo):
    fig.tight_layout()
    fig.savefig(os.path.join(comun.GRAFICOS, archivo), dpi=120)
    plt.close(fig)
    print(f"  -> {archivo}")


def linea(df, valor, titulo, ylabel, archivo, fmt=None):
    """Línea por aglomerado a lo largo del tiempo (x = PERIODO_NUM, ticks por año)."""
    fig, ax = plt.subplots()
    for nombre, g in df.groupby("AGLOMERADO" if "AGLOMERADO" in df else "AGLO_NOMBRE"):
        g = g.sort_values("PERIODO_NUM")
        ax.plot(g["PERIODO_NUM"], g[valor], marker="o", markersize=4,
                linewidth=1.8, label=nombre, color=COLORES.get(nombre))
    ax.set_title(titulo, fontweight="bold")
    ax.set_xlabel("Año"); ax.set_ylabel(ylabel)
    ax.set_xticks(ANIOS_TICK)
    if fmt:
        ax.yaxis.set_major_formatter(fmt)
    ax.legend()
    guardar(fig, archivo)


def barras(pivot, titulo, ylabel, archivo, fmt=None):
    fig, ax = plt.subplots()
    pivot.plot(kind="bar", ax=ax, color=[COLORES.get(c) for c in pivot.columns])
    ax.set_title(titulo, fontweight="bold")
    ax.set_xlabel(""); ax.set_ylabel(ylabel)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    if fmt:
        ax.yaxis.set_major_formatter(fmt)
    ax.legend(title="")
    guardar(fig, archivo)


def main():
    print("Generando gráficos...")
    tasas = t("tasas.csv")
    ingresos = t("ingresos_reales.csv")
    anio_foto = int(t("anio_foto.csv")["ANIO_FOTO"].iloc[0])

    # --- Tasas (líneas trimestrales) ---
    linea(tasas, "TASA_ACTIVIDAD", "Tasa de actividad (trimestral, 2016-2025)", "%", "01_actividad.png")
    linea(tasas, "TASA_EMPLEO", "Tasa de empleo (trimestral, 2016-2025)", "%", "02_empleo.png")
    linea(tasas, "TASA_DESOCUPACION", "Tasa de desocupación (trimestral, 2016-2025)", "%", "03_desocupacion.png")

    # --- Ingreso real ---
    linea(ingresos, "MEDIANA_REAL",
          f"Ingreso mediano real ({comun.ETIQUETA_PRECIOS})", "Pesos constantes",
          "04_ingreso_real.png", PESOS)

    # Nominal vs real
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.2))
    for aglo, g in ingresos.groupby("AGLOMERADO"):
        g = g.sort_values("PERIODO_NUM")
        a1.plot(g["PERIODO_NUM"], g["MEDIANA_NOMINAL"], marker="o", markersize=3, label=aglo, color=COLORES.get(aglo))
        a2.plot(g["PERIODO_NUM"], g["MEDIANA_REAL"], marker="o", markersize=3, label=aglo, color=COLORES.get(aglo))
    a1.set_title("Ingreso mediano nominal", fontweight="bold")
    a2.set_title("Ingreso mediano real (precios constantes)", fontweight="bold")
    for a in (a1, a2):
        a.set_xlabel("Año"); a.set_xticks(ANIOS_TICK); a.legend(); a.grid(alpha=0.3)
        a.yaxis.set_major_formatter(PESOS)
    guardar(fig, "05_nominal_vs_real.png")

    # --- No respuesta ---
    linea(t("no_respuesta.csv"), "PCT_NO_RESPUESTA",
          "No respuesta a ingresos entre ocupados (%)", "%", "06_no_respuesta.png")

    # --- Cruces (barras, último año) ---
    educ = t("ing_x_educacion.csv").pivot(index="NIVEL", columns="AGLO_NOMBRE", values="INGRESO_REAL_MEDIANO")
    educ = educ.reindex([e for e in ORDEN_EDUC if e in educ.index])
    barras(educ, f"Ingreso real mediano por nivel educativo ({anio_foto})",
           "Pesos constantes", "07_ingreso_educacion.png", PESOS)

    calif = t("ing_x_calificacion.csv").pivot(index="CALIFICACION", columns="AGLO_NOMBRE", values="INGRESO_REAL_MEDIANO")
    calif = calif.reindex([c for c in ORDEN_CALIF if c in calif.index])
    barras(calif, f"Ingreso real mediano por calificación de la tarea ({anio_foto})",
           "Pesos constantes", "08_ingreso_calificacion.png", PESOS)

    linea(t("brecha_genero.csv"), "BRECHA_%",
          "Brecha de género (ingreso mediano mujer vs varón, %)", "%", "09_brecha_genero.png")

    # --- Boxplots (distribución y outliers) ---
    panel = pd.read_parquet(comun.PANEL_PARQUET)
    perc = panel[panel["P47T"] > 0].copy()
    perc["REAL"] = perc["P47T"] * perc["FACTOR_REAL"]

    # Boxplot por aglomerado (escala log para ver toda la distribución y los outliers)
    fig, ax = plt.subplots(figsize=(8, 5.5))
    datos = [perc.loc[perc["AGLO_NOMBRE"] == nom, "REAL"] for nom in comun.AGLOMERADOS.values()]
    bp = ax.boxplot(datos, tick_labels=list(comun.AGLOMERADOS.values()), patch_artist=True,
                    flierprops=dict(marker="o", markersize=3, markerfacecolor="gray", alpha=0.3))
    for parche, nom in zip(bp["boxes"], comun.AGLOMERADOS.values()):
        parche.set_facecolor(COLORES.get(nom)); parche.set_alpha(0.6)
    for med in bp["medians"]:
        med.set_color("black")
    ax.set_yscale("log")
    ax.set_title("Distribución del ingreso real y outliers (escala logarítmica)", fontweight="bold")
    ax.set_ylabel("Pesos constantes (log)")
    ax.yaxis.set_major_formatter(PESOS)
    guardar(fig, "10_boxplot_aglomerado.png")

    # Boxplot por año (evolución de la distribución)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    anios = sorted(perc["ANIO"].unique())
    datos = [perc.loc[perc["ANIO"] == a, "REAL"] for a in anios]
    bp = ax.boxplot(datos, tick_labels=anios, patch_artist=True, showfliers=False)
    for parche in bp["boxes"]:
        parche.set_facecolor("#4c72b0"); parche.set_alpha(0.6)
    for med in bp["medians"]:
        med.set_color("black")
    ax.set_title("Distribución del ingreso real por año (sin outliers extremos)", fontweight="bold")
    ax.set_xlabel("Año"); ax.set_ylabel("Pesos constantes")
    ax.yaxis.set_major_formatter(PESOS)
    guardar(fig, "11_boxplot_anual.png")

    print(f"\nGráficos guardados en: {comun.GRAFICOS}")


if __name__ == "__main__":
    main()

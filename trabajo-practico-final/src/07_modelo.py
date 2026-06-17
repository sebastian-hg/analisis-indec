"""
07_modelo.py - Modelo de regresión para imputar la no respuesta a ingresos (objetivo 4).

Estima el ingreso de los ocupados que no declararon P21 (= -9) a partir de sus
características, con una regresión lineal entrenada sobre quienes sí declararon.

  - Variable a predecir: log(P21) (corrige la asimetría del ingreso).
  - Predictores: edad y edad², sexo, nivel educativo, calificación de la tarea,
    aglomerado y PERÍODO (efecto fijo de año-trimestre, que absorbe la inflación).
  - Evaluación: partición train/test (80/20), R² y RMSE.

Uso:  python src/07_modelo.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import comun

PREDICTORES_NUM = ["CH06", "CH06_2"]
PREDICTORES_CAT = ["CH04", "NIVEL_ED", "CALIF", "AGLOMERADO", "PERIODO"]

# Nombres legibles para el gráfico de coeficientes (se excluyen los efectos de período).
ETIQUETAS = {
    "CH04_2": "Mujer (vs varón)", "AGLOMERADO_29": "Gran Tucumán (vs Rosario)",
    "NIVEL_ED_6": "Superior completo", "NIVEL_ED_5": "Superior incompleto",
    "NIVEL_ED_4": "Secundario completo", "NIVEL_ED_3": "Secundario incompleto",
    "NIVEL_ED_2": "Primario completo", "NIVEL_ED_7": "Sin instrucción",
    "CALIF_Profesional": "Tarea profesional", "CALIF_Técnica": "Tarea técnica",
    "CALIF_Operativa": "Tarea operativa", "CH06": "Edad (por año)",
}


def preparar(panel):
    df = panel[panel["ESTADO"] == comun.ESTADO_OCUPADO].copy()
    df["CH06_2"] = df["CH06"] ** 2
    df["CALIF"] = df["PP04D_COD"].apply(comun.calificacion_tarea)
    df = df.dropna(subset=["CH06", "CH04", "NIVEL_ED"])
    declararon = df[df["P21"] > 0].copy()
    no_declararon = df[df["P21"] == comun.NO_RESPUESTA_INGRESO].copy()
    return declararon, no_declararon


def matriz(df, columnas_ref=None):
    X = df[PREDICTORES_NUM + PREDICTORES_CAT].copy()
    X = pd.get_dummies(X, columns=PREDICTORES_CAT, drop_first=True, dtype=float)
    if columnas_ref is not None:
        X = X.reindex(columns=columnas_ref, fill_value=0.0)
    return X


def main():
    panel = pd.read_parquet(comun.PANEL_PARQUET)
    declararon, no_declararon = preparar(panel)

    print(f"Ocupados que DECLARARON ingreso (entrenamiento): {len(declararon):,}")
    print(f"Ocupados que NO declararon (a imputar):          {len(no_declararon):,}")

    X = matriz(declararon)
    y = np.log(declararon["P21"])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = LinearRegression().fit(X_train, y_train)
    y_pred = modelo.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse_log = np.sqrt(mean_squared_error(y_test, y_pred))
    rmse_pesos = np.sqrt(mean_squared_error(np.exp(y_test), np.exp(y_pred)))

    print(f"\n=== RENDIMIENTO (test) ===\n  R² = {r2:.3f} | RMSE log = {rmse_log:.3f} | RMSE $ = {rmse_pesos:,.0f}")

    coefs = (pd.DataFrame({"variable": X.columns, "coef": modelo.coef_})
                .assign(efecto_pct=lambda d: (np.exp(d["coef"]) - 1) * 100)
                .sort_values("coef", ascending=False))
    coefs.to_csv(os.path.join(comun.TABLAS, "modelo_coeficientes.csv"), index=False)

    # --- Gráfico de coeficientes: un solo color, todo en negro, con valores ---
    g = coefs[coefs["variable"].isin(ETIQUETAS)].copy()
    g["nombre"] = g["variable"].map(ETIQUETAS)
    g = g.sort_values("efecto_pct")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(g["nombre"], g["efecto_pct"], color="#4c72b0", edgecolor="black")
    ax.axvline(0, color="black", linewidth=0.9)
    for y_i, v in enumerate(g["efecto_pct"]):
        ax.text(v + (3 if v >= 0 else -3), y_i, f"{v:+.0f}%", va="center",
                ha="left" if v >= 0 else "right", color="black", fontsize=9)
    ax.set_title("Influencia de cada variable sobre el ingreso (%)",
                 fontweight="bold", color="black")
    ax.set_xlabel("Efecto % respecto de la categoría base", color="black")
    ax.tick_params(colors="black")
    ax.margins(x=0.15)
    fig.tight_layout()
    fig.savefig(os.path.join(comun.GRAFICOS, "12_modelo_coeficientes.png"), dpi=120)
    plt.close(fig)
    print("  -> gráfico: 12_modelo_coeficientes.png")

    # --- Imputación ---
    if len(no_declararon):
        X_imp = matriz(no_declararon, columnas_ref=X.columns)
        no_declararon = no_declararon.copy()
        no_declararon["P21_IMPUTADO"] = np.exp(modelo.predict(X_imp))
        no_declararon["P21_IMP_REAL"] = no_declararon["P21_IMPUTADO"] * no_declararon["FACTOR_REAL"]
        no_declararon[["PERIODO", "AGLO_NOMBRE", "CH04", "NIVEL_ED",
                       "P21_IMPUTADO", "P21_IMP_REAL"]].to_csv(
            os.path.join(comun.TABLAS, "ingresos_imputados.csv"), index=False)

        pd.DataFrame([{
            "R2": round(r2, 3), "RMSE_LOG": round(rmse_log, 3), "RMSE_PESOS": round(rmse_pesos, 0),
            "N_TRAIN": len(declararon), "N_IMPUTADO": len(no_declararon),
            "MEDIANA_IMPUTADA_REAL": round(no_declararon["P21_IMP_REAL"].median(), 0),
        }]).to_csv(os.path.join(comun.TABLAS, "modelo_resumen.csv"), index=False)

        print(f"\n=== IMPUTACIÓN ===\n  Imputados: {len(no_declararon):,} | "
              f"mediana real: ${no_declararon['P21_IMP_REAL'].median():,.0f}")


if __name__ == "__main__":
    main()

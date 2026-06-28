"""
07_modelo.py - Modelo de regresion para imputar la no respuesta a ingresos (objetivo 4).

Que hace este archivo, contado como una historia en cinco pasos:

  1. Separa a los ocupados en dos grupos: los que SI declararon su ingreso (con
     ellos vamos a entrenar el modelo) y los que NO lo declararon (a ellos les
     vamos a estimar el ingreso, es decir, imputarlo).
  2. Construye las variables explicativas (las "predictoras") y la variable a
     predecir, que es el ingreso real (en pesos, ya descontada la inflacion).
     Todas las predictoras son CUANTITATIVAS: la edad ya lo es, y las ordinales
     (nivel educativo y calificacion) se parsean a una escala numerica con
     significado (anios de educacion y un puntaje de 1 a 4). El sexo y el
     aglomerado entran como indicadores binarios (0 o 1).
  3. Entrena una regresion lineal por minimos cuadrados usando el 80% de los datos.
  4. Evalua que tan bien predice sobre el 20% restante (R2, RMSE, MAE) y revisa
     los residuos con dos graficos de diagnostico.
  5. Aplica el modelo a los que no declararon, para estimarles el ingreso.

NOTA sobre el logaritmo: el ingreso tiene una distribucion muy asimetrica, de tipo
Pareto (cola larga a la derecha). En vez de transformarlo con logaritmo para
forzarlo a una normal, lo modelamos directamente en pesos y describimos esa forma
asimetrica con la mediana y las medidas de forma (asimetria y curtosis).

Uso:  python src/07_modelo.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import statsmodels.api as sm
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import comun

# --- Variables que usa el modelo (se declaran aca arriba para verlas de un vistazo) ---
# Son todas cuantitativas. Las ordinales (educacion y calificacion) ya vienen
# parseadas a una escala numerica; el sexo y el aglomerado son indicadores 0/1.
# NO se incluye el periodo (el trimestre): no es una caracteristica de la persona.
PREDICTORAS = ["edad", "anios_educacion", "calificacion", "mujer", "tucuman"]

# Traduccion de cada predictora a un texto legible, solo para el grafico de coeficientes.
ETIQUETAS_DE_COEFICIENTES = {
    "edad": "Edad (por año)",
    "anios_educacion": "Educación (por año)",
    "calificacion": "Calificación (por nivel)",
    "mujer": "Mujer (vs varón)",
    "tucuman": "Gran Tucumán (vs Rosario)",
}

# Forzamos que todos los textos de los graficos salgan en negro (mejor para imprimir).
plt.rcParams.update({"text.color": "black", "axes.labelcolor": "black",
                     "xtick.color": "black", "ytick.color": "black",
                     "axes.titlecolor": "black"})


def separar_grupos(panel):
    """Divide a los ocupados en quienes SI declararon ingreso y quienes NO, y de paso
    construye las predictoras cuantitativas de cada persona.

    Por que se hace asi: el modelo aprende la relacion entre las caracteristicas de
    la persona y su ingreso mirando a quienes lo informaron, y despues usa esa
    relacion aprendida para estimar el ingreso de quienes no respondieron.
    """
    ocupados = panel[panel["ESTADO"] == comun.ESTADO_OCUPADO].copy()
    ocupados["P21_REAL"] = ocupados["P21"] * ocupados["FACTOR_REAL"]  # ingreso deflactado (pesos)

    # Predictoras cuantitativas. Las dos ordinales se parsean a una escala numerica
    # con significado: el nivel educativo a anios de educacion y la calificacion de
    # la tarea a un puntaje de 1 (no calificada) a 4 (profesional).
    ocupados["edad"] = ocupados["CH06"]
    ocupados["anios_educacion"] = ocupados["NIVEL_ED"].map(comun.ANIOS_EDUCACION)
    ocupados["calificacion"] = ocupados["PP04D_COD"].apply(comun.calificacion_tarea).map(comun.CALIFICACION_ORDEN)
    # Indicadores binarios (0 o 1) para las dos variables nominales.
    ocupados["mujer"] = (ocupados["CH04"] == 2).astype(float)        # 1 = mujer, 0 = varon
    ocupados["tucuman"] = (ocupados["AGLOMERADO"] == 29).astype(float)  # 1 = Gran Tucuman, 0 = Gran Rosario

    # Descartamos a quienes les falta alguna predictora (por ejemplo, sin nivel
    # educativo, o con una calificacion que no entra en la escala de 1 a 4).
    ocupados = ocupados.dropna(subset=PREDICTORAS)

    declararon_ingreso = ocupados[ocupados["P21"] > 0].copy()
    no_declararon_ingreso = ocupados[ocupados["P21"] == comun.NO_RESPUESTA_INGRESO].copy()
    return declararon_ingreso, no_declararon_ingreso


def construir_predictoras(personas, columnas_del_modelo=None):
    """Selecciona las columnas predictoras (ya numericas) que entran al modelo.

    Como ahora todas las predictoras son cuantitativas, no hace falta convertir nada
    a variables indicadoras: simplemente tomamos las columnas en numeros.
    """
    matriz_predictoras = personas[PREDICTORAS].astype(float).copy()

    # Al imputar, alineamos las columnas exactamente a las que se usaron al entrenar.
    if columnas_del_modelo is not None:
        matriz_predictoras = matriz_predictoras.reindex(columns=columnas_del_modelo, fill_value=0.0)
    return matriz_predictoras


def entrenar(declararon_ingreso):
    """Ajusta la regresion lineal por minimos cuadrados usando el 80% de los datos.

    La variable a predecir es el ingreso REAL en pesos (sin logaritmo). Por que real
    y no nominal: asi el modelo explica el ingreso por las caracteristicas de la
    persona y no por la inflacion de cada periodo. Por que separar entrenamiento y
    prueba: entrenar con unos datos y evaluar con otros distintos evita el
    sobreajuste (que el modelo "memorice" en vez de aprender la relacion general).
    """
    predictoras = construir_predictoras(declararon_ingreso)
    ingreso_real = declararon_ingreso["P21_REAL"]   # en pesos, SIN logaritmo

    (predictoras_entrenamiento, predictoras_prueba,
     ingreso_entrenamiento, ingreso_prueba) = train_test_split(
        predictoras, ingreso_real, test_size=0.2, random_state=0)

    # add_constant agrega el termino independiente (el intercepto). OLS (minimos
    # cuadrados ordinarios) busca los coeficientes que hacen mas chica la suma de los
    # errores al cuadrado entre lo observado y lo predicho.
    modelo = sm.OLS(ingreso_entrenamiento, sm.add_constant(predictoras_entrenamiento)).fit()
    return modelo, predictoras.columns, predictoras_prueba, ingreso_prueba


def evaluar(modelo, predictoras_prueba, ingreso_prueba):
    """Mide que tan bien predice el modelo sobre el 20% de prueba (datos no vistos).

    El R2 dice que proporcion de la variabilidad del ingreso explica el modelo. El
    RMSE y el MAE miden el error promedio de prediccion, directamente en pesos (como
    el modelo ya esta en pesos, no hay que deshacer ninguna transformacion).
    """
    ingreso_predicho = modelo.predict(sm.add_constant(predictoras_prueba, has_constant="add"))
    return {
        "R2": round(modelo.rsquared, 3),               # ajuste sobre los datos de entrenamiento
        "R2_AJUSTADO": round(modelo.rsquared_adj, 3),  # igual, pero penalizando variables de mas
        "R2_TEST": round(r2_score(ingreso_prueba, ingreso_predicho), 3),  # ajuste sobre la prueba
        "RMSE_PESOS": round(np.sqrt(mean_squared_error(ingreso_prueba, ingreso_predicho)), 0),
        "MAE_PESOS": round(mean_absolute_error(ingreso_prueba, ingreso_predicho), 0),
    }


def coeficientes(modelo):
    """Extrae los coeficientes del modelo, ya expresados en pesos.

    Como el modelo esta en pesos, cada coeficiente es directamente el cambio en pesos
    del ingreso por cada unidad de la variable, manteniendo el resto constante (por
    ejemplo, cuantos pesos mas se gana por cada anio de educacion).
    """
    tabla_de_coeficientes = pd.DataFrame({
        "variable": modelo.params.index,
        "coef": modelo.params.values,
        "p_value": modelo.pvalues.values,
    })

    # Sacamos el termino independiente ("const"), que no es una variable explicativa.
    # El efecto en pesos es directamente el coeficiente.
    tabla_de_coeficientes = tabla_de_coeficientes[tabla_de_coeficientes["variable"] != "const"].copy()
    tabla_de_coeficientes["efecto_pesos"] = tabla_de_coeficientes["coef"]
    tabla_de_coeficientes = tabla_de_coeficientes.sort_values("coef", ascending=False)

    tabla_de_coeficientes.to_csv(os.path.join(comun.TABLAS, "modelo_coeficientes.csv"), index=False)
    return tabla_de_coeficientes


def imputar(modelo, no_declararon_ingreso, columnas_del_modelo):
    """Estima el ingreso de quienes no respondieron, en pesos reales.

    Por que: en lugar de descartar esos casos (o rellenarlos con la media, que
    deformaria la distribucion concentrando todo en un solo valor), se predice el
    ingreso de cada persona a partir de sus caracteristicas.
    """
    predictoras_a_imputar = construir_predictoras(no_declararon_ingreso, columnas_del_modelo)
    personas_imputadas = no_declararon_ingreso.copy()

    # El modelo predice el ingreso real en pesos. Como es un modelo lineal en pesos,
    # para algun caso extremo podria dar un valor negativo; un ingreso no puede ser
    # negativo, asi que lo recortamos en 0 como minimo. Despues lo dividimos por el
    # factor para tener tambien el valor en pesos corrientes del periodo.
    personas_imputadas["P21_IMP_REAL"] = modelo.predict(
        sm.add_constant(predictoras_a_imputar, has_constant="add")).clip(lower=0)
    personas_imputadas["P21_IMPUTADO"] = personas_imputadas["P21_IMP_REAL"] / personas_imputadas["FACTOR_REAL"]

    personas_imputadas[["PERIODO", "AGLO_NOMBRE", "CH04", "NIVEL_ED",
                        "P21_IMPUTADO", "P21_IMP_REAL"]].to_csv(
        os.path.join(comun.TABLAS, "ingresos_imputados.csv"), index=False)
    return personas_imputadas


def graficar_coeficientes(tabla_de_coeficientes):
    """Grafico de puntos: cuantos pesos cambia el ingreso por cada variable."""
    datos_grafico = tabla_de_coeficientes[
        tabla_de_coeficientes["variable"].isin(ETIQUETAS_DE_COEFICIENTES)].copy()
    datos_grafico["nombre"] = datos_grafico["variable"].map(ETIQUETAS_DE_COEFICIENTES)
    datos_grafico = datos_grafico.sort_values("efecto_pesos")
    posiciones_verticales = list(range(len(datos_grafico)))

    figura, eje = plt.subplots(figsize=(9, 5.5))
    eje.plot(datos_grafico["efecto_pesos"], posiciones_verticales,
             color="#9bb4cc", linewidth=1.5, zorder=1)   # linea de tendencia
    eje.scatter(datos_grafico["efecto_pesos"], posiciones_verticales,
                color="#1f4e79", s=60, zorder=3)          # puntos
    eje.axvline(0, color="black", linewidth=0.9, linestyle="--")

    # Escribimos el valor del efecto (en pesos) arriba de cada punto.
    for posicion, valor in zip(posiciones_verticales, datos_grafico["efecto_pesos"]):
        etiqueta_pesos = ("+" if valor >= 0 else "-") + "$" + f"{abs(valor):,.0f}".replace(",", ".")
        eje.text(valor, posicion + 0.2, etiqueta_pesos, va="bottom", ha="center",
                 color="black", fontsize=9)

    eje.set_yticks(posiciones_verticales)
    eje.set_yticklabels(datos_grafico["nombre"])
    eje.set_title("Influencia de cada variable sobre el ingreso (en pesos)", fontweight="bold")
    eje.set_xlabel("Cambio en el ingreso real (pesos) por unidad de la variable")
    eje.margins(x=0.2, y=0.15)
    eje.grid(axis="x", alpha=0.3)
    figura.tight_layout()
    figura.savefig(os.path.join(comun.GRAFICOS, "12_modelo_coeficientes.png"), dpi=120)
    plt.close(figura)


def graficar_diagnostico(modelo):
    """Dos graficos para mirar los residuos (los errores) del modelo lineal.

    El QQ-plot compara los residuos con una distribucion normal. Como el ingreso es
    de tipo Pareto (cola larga), es esperable que los residuos se alejen de la normal
    en los extremos. El grafico de residuos contra valores predichos sirve para ver
    si la dispersion del error se mantiene pareja (homocedasticidad).
    """
    residuos = modelo.resid
    valores_predichos = modelo.fittedvalues

    # Tomamos una muestra de hasta 5000 puntos solo para que el grafico no se sature.
    indices_muestra = residuos.sample(min(5000, len(residuos)), random_state=42).index

    # Los dos diagnosticos van en una sola figura, lado a lado, para ahorrar espacio.
    figura, (eje_qq, eje_residuos) = plt.subplots(1, 2, figsize=(13, 5))

    sm.qqplot(residuos.loc[indices_muestra], line="s", markerfacecolor="gray",
              markeredgecolor="gray", alpha=0.4, ax=eje_qq)
    eje_qq.get_lines()[1].set_color("black")
    eje_qq.set_title("QQ-plot de los residuos (normalidad)", fontweight="bold")
    eje_qq.set_xlabel("Cuantiles teoricos")
    eje_qq.set_ylabel("Cuantiles de los residuos")

    eje_residuos.scatter(valores_predichos.loc[indices_muestra], residuos.loc[indices_muestra],
                         s=8, color="gray", alpha=0.4)
    eje_residuos.axhline(0, color="black", linewidth=1)
    eje_residuos.set_title("Residuos vs valores predichos (homocedasticidad)", fontweight="bold")
    eje_residuos.set_xlabel("Valor predicho (ingreso en pesos)")
    eje_residuos.set_ylabel("Residuo")
    eje_residuos.grid(alpha=0.3)

    figura.tight_layout()
    figura.savefig(os.path.join(comun.GRAFICOS, "15_diagnostico.png"), dpi=120)
    plt.close(figura)


def graficar_predicho_vs_real(modelo, predictoras_prueba, ingreso_prueba):
    """Compara, persona por persona del conjunto de prueba, el ingreso REAL (eje x) con
    el que PREDIJO el modelo (eje y). Si el modelo acertara siempre, todos los puntos
    caerian sobre la diagonal roja; cuanto mas cerca de esa linea, mejor la prediccion."""
    ingreso_predicho = modelo.predict(sm.add_constant(predictoras_prueba, has_constant="add"))

    formato_millones = mticker.FuncFormatter(lambda valor, _: f"${valor/1e6:.1f}M")
    tope = 3_000_000   # recortamos la vista al rango donde esta la mayoria
    figura, eje = plt.subplots(figsize=(7.5, 7))
    eje.scatter(ingreso_prueba, ingreso_predicho, s=10, color="#1f4e79", alpha=0.25)
    eje.plot([0, tope], [0, tope], color="red", linewidth=2,
             label="Predicción perfecta (predicho = real)")
    eje.set_xlim(0, tope); eje.set_ylim(0, tope)
    eje.set_xlabel("Ingreso real (pesos)"); eje.set_ylabel("Ingreso predicho por el modelo (pesos)")
    eje.set_title("Ingreso predicho vs. ingreso real (conjunto de prueba)", fontweight="bold")
    eje.xaxis.set_major_formatter(formato_millones)
    eje.yaxis.set_major_formatter(formato_millones)
    eje.legend(); eje.grid(alpha=0.3)
    figura.tight_layout()
    figura.savefig(os.path.join(comun.GRAFICOS, "16_predicho_vs_real.png"), dpi=120)
    plt.close(figura)


def main():
    panel = pd.read_parquet(comun.PANEL_PARQUET)

    # Paso 1. Separar: con quienes entrenamos y a quienes les imputamos el ingreso.
    declararon_ingreso, no_declararon_ingreso = separar_grupos(panel)
    print(f"Declararon ingreso (entrenamiento): {len(declararon_ingreso):,}")
    print(f"No declararon (a imputar):          {len(no_declararon_ingreso):,}")

    # Pasos 2 y 3. Entrenar la regresion sobre el 80% de quienes declararon.
    modelo, columnas_del_modelo, predictoras_prueba, ingreso_prueba = entrenar(declararon_ingreso)

    # Paso 4. Evaluar sobre el 20% de prueba e interpretar los coeficientes.
    metricas = evaluar(modelo, predictoras_prueba, ingreso_prueba)
    print(f"\nR2={metricas['R2']} | R2 ajustado={metricas['R2_AJUSTADO']} | R2 test={metricas['R2_TEST']}")
    print(f"RMSE=${metricas['RMSE_PESOS']:,.0f} | MAE=${metricas['MAE_PESOS']:,.0f}")
    tabla_de_coeficientes = coeficientes(modelo)
    graficar_coeficientes(tabla_de_coeficientes)
    graficar_diagnostico(modelo)
    graficar_predicho_vs_real(modelo, predictoras_prueba, ingreso_prueba)

    # Paso 5. Imputar el ingreso de quienes no respondieron.
    personas_imputadas = imputar(modelo, no_declararon_ingreso, columnas_del_modelo)
    mediana_imputada_real = round(personas_imputadas["P21_IMP_REAL"].median(), 0)

    # Guardamos el resumen de metricas para que el informe (08) lo pueda leer.
    pd.DataFrame([{**metricas, "N_TRAIN": len(declararon_ingreso),
                   "N_IMPUTADO": len(personas_imputadas),
                   "MEDIANA_IMPUTADA_REAL": mediana_imputada_real}]).to_csv(
        os.path.join(comun.TABLAS, "modelo_resumen.csv"), index=False)
    print(f"\nImputados: {len(personas_imputadas):,} | mediana real: ${mediana_imputada_real:,.0f}")


if __name__ == "__main__":
    main()

"""
08_generar_reporte.py - Genera el informe reporte.md a partir de los datos.

Arma el informe automáticamente leyendo las tablas calculadas e insertando los
números, tablas y gráficos. Tono descriptivo/académico: presenta lo que muestran
los datos procesados, sin interpretaciones que excedan la evidencia.

Correr DESPUÉS de los scripts 02 a 07.

Uso:  python src/08_generar_reporte.py
"""

import os
import pandas as pd
import comun


def pesos(x):
    return "$" + f"{x:,.0f}".replace(",", ".")


def millones(x):
    return f"{x/1e6:,.1f}".replace(".", ",") + " M"


def pct(x, dec=1):
    return f"{x:.{dec}f}".replace(".", ",") + "%"


def pct_signo(x, dec=1):
    return f"{x:+.{dec}f}".replace(".", ",") + "%"


def tabla_md(headers, filas):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for f in filas:
        out.append("| " + " | ".join(str(c) for c in f) + " |")
    return "\n".join(out)


def t(archivo):
    return pd.read_csv(os.path.join(comun.TABLAS, archivo))


def coef(coefs, variable):
    fila = coefs[coefs["variable"] == variable]
    return fila["efecto_pct"].iloc[0] if len(fila) else None


def main():
    panel = pd.read_parquet(comun.PANEL_PARQUET)
    tasas_a = t("tasas_anual.csv")
    ing_a = t("ingresos_anual.csv")
    nr = t("no_respuesta.csv")
    outliers = t("outliers.csv")
    calif = t("ing_x_calificacion.csv")
    coefs = t("modelo_coeficientes.csv")
    modelo = t("modelo_resumen.csv").iloc[0]
    anio_foto = int(t("anio_foto.csv")["ANIO_FOTO"].iloc[0])

    nombres = list(comun.AGLOMERADOS.values())
    a1, a2 = nombres
    anio_ini, anio_fin = int(panel["ANIO"].min()), int(panel["ANIO"].max())
    n_trim = panel["PERIODO"].nunique()
    casos = {nom: int((panel["AGLO_NOMBRE"] == nom).sum()) for nom in nombres}

    # Variación del ingreso real (promedio anual) entre el primer y el último año
    var = {}
    for nom in nombres:
        s = ing_a[ing_a["AGLOMERADO"] == nom].sort_values("ANIO")["MEDIANA_REAL"]
        var[nom] = (s.iloc[-1] / s.iloc[0] - 1) * 100
    nr_max = {nom: nr[nr["AGLOMERADO"] == nom]["PCT_NO_RESPUESTA"].max() for nom in nombres}

    ef_mujer = coef(coefs, "CH04_2"); ef_aglo2 = coef(coefs, "AGLOMERADO_29")
    ef_super = coef(coefs, "NIVEL_ED_6"); ef_prof = coef(coefs, "CALIF_Profesional")
    ef_edad = coef(coefs, "CH06")
    G = "output/graficos"

    # Valores para las conclusiones (todo desde los datos)
    brecha = t("brecha_genero.csv")
    brecha_prom = {nom: brecha[brecha["AGLO_NOMBRE"] == nom]["BRECHA_%"].mean() for nom in nombres}
    peak = {}
    for nom in nombres:
        sub = tasas_a[tasas_a["AGLOMERADO"] == nom]
        fila = sub.loc[sub["TASA_DESOCUPACION"].idxmax()]
        peak[nom] = (int(fila["ANIO"]), fila["TASA_DESOCUPACION"])

    # Tablas (promedios anuales, para legibilidad)
    def piv(df, val):
        return df.pivot(index="ANIO", columns="AGLOMERADO", values=val)

    pd_des = piv(tasas_a, "TASA_DESOCUPACION")
    tabla_des = tabla_md(["Año", f"{a1}", f"{a2}"],
                         [[a, pct(pd_des.loc[a, a1]), pct(pd_des.loc[a, a2])] for a in pd_des.index])
    pd_emp = piv(tasas_a, "TASA_EMPLEO")
    tabla_emp = tabla_md(["Año", f"{a1}", f"{a2}"],
                         [[a, pct(pd_emp.loc[a, a1]), pct(pd_emp.loc[a, a2])] for a in pd_emp.index])
    pd_ing = piv(ing_a, "MEDIANA_REAL")
    tabla_ing = tabla_md(["Año", f"{a1}", f"{a2}"],
                         [[a, pesos(pd_ing.loc[a, a1]), pesos(pd_ing.loc[a, a2])] for a in pd_ing.index])

    tabla_out = tabla_md(["Aglomerado", "Mediana", "Q1", "Q3", "Límite sup.", "Outliers", "%", "Máx."],
                         [[r["AGLOMERADO"], pesos(r["MEDIANA"]), pesos(r["Q1"]), pesos(r["Q3"]),
                           pesos(r["LIM_SUP"]), int(r["OUTLIERS"]), pct(r["PCT_OUTLIERS"]),
                           millones(r["MAX"])] for _, r in outliers.iterrows()])

    pc = calif.pivot(index="CALIFICACION", columns="AGLO_NOMBRE", values="INGRESO_REAL_MEDIANO")
    tabla_cal = tabla_md(["Calificación", a1, a2],
                         [[c, pesos(pc.loc[c, a1]), pesos(pc.loc[c, a2])]
                          for c in ["Profesional", "Técnica", "Operativa", "No calificada"] if c in pc.index])

    tabla_mod = tabla_md(["Métrica", "Valor"], [
        ["R² (test)", str(modelo["R2"]).replace(".", ",")],
        ["RMSE (escala log)", str(modelo["RMSE_LOG"]).replace(".", ",")],
        ["Casos de entrenamiento", f"{int(modelo['N_TRAIN']):,}".replace(",", ".")],
        ["Casos imputados", f"{int(modelo['N_IMPUTADO']):,}".replace(",", ".")]])

    md = f"""# Evolución del mercado laboral y los ingresos en {a1} y {a2} ({anio_ini}-{anio_fin})

**Materia:** Introducción al Análisis de Datos - TUP, UTN
**Trabajo práctico final (2º parcial)** · Docente: Luis N. Fernández
**Integrantes:** {comun.INTEGRANTES}
**Fuente:** Encuesta Permanente de Hogares (EPH), INDEC - base individual de aglomerados, todos los trimestres disponibles entre {anio_ini} y {anio_fin}.

---

## 1. Introducción y datos

Se analiza la evolución de la tasa de actividad, la tasa de empleo, la tasa de desocupación y los ingresos de la población en dos aglomerados urbanos, **{a1}** y **{a2}**, a partir de las bases de microdatos individuales de la EPH. Se procesaron **{n_trim} bases trimestrales** entre {anio_ini} y {anio_fin}. El número de registros (personas) analizados es:

{tabla_md(["Código", "Aglomerado", "Registros"],
          [[cod, nom, f"{casos[nom]:,}".replace(",", ".")] for cod, nom in comun.AGLOMERADOS.items()])}

Las tasas se construyen ponderando cada registro por el factor de expansión `PONDERA`. Las tablas de este informe presentan **promedios anuales** de los valores trimestrales; los gráficos muestran la serie trimestral completa.

---

## 2. Metodología

Indicadores del mercado laboral (definiciones del INDEC):

- PEA (población económicamente activa) = ocupados + desocupados.
- Tasa de actividad = PEA / población total.
- Tasa de empleo = ocupados / población total.
- Tasa de desocupación = desocupados / PEA.

La condición de actividad se toma de la variable `ESTADO`. Los ingresos nominales se deflactan con el **IPC Nivel General del INDEC** (promedio de cada trimestre) y se expresan en **{comun.ETIQUETA_PRECIOS}**:

> ingreso real = ingreso nominal x (IPC del período base / IPC del período)

El IPC de 2016 se empalma con el IPC-GBA (igual base, diciembre 2016 = 100), dado que la serie nacional comienza en diciembre de 2016. La no respuesta a los montos de ingreso se identifica con el código **{comun.NO_RESPUESTA_INGRESO}** y se excluye del cálculo de promedios.

---

## 3. Objetivo 1 - Análisis univariado: no respuesta y valores atípicos

### 3.1 No respuesta a ingresos

La proporción de ocupados que no declara su ingreso de la ocupación principal (`P21` = {comun.NO_RESPUESTA_INGRESO}) se presenta por trimestre:

![No respuesta a ingresos]({G}/06_no_respuesta.png)

En {a1} el porcentaje de no respuesta alcanza un máximo de {pct(nr_max[a1])} y en {a2} un máximo de {pct(nr_max[a2])} a lo largo del período analizado.

### 3.2 Valores atípicos (outliers)

Se aplicó el método del rango intercuartílico (IQR) sobre el ingreso real, considerando atípico todo valor por debajo de Q1 - 1,5 x IQR o por encima de Q3 + 1,5 x IQR:

{tabla_out}

La distribución del ingreso y sus valores atípicos se observan en el siguiente diagrama de cajas (escala logarítmica, que permite visualizar el rango completo):

![Distribución del ingreso real por aglomerado]({G}/10_boxplot_aglomerado.png)

El diagrama de cajas por año muestra cómo se desplaza la distribución a lo largo del tiempo:

![Distribución del ingreso real por año]({G}/11_boxplot_anual.png)

---

## 4. Objetivo 2 - Evolución de los indicadores

### 4.1 Tasas del mercado laboral

![Tasa de actividad]({G}/01_actividad.png)

![Tasa de empleo]({G}/02_empleo.png)

Tasa de empleo (promedio anual, %):

{tabla_emp}

![Tasa de desocupación]({G}/03_desocupacion.png)

Tasa de desocupación (promedio anual, %):

{tabla_des}

### 4.2 Ingresos reales

La comparación entre el ingreso nominal y el ingreso real (deflactado) se presenta a continuación:

![Ingreso nominal vs real]({G}/05_nominal_vs_real.png)

![Ingreso real mediano]({G}/04_ingreso_real.png)

Ingreso mediano real (promedio anual, {comun.ETIQUETA_PRECIOS}):

{tabla_ing}

Entre {anio_ini} y {anio_fin}, el ingreso real mediano (promedio anual) varía **{pct_signo(var[a1])}** en {a1} y **{pct_signo(var[a2])}** en {a2}.

### 4.3 Análisis multivariado

Ingreso real mediano según nivel educativo ({anio_foto}):

![Ingreso por nivel educativo]({G}/07_ingreso_educacion.png)

Ingreso real mediano según calificación de la tarea ({anio_foto}, último dígito de `PP04D_COD`):

![Ingreso por calificación]({G}/08_ingreso_calificacion.png)

{tabla_cal}

Brecha de género (cociente entre el ingreso mediano de mujeres y varones), por trimestre:

![Brecha de género]({G}/09_brecha_genero.png)

---

## 5. Objetivo 3 - Visualización

Los gráficos se generaron con `matplotlib` a partir de las tablas calculadas. Se utilizó un color fijo por aglomerado en las series de tiempo y diagramas de cajas para la distribución del ingreso.

---

## 6. Objetivo 4 - Modelo de imputación de la no respuesta a ingresos

Se ajustó un modelo de **regresión lineal** para estimar el ingreso de los ocupados que no declararon `P21`. La variable dependiente es el logaritmo natural del ingreso. Las variables independientes son: edad y edad², sexo, nivel educativo, calificación de la tarea, aglomerado y período (efecto fijo de año-trimestre, que absorbe la variación de precios). El modelo se entrenó sobre el 80% de los ocupados que declararon ingreso y se evaluó sobre el 20% restante.

{tabla_mod}

El coeficiente de determinación R² indica la proporción de la variabilidad del logaritmo del ingreso explicada por el modelo. La influencia de cada variable independiente (en un modelo logarítmico, cada coeficiente equivale aproximadamente a un cambio porcentual del ingreso respecto de la categoría base) se presenta a continuación:

![Coeficientes del modelo]({G}/12_modelo_coeficientes.png)

Según el modelo:

- Nivel educativo superior completo: **{pct_signo(ef_super,0)}** respecto de primario incompleto.
- Tarea profesional: **{pct_signo(ef_prof,0)}** respecto de tarea no calificada.
- Sexo femenino: **{pct_signo(ef_mujer)}** respecto del masculino, a igualdad del resto de las variables.
- Aglomerado {a2}: **{pct_signo(ef_aglo2)}** respecto de {a1}.
- Edad: **{pct_signo(ef_edad)}** por año, con término cuadrático negativo (relación cóncava).

Aplicado a los {int(modelo['N_IMPUTADO']):,} ocupados sin respuesta, el modelo estima una mediana de ingreso real de **{pesos(modelo['MEDIANA_IMPUTADA_REAL'])}**.

---

## 7. Conclusiones

A partir del procesamiento de las bases de la EPH para {a1} y {a2} entre {anio_ini} y {anio_fin} se desprende lo siguiente:

1. Las tres tasas del mercado laboral siguen una trayectoria similar en ambos aglomerados. La tasa de desocupación alcanza su valor anual más alto en {peak[a1][0]} en {a1} ({pct(peak[a1][1])}) y en {peak[a2][0]} en {a2} ({pct(peak[a2][1])}), coincidiendo con el contexto de la pandemia, y luego desciende; las tasas de empleo se recuperan hacia el final del período.

2. El ingreso real mediano evoluciona de manera distinta en cada aglomerado: entre {anio_ini} y {anio_fin} varía **{pct_signo(var[a1])}** en {a1} y **{pct_signo(var[a2])}** en {a2}. La diferencia de poder adquisitivo entre ambos se amplía a lo largo del período.

3. El ingreso presenta diferencias estructurales según las características de las personas: aumenta con el nivel educativo y la calificación de la tarea, y es menor para las mujeres, que ganan en promedio {pct(abs(brecha_prom[a1]))} menos que los varones en {a1} y {pct(abs(brecha_prom[a2]))} menos en {a2}.

4. La no respuesta a ingresos es bastante mayor en {a1} (hasta {pct(nr_max[a1])}) que en {a2} (hasta {pct(nr_max[a2])}), lo que respalda el uso de un modelo de imputación.

5. El modelo de regresión explica el {pct(modelo['R2']*100,0)} de la variabilidad del ingreso y permite cuantificar el efecto de cada variable: nivel educativo superior completo ({pct_signo(ef_super,0)}), tarea profesional ({pct_signo(ef_prof,0)}), sexo femenino ({pct_signo(ef_mujer)}) y aglomerado de residencia ({pct_signo(ef_aglo2)}), siempre respecto de su categoría base.

---

*Análisis realizado con Python (pandas, scikit-learn, matplotlib) sobre las bases de microdatos de la EPH del INDEC.*
"""

    ruta = os.path.join(comun.RAIZ, "reporte.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Informe generado: {ruta} ({len(md.split())} palabras)")


if __name__ == "__main__":
    main()

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


# --- Helpers de formato y de lectura de tablas ---
# Convierten numeros al formato de Argentina (coma decimal, punto de miles) y leen
# las tablas calculadas. Se usan muchas veces dentro del texto del informe.

def pesos(monto):
    # Monto en pesos sin decimales, por ejemplo $1.234.567
    return "$" + f"{monto:,.0f}".replace(",", ".")


def pesos_con_signo(monto):
    # Monto en pesos con signo (+/-), por ejemplo +$44.866
    signo = "+" if monto >= 0 else "-"
    return signo + "$" + f"{abs(monto):,.0f}".replace(",", ".")


def millones(monto):
    # Monto expresado en millones con un decimal, por ejemplo "1,2 M" o "2.543,0 M"
    # (punto para los miles y coma para el decimal, formato argentino).
    texto = f"{monto/1e6:,.1f}"            # ej. "2,543.0" (coma miles, punto decimal)
    return texto.replace(",", "@").replace(".", ",").replace("@", ".") + " M"


def miles(cantidad):
    # Entero con punto de miles, por ejemplo 1.234.567
    return f"{int(cantidad):,}".replace(",", ".")


def numero(valor):
    # Numero suelto con coma decimal (sin separador de miles)
    return str(valor).replace(".", ",")


def porcentaje(valor, decimales=1):
    # Porcentaje con coma decimal, por ejemplo "12,3%"
    return f"{valor:.{decimales}f}".replace(".", ",") + "%"


def porcentaje_con_signo(valor, decimales=1):
    # Igual que porcentaje pero forzando el signo (+/-), util para variaciones
    return f"{valor:+.{decimales}f}".replace(".", ",") + "%"


def tabla_markdown(encabezados, filas):
    # Arma una tabla de markdown a partir de los encabezados y de las filas.
    lineas = ["| " + " | ".join(encabezados) + " |",
              "|" + "|".join(["---"] * len(encabezados)) + "|"]
    for fila in filas:
        lineas.append("| " + " | ".join(str(celda) for celda in fila) + " |")
    return "\n".join(lineas)


def leer_tabla(nombre_archivo):
    # Lee un CSV de la carpeta de tablas calculadas y lo devuelve como DataFrame.
    return pd.read_csv(os.path.join(comun.TABLAS, nombre_archivo))


def efecto_en_pesos(coeficientes, variable):
    # Devuelve el efecto en pesos de una variable del modelo, o None si no esta.
    fila = coeficientes[coeficientes["variable"] == variable]
    return fila["efecto_pesos"].iloc[0] if len(fila) else None


def main():
    # Cargamos el panel ya procesado y cada tabla de resultados que dejaron los
    # scripts previos (02 a 07). El helper leer_tabla() lee un CSV de la carpeta de tablas.
    panel = pd.read_parquet(comun.PANEL_PARQUET)
    tasas_anuales = leer_tabla("tasas_anual.csv")
    ingresos_anuales = leer_tabla("ingresos_anual.csv")
    no_respuesta = leer_tabla("no_respuesta.csv")
    valores_atipicos = leer_tabla("outliers.csv")
    descriptivas = leer_tabla("descriptivas.csv").set_index("AGLOMERADO")
    multivariado = leer_tabla("multivariado_resumen.csv").iloc[0]
    ingreso_por_calificacion = leer_tabla("ing_x_calificacion.csv")
    tabla_coeficientes = leer_tabla("modelo_coeficientes.csv")
    resumen_modelo = leer_tabla("modelo_resumen.csv").iloc[0]
    anio_foto = int(leer_tabla("anio_foto.csv")["ANIO_FOTO"].iloc[0])

    # Nombres de los dos aglomerados (aglomerado_1 y aglomerado_2 se usan mucho dentro de los f-strings).
    nombres_aglomerados = list(comun.AGLOMERADOS.values())
    aglomerado_1, aglomerado_2 = nombres_aglomerados
    anio_ini, anio_fin = int(panel["ANIO"].min()), int(panel["ANIO"].max())
    cantidad_trimestres = panel["PERIODO"].nunique()
    casos = {aglomerado: int((panel["AGLO_NOMBRE"] == aglomerado).sum()) for aglomerado in nombres_aglomerados}

    # Variacion del ingreso real (promedio anual) entre el primer y el ultimo anio.
    variacion_ingreso = {}
    for aglomerado in nombres_aglomerados:
        serie_ingreso_real = ingresos_anuales[ingresos_anuales["AGLOMERADO"] == aglomerado].sort_values("ANIO")["MEDIANA_REAL"]
        variacion_ingreso[aglomerado] = (serie_ingreso_real.iloc[-1] / serie_ingreso_real.iloc[0] - 1) * 100
    no_respuesta_maxima = {aglomerado: no_respuesta[no_respuesta["AGLOMERADO"] == aglomerado]["PCT_NO_RESPUESTA"].max() for aglomerado in nombres_aglomerados}

    # Efecto en pesos de cada variable del modelo, para citarlo en el texto.
    efecto_mujer = efecto_en_pesos(tabla_coeficientes, "mujer"); efecto_aglomerado = efecto_en_pesos(tabla_coeficientes, "tucuman")
    efecto_educacion = efecto_en_pesos(tabla_coeficientes, "anios_educacion"); efecto_calificacion = efecto_en_pesos(tabla_coeficientes, "calificacion")
    efecto_edad = efecto_en_pesos(tabla_coeficientes, "edad")
    carpeta_graficos = "output/graficos"

    # Valores para las conclusiones (todo derivado de los datos).
    brecha_genero = leer_tabla("brecha_genero.csv")
    brecha_prom = {aglomerado: brecha_genero[brecha_genero["AGLO_NOMBRE"] == aglomerado]["BRECHA_%"].mean() for aglomerado in nombres_aglomerados}
    pico_desocupacion = {}
    for aglomerado in nombres_aglomerados:
        tasas_del_aglo = tasas_anuales[tasas_anuales["AGLOMERADO"] == aglomerado]
        fila_pico = tasas_del_aglo.loc[tasas_del_aglo["TASA_DESOCUPACION"].idxmax()]
        pico_desocupacion[aglomerado] = (int(fila_pico["ANIO"]), fila_pico["TASA_DESOCUPACION"])

    # Tablas en markdown con promedios anuales (mas legibles que el detalle trimestral).
    def pivote_anual(tabla, columna):
        return tabla.pivot(index="ANIO", columns="AGLOMERADO", values=columna)

    desocupacion_anual = pivote_anual(tasas_anuales, "TASA_DESOCUPACION")
    tabla_des = tabla_markdown(["Año", f"{aglomerado_1}", f"{aglomerado_2}"],
                         [[anio, porcentaje(desocupacion_anual.loc[anio, aglomerado_1]), porcentaje(desocupacion_anual.loc[anio, aglomerado_2])] for anio in desocupacion_anual.index])
    empleo_anual = pivote_anual(tasas_anuales, "TASA_EMPLEO")
    tabla_emp = tabla_markdown(["Año", f"{aglomerado_1}", f"{aglomerado_2}"],
                         [[anio, porcentaje(empleo_anual.loc[anio, aglomerado_1]), porcentaje(empleo_anual.loc[anio, aglomerado_2])] for anio in empleo_anual.index])
    ingreso_real_anual = pivote_anual(ingresos_anuales, "MEDIANA_REAL")
    tabla_ing = tabla_markdown(["Año", f"{aglomerado_1}", f"{aglomerado_2}"],
                         [[anio, pesos(ingreso_real_anual.loc[anio, aglomerado_1]), pesos(ingreso_real_anual.loc[anio, aglomerado_2])] for anio in ingreso_real_anual.index])

    tabla_desc = tabla_markdown(["Medida", aglomerado_1, aglomerado_2], [
        ["Cantidad de personas", miles(descriptivas.loc[aglomerado_1, "N"]), miles(descriptivas.loc[aglomerado_2, "N"])],
        ["Varones", miles(descriptivas.loc[aglomerado_1, "VARONES"]), miles(descriptivas.loc[aglomerado_2, "VARONES"])],
        ["Mujeres", miles(descriptivas.loc[aglomerado_1, "MUJERES"]), miles(descriptivas.loc[aglomerado_2, "MUJERES"])],
        ["Suma de los ingresos (total)", pesos(descriptivas.loc[aglomerado_1, "SUMA"]), pesos(descriptivas.loc[aglomerado_2, "SUMA"])],
        ["Suma de ingresos de varones", pesos(descriptivas.loc[aglomerado_1, "SUMA_VARONES"]), pesos(descriptivas.loc[aglomerado_2, "SUMA_VARONES"])],
        ["Suma de ingresos de mujeres", pesos(descriptivas.loc[aglomerado_1, "SUMA_MUJERES"]), pesos(descriptivas.loc[aglomerado_2, "SUMA_MUJERES"])],
        ["Media general (suma ÷ personas)", pesos(descriptivas.loc[aglomerado_1, "MEDIA"]), pesos(descriptivas.loc[aglomerado_2, "MEDIA"])],
        ["Promedio de varones", pesos(descriptivas.loc[aglomerado_1, "MEDIA_VARONES"]), pesos(descriptivas.loc[aglomerado_2, "MEDIA_VARONES"])],
        ["Promedio de mujeres", pesos(descriptivas.loc[aglomerado_1, "MEDIA_MUJERES"]), pesos(descriptivas.loc[aglomerado_2, "MEDIA_MUJERES"])],
        ["Mediana", pesos(descriptivas.loc[aglomerado_1, "MEDIANA"]), pesos(descriptivas.loc[aglomerado_2, "MEDIANA"])],
        ["Desvío estándar", pesos(descriptivas.loc[aglomerado_1, "DESVIO"]), pesos(descriptivas.loc[aglomerado_2, "DESVIO"])],
        ["Coef. de variación", porcentaje(descriptivas.loc[aglomerado_1, "CV"]), porcentaje(descriptivas.loc[aglomerado_2, "CV"])],
        ["Asimetría (Fisher)", numero(descriptivas.loc[aglomerado_1, "ASIMETRIA"]), numero(descriptivas.loc[aglomerado_2, "ASIMETRIA"])],
        ["Curtosis", numero(descriptivas.loc[aglomerado_1, "CURTOSIS"]), numero(descriptivas.loc[aglomerado_2, "CURTOSIS"])],
        ["Mínimo", pesos(descriptivas.loc[aglomerado_1, "MIN"]), pesos(descriptivas.loc[aglomerado_2, "MIN"])],
        ["Q1", pesos(descriptivas.loc[aglomerado_1, "Q1"]), pesos(descriptivas.loc[aglomerado_2, "Q1"])],
        ["Q3", pesos(descriptivas.loc[aglomerado_1, "Q3"]), pesos(descriptivas.loc[aglomerado_2, "Q3"])],
        ["Máximo", millones(descriptivas.loc[aglomerado_1, "MAX"]), millones(descriptivas.loc[aglomerado_2, "MAX"])],
    ])

    tabla_out = tabla_markdown(["Aglomerado", "Q1", "Q3", "RI", "Out. moderados",
                          "Out. severos", "% (IQR)", "Out. z-score"],
                         [[fila["AGLOMERADO"], pesos(fila["Q1"]), pesos(fila["Q3"]), pesos(fila["RI"]),
                           int(fila["OUT_MODERADOS"]), int(fila["OUT_SEVEROS"]), porcentaje(fila["PCT_OUTLIERS"]),
                           int(fila["OUT_ZSCORE"])] for _, fila in valores_atipicos.iterrows()])

    ingreso_calif_pivot = ingreso_por_calificacion.pivot(index="CALIFICACION", columns="AGLO_NOMBRE", values="INGRESO_REAL_MEDIANO")
    tabla_cal = tabla_markdown(["Calificación", aglomerado_1, aglomerado_2],
                         [[c, pesos(ingreso_calif_pivot.loc[c, aglomerado_1]), pesos(ingreso_calif_pivot.loc[c, aglomerado_2])]
                          for c in ["Profesional", "Técnica", "Operativa", "No calificada"] if c in ingreso_calif_pivot.index])

    # Tabla de la brecha de genero (ultimo anio): varones, mujeres y diferencia.
    ingreso_por_sexo = leer_tabla("ing_x_sexo.csv").pivot(index="AGLO_NOMBRE", columns="SEXO", values="INGRESO_REAL_MEDIANO")
    tabla_sexo = tabla_markdown(["Aglomerado", "Varones", "Mujeres", "Diferencia", "Brecha"],
                          [[aglomerado, pesos(ingreso_por_sexo.loc[aglomerado, "Varón"]), pesos(ingreso_por_sexo.loc[aglomerado, "Mujer"]),
                            pesos(ingreso_por_sexo.loc[aglomerado, "Varón"] - ingreso_por_sexo.loc[aglomerado, "Mujer"]),
                            porcentaje_con_signo((ingreso_por_sexo.loc[aglomerado, "Mujer"] / ingreso_por_sexo.loc[aglomerado, "Varón"] - 1) * 100)]
                           for aglomerado in nombres_aglomerados])

    tabla_mod = tabla_markdown(["Métrica", "Valor"], [
        ["R²", str(resumen_modelo["R2"]).replace(".", ",")],
        ["R² ajustado", str(resumen_modelo["R2_AJUSTADO"]).replace(".", ",")],
        ["R² en validación (test)", str(resumen_modelo["R2_TEST"]).replace(".", ",")],
        ["RMSE (test, en pesos)", pesos(resumen_modelo["RMSE_PESOS"])],
        ["MAE (test, en pesos)", pesos(resumen_modelo["MAE_PESOS"])],
        ["Casos de entrenamiento", f"{int(resumen_modelo['N_TRAIN']):,}".replace(",", ".")],
        ["Casos imputados", f"{int(resumen_modelo['N_IMPUTADO']):,}".replace(",", ".")]])

    # Estadisticas del ingreso real por nivel educativo (foto del ultimo ano), para
    # acompanar el boxplot con todos los numeros (N, Q1, mediana, Q3, media).
    ocupados_foto = panel[(panel["ESTADO"] == comun.ESTADO_OCUPADO) & (panel["P21"] > 0) &
                          (panel["ANIO"] == anio_foto)].copy()
    ocupados_foto["INGRESO_REAL"] = ocupados_foto["P21"] * ocupados_foto["FACTOR_REAL"]
    ocupados_foto["NIVEL"] = ocupados_foto["NIVEL_ED"].map(comun.NIVEL_ED)
    ocupados_foto["ORDEN_NIVEL"] = ocupados_foto["NIVEL_ED"].map(comun.NIVEL_ED_ORDEN)
    filas_educacion = []
    for orden_nivel, grupo_nivel in ocupados_foto.dropna(subset=["ORDEN_NIVEL"]).groupby("ORDEN_NIVEL"):
        ingreso = grupo_nivel["INGRESO_REAL"]
        filas_educacion.append([grupo_nivel["NIVEL"].iloc[0], miles(len(ingreso)),
                                pesos(ingreso.quantile(0.25)), pesos(ingreso.median()),
                                pesos(ingreso.quantile(0.75)), pesos(ingreso.mean())])
    tabla_educacion = tabla_markdown(["Nivel educativo", "N", "Q1", "Mediana", "Q3", "Media"], filas_educacion)

    md = f"""|   |   |
|--|--|
| **Materia** | Introducción al Análisis de Datos - TUP, UTN |
| **Docente** | Luis N. Fernández |
| **Integrantes** | {comun.INTEGRANTES} |
| **Fuente** | Encuesta Permanente de Hogares (EPH), INDEC. Base individual de aglomerados, todos los trimestres disponibles entre {anio_ini} y {anio_fin}. |

## Trabajo práctico final (recuperatorio 2do parcial)
# Evolución del mercado laboral y los ingresos en {aglomerado_1} y {aglomerado_2} ({anio_ini}-{anio_fin})

---

## Introducción

Para este trabajo tomamos las bases de la Encuesta Permanente de Hogares (EPH) del INDEC y analizamos cómo evolucionaron, entre {anio_ini} y {anio_fin}, la tasa de actividad, la de empleo, la de desocupación y los ingresos en dos aglomerados: **{aglomerado_1}** y **{aglomerado_2}**. Trabajamos con las bases individuales de los {cantidad_trimestres} trimestres disponibles, quedándonos solo con los registros de esos dos aglomerados.

En estos años hubo mucha inflación, así que a los ingresos siempre los miramos en términos **reales**, es decir, descontando la suba de precios, para poder comparar de forma justa un peso de {anio_ini} con uno de {anio_fin}. Para eso ajustamos cada monto con el índice de precios (IPC) del INDEC y los dejamos todos expresados en {comun.ETIQUETA_PRECIOS}. Para las tasas de actividad, empleo y desocupación usamos una variable de la EPH llamada `ESTADO`, que indica si cada persona está ocupada, desocupada o inactiva, y a cada persona la pesamos por su `PONDERA`, que es un número que dice a cuántas personas de la población representa (la EPH es una encuesta a una muestra, así que cada respuesta vale por muchas personas más).

Cada variable la usamos según su tipo. Las **cuantitativas** (el ingreso y la edad) las trabajamos directamente como números. Las **ordinales** (el nivel educativo y la calificación de la tarea) tienen un orden pero no una distancia entre categorías, así que cuando las necesitamos como números les asignamos una escala con sentido: al nivel educativo le ponemos los años de educación que corresponden a cada nivel, y a la calificación un puntaje de 1 a 4. Las **nominales** de dos categorías (el sexo y el aglomerado) las pasamos a 0 y 1; y las nominales de varias categorías sin orden (la condición de actividad y la rama de actividad) no las convertimos en números, sino que medimos su relación con el ingreso con el **eta cuadrado** (que indica qué parte de la variación del ingreso explican los grupos) o la V de Cramer.

---

## 1. Análisis univariado

La variable que exploramos es el **ingreso real de la ocupación principal** de los ocupados, es decir, lo que gana cada persona en su trabajo principal, **ajustado por la inflación**. Vemos cómo se distribuye, qué valores atípicos tiene y cuánta gente no declara cuánto gana.

### 1.1 Exploración y medidas de resumen

Calculamos las medidas de resumen del ingreso real en el último año ({anio_foto}). La tabla muestra primero los **insumos** del cálculo (cuántas personas hay, cuántos varones y mujeres, y la suma de todos los ingresos) y después las medidas que salen de ahí; por ejemplo, la media es esa suma dividida la cantidad de personas:

{tabla_desc}

Lo primero que se nota es que la **media es bastante mayor que la mediana**. Esto pasa porque la distribución del ingreso es **muy asimétrica, con una cola hacia la derecha**: la mayoría gana poco o un valor medio, y una minoría gana mucho, y esos pocos ingresos altos tiran del promedio hacia arriba. El **coeficiente de asimetría de Fisher**, que es positivo, confirma esa cola a la derecha, y la **curtosis** (que mide qué tan pesadas son las colas, o sea cuántos valores extremos hay: en una distribución normal vale 3) está acá muy por encima de 3, lo que confirma que hay muchos más ingresos extremos de lo habitual. El **coeficiente de variación**, cercano al 100%, muestra que los ingresos son muy desiguales. Para leer la forma de la distribución no nos fijamos en un solo dato, sino en cómo se relacionan: la **media frente a la mediana** y la **asimetría** nos dicen hacia qué lado se inclina; la **curtosis**, cuántos valores extremos hay; y el **coeficiente de variación**, qué tan dispares son los ingresos. Por todo esto, para resumir el ingreso preferimos la **mediana**, que no se deja arrastrar por los valores extremos como sí le pasa a la media. El histograma deja ver esa forma:

![Histograma del ingreso real]({carpeta_graficos}/13_histograma_ingreso.png)

### 1.2 Valores atípicos

Para detectar los valores atípicos del ingreso usamos dos métodos:  El primero es el del **rango intercuartílico**: marcamos como atípico moderado a todo valor que esté a más de 1,5 rangos del cuartil 3, y como severo al que esté a más de 3 rangos. El segundo es el **z-score** (la regla de los tres desvíos), que marca como atípico a todo ingreso que esté a más de 3 desvíos de la media.

<img src="{carpeta_graficos}/20_boxplot_distribucion.png" style="max-width:95%; max-height:8.5cm; display:block; margin:8px auto;">

En el boxplot, la **caja** va del primer cuartil (Q1) al tercero (Q3) y contiene al 50% del medio de los ingresos; la **línea negra** es la mediana y el **diamante verde**, la media (que queda más arriba, arrastrada por los ingresos altos); los **bigotes** llegan hasta 1,5 veces el rango entre cuartiles y los **puntos grises** son los outliers, que siguen incluso por encima del tope del gráfico. En números, los dos métodos quedan así:

{tabla_out}

Los dos métodos coinciden en que los atípicos son alrededor del 5% de los casos y están casi todos en la **parte alta** (ingresos muy altos). Acá fue importante distinguir un **outlier** de una **inconsistencia**: un ingreso muy alto es un valor **posible** (hay gente que gana mucho), no un error, así que decidimos **no eliminarlos**; en cambio, un valor imposible (como un ingreso negativo) sí habría que sacarlo. Justamente porque existen estos valores altos es que preferimos la mediana y el rango intercuartílico, que son medidas robustas.

### 1.3 No respuesta a ingresos

Otra cosa que miramos a nivel univariado es la **no respuesta**: ocupados que trabajan pero no dicen cuánto ganan (en la EPH se marca con el código {comun.NO_RESPUESTA_INGRESO}). Nos importa porque quienes no contestan pueden tener un perfil distinto del resto (por ejemplo, los que más ganan), y si los ignoramos podemos sesgar las estimaciones. En nuestros datos la no respuesta llega a un máximo de {porcentaje(no_respuesta_maxima[aglomerado_1])} en {aglomerado_1} y {porcentaje(no_respuesta_maxima[aglomerado_2])} en {aglomerado_2}.

![No respuesta a ingresos]({carpeta_graficos}/06_no_respuesta.png)

Por eso decidimos no descartar esos casos ni completarlos con la media (que deformaría la distribución), sino estimarlos con un modelo, que es lo que hacemos en la parte **3. Modelo de imputación de la no respuesta a ingresos**.

---

## 2. Análisis multivariado

En esta parte cruzamos las variables: primero vemos cómo evolucionaron los indicadores a lo largo del tiempo, y después cómo cambia el ingreso según el nivel educativo, las características del empleo, el sexo y la edad.

### 2.1 Evolución de las tasas del mercado laboral

Primero miramos cada aglomerado por separado, con sus tres tasas juntas, y después los comparamos en un mismo gráfico.

En **{aglomerado_1}**, la actividad y el empleo se mueven casi en paralelo y bastante por encima de la desocupación. En 2020 las tres se quiebran de golpe (caen la actividad y el empleo, y salta la desocupación, que llega a {porcentaje(pico_desocupacion[aglomerado_1][1])} en {pico_desocupacion[aglomerado_1][0]}); después la desocupación baja con fuerza y la actividad y el empleo se recuperan hacia el final del período.

![Tasas del mercado laboral en {aglomerado_1}]({carpeta_graficos}/21_tasas_rosario.png)

En **{aglomerado_2}** el patrón es parecido, pero la desocupación tiene su punto más alto un poco más tarde, en {pico_desocupacion[aglomerado_2][0]} ({porcentaje(pico_desocupacion[aglomerado_2][1])}), y la actividad y el empleo se mueven en valores similares, en general apenas por debajo de los de {aglomerado_1}.

![Tasas del mercado laboral en {aglomerado_2}]({carpeta_graficos}/22_tasas_tucuman.png)

Para compararlos directamente pusimos las tres tasas de los dos aglomerados en un mismo gráfico. El **color** indica la tasa (actividad, empleo y desocupación) y el **estilo de línea**, el aglomerado (línea llena para {aglomerado_1} y punteada para {aglomerado_2}); las referencias están abajo del gráfico.

<img src="{carpeta_graficos}/01_tasas.png" style="max-width:88%; max-height:8.5cm; display:block; margin:8px auto;">

Así se ve todo de una: las dos ciudades tienen una actividad y un empleo bastante parecidos, y la diferencia más marcada está en la desocupación, sobre todo en el momento del pico (2020 en {aglomerado_1}, 2021 en {aglomerado_2}). La tasa de desocupación, año a año, fue:

{tabla_des}

### 2.2 Evolución del ingreso real: tendencia central y posición

Para los ingresos, comparar el **nominal** con el **real** es la mejor forma de ver el efecto de la inflación: el nominal sube siempre porque suben los precios, pero el real muestra qué pasó de verdad con el poder de compra.

![Ingreso nominal vs real]({carpeta_graficos}/05_nominal_vs_real.png)

Entre {anio_ini} y {anio_fin}, el ingreso real mediano (promedio anual) varió **{porcentaje_con_signo(variacion_ingreso[aglomerado_1])}** en {aglomerado_1} y **{porcentaje_con_signo(variacion_ingreso[aglomerado_2])}** en {aglomerado_2}. Más allá del número, lo que se ve es una **pérdida de poder de compra** en los años de más inflación y una recuperación parcial hacia el final.

{tabla_ing}

Además de la mediana, seguimos las **medidas de posición** (los cuartiles). La banda entre el primer cuartil (P25) y el tercero (P75) contiene al 50% del medio de los ingresos, y su ancho muestra qué tan dispares son:

![Evolución de las medidas de posición]({carpeta_graficos}/17_posicion_evolucion.png)

### 2.3 El ingreso según el nivel educativo

Cuando cruzamos el ingreso con el **nivel educativo** vemos una relación clara: a mayor nivel, mayor ingreso mediano (y también más dispersión dentro de cada grupo):

<img src="{carpeta_graficos}/07_ingreso_educacion.png" style="max-width:95%; max-height:8.5cm; display:block; margin:8px auto;">

El boxplot compara los dos aglomerados en cada nivel educativo. La tabla siguiente resume los números por nivel (juntando los dos aglomerados): la cantidad de personas (N), el primer cuartil (Q1), la mediana, el tercer cuartil (Q3) y la media.

{tabla_educacion}

Para ponerle un número a esa asociación usamos el coeficiente **eta cuadrado**, que mide qué parte de la variación del ingreso explica cada variable: el nivel educativo explica el {porcentaje(multivariado['ETA2_EDUCACION']*100)} de la variabilidad del ingreso.

### 2.4 El ingreso según las características del empleo

La consigna nos pedía mirar también las características del empleo (`PP04B_COD`, la rama de actividad, y `PP04D_COD`, la calificación de la tarea). La **calificación** es la que más pesa: explica el {porcentaje(multivariado['ETA2_CALIFICACION']*100)} de la variabilidad del ingreso, todavía un poco más que el nivel educativo. El ingreso mediano por calificación es:

{tabla_cal}

La **rama de actividad** también muestra diferencias, aunque más chicas (eta cuadrado de {numero(multivariado['ETA2_RAMA'])}).

### 2.5 El ingreso según el sexo y la edad

Comparando varones y mujeres aparece una **brecha de género** que se mantiene en todo el período: las mujeres ganan en promedio {porcentaje(abs(brecha_prom[aglomerado_1]))} menos en {aglomerado_1} y {porcentaje(abs(brecha_prom[aglomerado_2]))} menos en {aglomerado_2}. En el último año la diferencia fue:

{tabla_sexo}

El **mapa de calor** se lee así: cada celda es la **correlación de Pearson** entre dos variables, que va de **-1 a 1** (cerca de 1, las dos suben juntas; cerca de 0, no hay relación lineal). El color lo acompaña: cuanto más rojo, más cerca de 1. Ordenando de la más fuerte a la más débil:

- La relación **más fuerte** es entre el **ingreso de la ocupación principal y el ingreso total** ({numero(multivariado['PEARSON_INGRESOS'])}, casi 1). Es esperable, porque el ingreso total **incluye** al de la ocupación principal: quien gana más en su trabajo, gana más en total.
- Después viene **años de educación con el ingreso** ({numero(multivariado['PEARSON_EDUC_ING'])}): una relación positiva y moderada (a más educación, más ingreso).
- La más **débil** es la de la **edad con el ingreso** ({numero(multivariado['PEARSON_EDAD_ING'])}), justamente porque esa relación no es una recta.

![Matriz de correlación]({carpeta_graficos}/14_heatmap_correlacion.png)

### 2.6 Qué medida usamos en cada cruce

Un detalle que cuidamos fue usar en cada cruce la medida que corresponde al tipo de las variables:

| Cruce | Tipos | Medida | Valor |
|--|--|--|--|
| Edad con ingreso | cuantitativa con cuantitativa | Pearson y Spearman | {numero(multivariado['PEARSON_EDAD_ING'])} y {numero(multivariado['SPEARMAN_EDAD_ING'])} |
| Nivel educativo con ingreso | ordinal (pasada a años de educación) | eta², Spearman y Pearson | {porcentaje(multivariado['ETA2_EDUCACION']*100)}, {numero(multivariado['SPEARMAN_EDUC_ING'])} y {numero(multivariado['PEARSON_EDUC_ING'])} |
| Calificación con ingreso | ordinal con cuantitativa | eta² | {porcentaje(multivariado['ETA2_CALIFICACION']*100)} |
| Sexo con ingreso | nominal con cuantitativa | eta² | {porcentaje(multivariado['ETA2_SEXO']*100)} |
| Nivel educativo con condición de actividad | nominal con nominal | V de Cramer | {numero(multivariado['CRAMER_EDUC_ESTADO'])} |

La idea es simple: **Pearson** solo entre variables cuantitativas; para una categórica con una cuantitativa, **eta cuadrado**; y entre dos categóricas, la **V de Cramer**. Cuando una variable es ordinal, como el nivel educativo, además del eta cuadrado la podemos pasar a una escala numérica con sentido (años de educación) y ahí sí calcular Pearson; lo que no corresponde es usar Pearson sobre los códigos crudos.

---

## 3. Modelo de imputación de la no respuesta a ingresos

Para completar la no respuesta a los ingresos armamos un modelo de **regresión lineal múltiple**. Los coeficientes se calculan por el método de **mínimos cuadrados** (OLS, *Ordinary Least Squares*): elige los valores que hacen más chica la **suma de los errores al cuadrado**, es decir, la combinación que mejor se ajusta al conjunto de los datos. La idea es aprender la relación entre el ingreso y las características de cada persona usando a quienes sí declararon su ingreso, y después usar esa relación para estimar el de quienes no respondieron.

La variable que queremos predecir es el **ingreso real, en pesos**. Lo dejamos en pesos (su escala original) para que cada coeficiente se interprete directamente en pesos. Las variables explicativas son todas numéricas: la **edad**, los **años de educación** (el nivel educativo pasado a una escala numérica) y la **calificación de la tarea** (un puntaje de 1 a 4), más dos indicadores 0/1 para el **sexo** y el **aglomerado**. Para evaluar el modelo separamos los datos en dos partes: entrenamos con el 80% y probamos con el 20% que el modelo no vio, así medimos si de verdad sirve para casos nuevos y no solo memoriza los datos.

{tabla_mod}

El **R²** nos dice qué parte de la variabilidad del ingreso explica el modelo. Nos dio {numero(resumen_modelo['R2'])} en entrenamiento y {numero(resumen_modelo['R2_TEST'])} en la prueba: son parecidos, y el de prueba un poco más bajo, que es lo esperable, porque el modelo siempre ajusta un poco mejor sobre los datos con los que se entrenó. Que sean tan parecidos nos dice que el modelo **generaliza bien** y no está sobreajustado. El **RMSE** y el **MAE** miden cuánto se equivoca el modelo, en pesos. El **MAE** (error medio absoluto) es el promedio de lo que le erra a cada persona, sin importar si predice de más o de menos: dio {pesos(resumen_modelo['MAE_PESOS'])}, así que en promedio el modelo se aparta del ingreso real en esa cifra. El **RMSE** (raíz del error cuadrático medio) es parecido, pero antes de promediar eleva cada error al cuadrado, así que les da más peso a los errores grandes; por eso queda más alto ({pesos(resumen_modelo['RMSE_PESOS'])}) y nos avisa de que hay algunas predicciones que se van bastante lejos.

Otra forma de ver qué tan bien predice es comparar, para cada persona del conjunto de prueba, el ingreso que el modelo estimó contra el que realmente tenía. Si el modelo fuera perfecto, todos los puntos caerían sobre la diagonal roja:

![Ingreso predicho vs. ingreso real]({carpeta_graficos}/16_predicho_vs_real.png)

La nube de puntos sigue la diagonal pero con bastante dispersión: el modelo acierta la tendencia general, aunque le cuesta con los ingresos más altos (los predice más bajos de lo que son). Eso es coherente con que el RMSE sea bastante mayor que el MAE.

Como el modelo está en pesos, cada coeficiente nos dice cuántos pesos cambia el ingreso por cada unidad de la variable, dejando el resto fijo:

![Coeficientes del modelo]({carpeta_graficos}/12_modelo_coeficientes.png)

- Cada **año de educación** suma {pesos_con_signo(efecto_educacion)} al ingreso.
- Cada **nivel de calificación** de la tarea suma {pesos_con_signo(efecto_calificacion)}.
- Cada **año de edad** suma {pesos_con_signo(efecto_edad)}.
- Ser **mujer** implica {pesos_con_signo(efecto_mujer)} respecto de un varón.
- Vivir en **{aglomerado_2}** implica {pesos_con_signo(efecto_aglomerado)} respecto de **{aglomerado_1}**.

Estos resultados van en la misma línea que el análisis multivariado: la educación y la calificación son lo que más sube el ingreso, y siguen apareciendo la brecha de género y la diferencia entre aglomerados.

### 3.1 Diagnóstico del modelo

Para revisar que el modelo sea válido miramos los residuos (los errores). El **QQ-plot** compara los residuos con una distribución normal (si caen sobre la diagonal, son aproximadamente normales) y el gráfico de **residuos contra valores predichos** sirve para ver que el error no tenga un patrón y se mantenga parejo. Como hay algunos ingresos muy altos, es esperable que en los extremos los residuos se aparten un poco de la normal.

![Diagnóstico del modelo: QQ-plot y residuos vs predichos]({carpeta_graficos}/15_diagnostico.png)

### 3.2 Imputación

Con el modelo ya entrenado estimamos el ingreso de los {miles(resumen_modelo['N_IMPUTADO'])} ocupados que no habían respondido, y nos dio una mediana imputada de **{pesos(resumen_modelo['MEDIANA_IMPUTADA_REAL'])}**. Completar la no respuesta de esta forma, según las características de cada persona, es mejor que imputar con la media, que metería a todos en un mismo valor y deformaría la distribución.

---

## Conclusiones

Analizando la EPH entre {anio_ini} y {anio_fin} para {aglomerado_1} y {aglomerado_2} pudimos seguir cómo se movieron el mercado laboral y los ingresos en un período difícil, con mucha inflación y la pandemia de 2020 de por medio. Las tasas de actividad, empleo y desocupación muestran ese impacto, con el quiebre de 2020 bien marcado.

En los ingresos, mirarlos en términos reales nos dejó ver la pérdida de poder de compra, que fue distinta entre los dos aglomerados. Vimos que el ingreso es muy desigual y asimétrico, por eso lo resumimos con la mediana y los cuartiles.

En el análisis multivariado, lo que más se asocia a mayores ingresos es el nivel educativo y la calificación de la tarea, y también quedó clara una brecha de género que se sostiene en el tiempo. Para cada cruce usamos la medida que correspondía al tipo de variable.

Por último, el modelo de regresión nos permitió imputar la no respuesta a partir de las características de cada persona, con un rendimiento razonable sobre datos nuevos y coeficientes fáciles de interpretar, en pesos.

---

## Bibliografía

- INDEC. *Encuesta Permanente de Hogares (EPH)*. Bases de microdatos y diseño de registro. Instituto Nacional de Estadística y Censos.
- INDEC. *Índice de Precios al Consumidor (IPC), Nivel General*. Serie de tiempo (apis.datos.gob.ar).
- Chan, D., Badano, C. I. y Rey, A. A. (2019). *Análisis inteligente de datos con lenguaje R*. edUTecNe, Universidad Tecnológica Nacional.
- McKinney, W. *Python para el análisis de datos*.
- Material de cátedra: Introducción al Análisis de Datos (UTN), unidades de visualización y de modelado predictivo.

---
"""

    ruta = os.path.join(comun.RAIZ, "reporte.md")
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(md)
    print(f"Informe generado: {ruta} ({len(md.split())} palabras)")


if __name__ == "__main__":
    main()

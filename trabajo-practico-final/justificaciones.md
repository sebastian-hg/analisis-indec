# Justificaciones del trabajo, con referencia al material de la materia

> Material de estudio para la defensa. Cada decisión del trabajo aparece con la
> cita exacta de dónde se justifica en el material de la cursada.

## Aclaración importante sobre las fuentes

- La **teoría de regresión lineal** (modelo, supuestos, R², diagnóstico) viene de las
  slides de la **clase 6 (`Regresión.pptx`)**, que citan a **Szretter**. El libro
  obligatorio `AID 2022.pdf` (Chan, Badano y Rey, edUTecNe-UTN, 2019) desarrolla la
  regresión **logística**, no la lineal; sí aporta el QQ-plot, los supuestos y la
  transformación logarítmica. Si preguntan "¿de dónde sacaron la regresión lineal?",
  la respuesta es la **clase 6**, no el libro.

---

## A. Decisiones de visualización

| Decisión | Justificación (archivo / ubicación) |
|--|--|
| Usar **gráfico de líneas** para la evolución de tasas e ingresos en el tiempo | `guia_visual_graficos.docx`, secc. 12 ("evolución temporal"); `Presentación clase 5.pdf`, slide 10. |
| Usar **boxplot** para ver distribución y **outliers** del ingreso | `guia_visual_graficos.docx`, secc. 4 ("el gráfico más importante… identificar cada elemento: mediana, Q1, Q3, RIC, bigotes, outliers"); `Presentación clase 5.pdf`, slide 11. |
| Usar **boxplots comparativos** para el ingreso por nivel educativo / calificación | `guia_visual_graficos.docx`, secc. 5 ("variable cuantitativa por grupos… un boxplot por nivel educativo, las medianas crecen con el nivel"). Es exactamente nuestro cruce. |
| Usar **histograma** para mostrar la **asimetría positiva** del ingreso | `guia_visual_graficos.docx`, secc. 2 ("ingresos: asimetría positiva, media > mediana"); `Presentación clase 5.pdf`, slide 7. |
| Usar **heatmap** para la **matriz de correlación** | `guia_visual_graficos.docx`, secc. 11; `Presentación clase 5.pdf`, slide 15; `Ejercicios clase 5.pdf` lo pide explícitamente ("graficar correlaciones con el gráfico correspondiente"). |
| Acompañar todo gráfico con **título y etiquetas de ejes** | `Presentación clase 5.pdf`, slide 5 (funciones `title()`, `xlabel()`, `ylabel()`, `legend()`). |

## B. Decisiones sobre el ingreso

| Decisión | Justificación (archivo / ubicación) |
|--|--|
| Reportar la **mediana** y no la media del ingreso | `guia_visual_graficos.docx`, secc. 2 ("conviene reportar la MEDIANA, que es más representativa" en distribuciones asimétricas como ingresos). |
| Detectar **outliers con el método IQR** (Q3 + 1,5·RIC) | `guia_visual_graficos.docx`, secc. 4 ("bigote superior = Q3 + 1,5·RIC; puntos fuera = outliers"). |
| Distinguir **outliers de inconsistencias** | `guia_visual_graficos.docx`, secc. 4 y 10 ("outliers son posibles y se inspeccionan; inconsistencias son imposibles y se eliminan"). |

## B2. Estadística descriptiva univariada (objetivo 1)

| Medida / decisión | Justificación (archivo / página) |
|--|--|
| Clasificación de variables (categórica, ordinal, cuantitativa) | `AID 2022.pdf` pág. 13-14 (secc. 2.1, niveles de medición). |
| Media vs mediana (la media no es robusta; la mediana sí) | `AID 2022.pdf` pág. 17-18 (la media es sensible a extremos; la mediana es robusta). |
| Desvío estándar y **coeficiente de variación (CV)** | `AID 2022.pdf` pág. 20-21 (varianza, desvío, CV = dispersión relativa). |
| Rango intercuartílico (RI) | `AID 2022.pdf` pág. 21. |
| **Asimetría de Fisher** (>0 = cola a derecha) | `AID 2022.pdf` pág. 22-23 (asimetría positiva: Moda < Mediana < Media). |
| **Curtosis** (k > 3 = leptocúrtica, colas pesadas) | `AID 2022.pdf` pág. 24 (k ≈ 3 en la normal). |
| Relación media-mediana según la asimetría | `AID 2022.pdf` pág. 23 (Figuras 2.4-2.6). |
| Outliers **moderados** (1,5-3·RI) y **severos** (>3·RI) | `AID 2022.pdf` pág. 36 (boxplot de Tukey). |
| Outliers por **z-score** (regla de los tres desvíos, \|z\|>3) | `AID 2022.pdf` pág. 38; colab `limpieza_de_datos.py` (`zscore`). |
| No eliminar outliers que son posibles (no son inconsistencias) | `AID 2022.pdf` pág. 36 ("deben inspeccionarse… no eliminarse si son posibles"); `guia_visual_graficos.docx` secc. 4 y 10. |
| Tratar la no respuesta como dato faltante; no imputar con la media | `guia_visual_graficos.docx` secc. 18; colab `limpieza_de_datos.py` (`dropna`/`fillna`); material de la clase 4 (limpieza de datos). |

## B3. Análisis multivariado y medidas de asociación (objetivo 2)

| Cruce / medida | Justificación (archivo / página) |
|--|--|
| Ingreso (cuantitativo) por grupos: boxplots comparativos | `guia_visual_graficos.docx` secc. 5; `Presentación clase 5.pdf` slide 11. |
| Asociación categórica-cuantitativa: coeficiente **eta** (eta²) / ANOVA | `guia_visual_graficos.docx` secc. 5 ("para cuantificar la asociación entre una categórica y una cuantitativa se usa T de Student, ANOVA o coeficiente eta"). |
| Evolución de **medidas de posición** (cuartiles P25 / P75) | `AID 2022.pdf` pág. 19-20 (cuantiles, cuartiles, percentiles); lo pide la consigna del TP. |
| Relación entre dos cuantitativas (edad-ingreso): **Pearson y Spearman** | `guia_visual_graficos.docx` secc. 8 (Pearson) y secc. 9 (Spearman cuando la relación no es lineal). |
| Cruce de dos categóricas: **gráfico de mosaicos** | `guia_visual_graficos.docx` secc. 14; `AID 2022.pdf` secc. 2.3 (información multivariada), pág. 41 en adelante. |
| Asociación entre dos categóricas: **V de Cramer** | `guia_visual_graficos.docx` secc. 14 ("para cuantificar la asociación entre dos variables categóricas se usa V de Cramer"). |

## C. Decisiones del modelo de regresión (objetivo 4)

| Decisión | Justificación (archivo / ubicación) |
|--|--|
| Usar **regresión lineal múltiple** | `Regresión.pptx`, slides 13-16 (modelo múltiple, cita Szretter pág. 113); `Ejemplo regresion.R` (`lm(mpg ~ .)`). |
| Estimar por **mínimos cuadrados (OLS)** | `Regresión.pptx`, slide 8 ("se calculan usando el método de mínimos cuadrados"). |
| Predecir el **logaritmo** del ingreso (variable asimétrica) | `guia_visual_graficos.docx`, secc. 2 ("aplicar una transformación logarítmica para acercar a una normal"); `AID 2022.pdf` pág. 254-255 (transformaciones de potencia / Box-Cox: cuando σ ∝ μ, transformar con log). |
| Modelar el **ingreso real** (deflactado), no el nominal | Evita que la inflación 2016-2025 contamine el modelo. Modelar el nominal con efecto fijo de período inflaba el R² (el período absorbe la inflación en log), técnica que además no está en el material. El ingreso real se construye con el IPC (mismo deflactor del objetivo 2). Ver `diferencias_feedback_profesor.md`. |
| **No** incluir el período ni la edad² | Solo se usan las variables que pide la consigna (edad, sexo, nivel educativo, calificación, aglomerado). El período no es una característica de la persona y no estaba en el material; la edad se deja lineal. |
| Reportar **R² y R² ajustado** | `Regresión.pptx`, slide 11 (R²) y slide 24 (R² ajustado: "proporción de varianza explicada teniendo en cuenta el número de predictores"); `summary()` en `Ejemplo regresion.R`. |
| **Diagnóstico**: QQ-plot de residuos (normalidad) | `Regresión.pptx`, slide 20 ("QQ plot… si los puntos se alinean con la diagonal sugiere normalidad"); `AID 2022.pdf` pág. 253-254; `Ejemplo regresion.R` (`plot(modelo)`). |
| **Diagnóstico**: gráfico de residuos vs predichos (homocedasticidad) | `Regresión.pptx`, slide 22 ("gráfico de residuos… evaluar si el modelo es adecuado"); `Ejemplo regresion.R` (`plot(modelo)`). |
| Los **4 supuestos** del modelo lineal (media 0, homocedasticidad, normalidad, independencia) | `Regresión.pptx`, slide 9; `AID 2022.pdf` pág. 252 y 255 (normalidad, homocedasticidad e independencia de los residuos, con sus tests). |
| Interpretar cada **coeficiente** como efecto sobre la respuesta | `Regresión.pptx`, slide 16 ("β1 = cambio en E(Y) al aumentar X1 en una unidad, manteniendo el resto constante"). |
| Evaluar con **partición train/test (80/20)** | `AID 2022.pdf` pág. 332-333 (partición entrenamiento/validación). |
| Reportar **RMSE y MAE** | `Regresión.pptx`, slide 29 (error cuadrático medio) y slide 30 (error medio absoluto). |
| **Imputar con el modelo** y no con la media | `guia_visual_graficos.docx`, secc. 18 ("imputar con la media deforma la distribución… mejor: imputación por modelado estadístico usando correlaciones con otras variables"). |

## D. Conceptos de la EPH (definiciones)

| Concepto | Dónde se ve |
|--|--|
| Tasa de desocupación = desocupados / PEA | `guia_visual_graficos.docx`, secc. 6 ("desocupados / (ocupados + desocupados) = PEA"). |
| Asociación entre categórica (nivel educativo) y cuantitativa (ingreso) | `guia_visual_graficos.docx`, secc. 5 (boxplots por grupo; se cuantifica con ANOVA / eta). |

---

## Cómo usar esto en la defensa

Cuando justifiques una decisión, nombrá la fuente. Ejemplos:

- "Usamos la mediana porque, como vimos en la guía de visualización, los ingresos
  tienen asimetría positiva y la media se va para arriba por los valores altos."
- "Transformamos el ingreso con logaritmo: está en la guía (asimetría positiva) y en el
  libro AID 2022 como transformación de Box-Cox cuando el desvío crece con la media."
- "Validamos los supuestos del modelo con el QQ-plot y el gráfico de residuos, que es el
  diagnóstico que vimos en la clase 6 y que en R se hace con `plot(modelo)`."

# Guía de defensa - TP Final EPH (Gran Rosario vs Gran Tucumán)

> Material de estudio personal (no es parte del entregable). Objetivo: poder explicar
> y justificar CADA decisión y CADA resultado con tus palabras.

---

## 1. El trabajo en 30 segundos (elevator pitch)

"Analizamos la evolución del mercado laboral y los ingresos en Gran Rosario y Gran
Tucumán entre 2016 y 2025, usando las bases de microdatos de la EPH del INDEC. Calculamos
las tasas de actividad, empleo y desocupación, y los ingresos reales (deflactados por
inflación). Después cruzamos los ingresos con variables como educación, sexo, edad y tipo
de empleo, y armamos un modelo de regresión para imputar los ingresos que no fueron
declarados. El hallazgo principal es que, aunque las dos ciudades siguen el mismo ciclo
laboral, el poder adquisitivo evolucionó muy distinto: Rosario lo mantuvo y Tucumán lo perdió."

---

## 2. Guion de presentación (si hay que exponer, ~7 min)

1. **Qué y por qué** (30s): objetivo, los 2 aglomerados y por qué los elegimos.
2. **Datos** (1 min): EPH, base individual, todos los trimestres 2016-2025, ponderador.
3. **Metodología** (1,5 min): definición de las tasas, deflación por IPC, no respuesta, outliers.
4. **Resultados - tasas** (1 min): el ciclo (pico 2020, recuperación).
5. **Resultados - ingresos reales** (1,5 min): la divergencia Rosario vs Tucumán. Es el punto fuerte.
6. **Multivariado** (1 min): educación, calificación, brecha de género.
7. **Modelo de imputación** (1 min): qué hace, R², principales efectos.
8. **Conclusiones** (30s): cerrar con la divergencia de poder adquisitivo y las brechas estructurales.

---

## 3. Números clave (saber de memoria)

| Dato | Valor |
|--|--|
| Período | 2016-2025, todos los trimestres (38 trimestres, arranca 2016-T2) |
| Registros analizados | ~153.000 (Rosario ~70.000, Tucumán ~83.000) |
| Códigos de aglomerado | Gran Rosario = 4, Gran Tucumán = 29 |
| Ingreso real Rosario 2016→2025 | aproximadamente +3% |
| Ingreso real Tucumán 2016→2025 | aproximadamente -12% |
| Pico de desocupación | Rosario ~14% (2020), Tucumán ~11% (2021) |
| Brecha de género | mujeres ganan ~30% menos (Rosario), ~33% menos (Tucumán) |
| No respuesta a ingresos | Rosario hasta 46%, Tucumán hasta 17% |
| Outliers (ingreso real) | ~5% de los casos (método IQR) |
| R² del modelo | 0,82 (explica el 82% de la variabilidad del log-ingreso) |
| Casos imputados | ~10.500 ocupados sin ingreso declarado |
| Base de precios | pesos del 4º trimestre de 2025 |

---

## 4. Conceptos que tenés que poder explicar

**EPH:** Encuesta Permanente de Hogares del INDEC. Mide ocupación, desocupación e ingresos
en aglomerados urbanos. Es muestral (no censal), por eso cada caso tiene un ponderador.

**Ponderador (PONDERA):** factor de expansión. Cada persona encuestada "representa" a un
cierto número de personas de la población. Por eso las tasas se calculan sumando PONDERA,
no contando casos.

**Condición de actividad (ESTADO):** 1 = ocupado, 2 = desocupado, 3 = inactivo,
4 = menor de 10. **Desocupado** = no trabajó la semana de referencia Y buscó activamente
trabajo. El que no busca es **inactivo**, no desocupado.

**Las tres tasas:**
- Actividad = PEA / población total. (PEA = ocupados + desocupados)
- Empleo = ocupados / población total.
- Desocupación = desocupados / **PEA** (¡ojo, el denominador es la PEA, no la población!).

**Ingreso real / deflactar:** pasar los pesos nominales (corrientes) a pesos de un mismo
momento, dividiendo por el índice de precios. Permite comparar poder adquisitivo entre
años sin que la inflación distorsione.

**No respuesta:** gente que no contesta cuánto gana. En la EPH se marca con -9. No es lo
mismo que ganar 0 (eso es "no corresponde", por ejemplo un inactivo).

**Mediana vs media:** la mediana es el valor del medio; no la afectan los valores extremos.
Como el ingreso tiene outliers muy altos, usamos mediana (es más representativa).

**P21 vs P47T:** P21 = ingreso de la ocupación principal (laboral, de los ocupados).
P47T = ingreso total individual (laboral + no laboral). Usamos P47T para la distribución
de ingresos de la población y P21 para el modelo de no respuesta laboral.

---

## 5. Banco de preguntas y respuestas

### Sobre las decisiones del trabajo

**¿Por qué eligieron esos dos aglomerados?**
Buscábamos un buen contraste regional (Rosario, Centro/agroindustria, vs Tucumán, NOA),
con muestra grande y estable, y que estuvieran presentes en todos los trimestres del período.

**¿Por qué usaron todos los trimestres y no uno solo por año?**
Para aprovechar toda la información disponible, ver mejor la dinámica (incluida la
estacionalidad) y darle más datos al modelo. Tener más observaciones lo hace más robusto.

**¿Por qué deflactaron los ingresos? ¿No alcanzaba con el nominal?**
No: el ingreso nominal crece casi solo por inflación. Entre 2016 y 2025 los nominales se
multiplican por más de 100, pero eso no significa que la gente esté mejor. Al deflactar se
ve el poder adquisitivo real, que es lo que importa.

**¿Qué índice usaron para deflactar y por qué el promedio trimestral?**
El IPC Nivel General del INDEC. Como trabajamos por trimestre, usamos el promedio de los
tres meses de cada trimestre. El IPC de 2016 lo empalmamos con el IPC-GBA porque la serie
nacional recién arranca en diciembre de 2016 (misma base, diciembre 2016 = 100).

**¿Por qué la mediana y no el promedio de ingresos?**
Porque el ingreso tiene valores atípicos muy altos que inflan el promedio. La mediana es
robusta a esos extremos y representa mejor al "ingreso típico" (AID 2022, pág. 17-18).

### Sobre el análisis univariado (objetivo 1)

**¿Cómo describieron la distribución del ingreso?**
Con medidas de resumen: tendencia central (media y mediana), dispersión (desvío estándar,
coeficiente de variación, rango intercuartílico) y forma (asimetría de Fisher y curtosis).
Está todo en el capítulo 2 del libro de la cátedra (AID 2022, pág. 17-24).

**¿Qué les dice el coeficiente de asimetría?**
Da fuertemente positivo (alrededor de 8-10), lo que confirma una asimetría positiva: la
distribución tiene cola a la derecha y la media queda por encima de la mediana, arrastrada
por unos pocos ingresos muy altos (AID 2022, pág. 22-23).

**¿Y la curtosis?**
Da muy por encima de 3, es decir una distribución leptocúrtica: colas pesadas, con presencia
de valores extremos (AID 2022, pág. 24).

**¿Qué es el coeficiente de variación?**
Es la dispersión relativa: desvío estándar dividido la media. Nos dio cerca del 100%, o sea
una dispersión muy grande en relación al nivel del ingreso (AID 2022, pág. 21).

**¿Cómo detectaron los outliers?**
Con dos métodos: el del rango intercuartílico, que distingue outliers moderados (entre 1,5 y
3 veces el RI) de severos (más de 3 veces), y el del z-score o regla de los tres desvíos
(|z| mayor a 3). Los dos dan alrededor del 5% de los casos (AID 2022, pág. 36 y 38).

**¿Por qué no eliminaron los outliers?**
Porque son valores posibles, no inconsistencias: un ingreso muy alto puede existir. El libro
dice que los atípicos se inspeccionan y no se eliminan si son posibles (AID 2022, pág. 36).
Por eso usamos medidas robustas (mediana, RI) en vez de la media.

**¿Qué hicieron con la no respuesta?**
Es un dato faltante (código -9 en la EPH). No la imputamos con la media porque eso deforma la
distribución (lo vimos en la guía de gráficos, secc. 18). En su lugar la estimamos con el
modelo de regresión del objetivo 4.

### Sobre los resultados

**¿Qué muestra la evolución de las tasas?**
Las dos ciudades siguen el mismo ciclo: deterioro fuerte en 2020 por la pandemia (pico de
desocupación) y recuperación del empleo después. Rosario tiene tasas de actividad y empleo
estructuralmente más altas.

**¿Cuál es el resultado más importante?**
La divergencia de ingresos reales: en una década, Rosario mantuvo el poder adquisitivo
(aproximadamente +3%) mientras Tucumán lo perdió (aproximadamente -12%). La brecha entre
las dos ciudades se amplió.

**¿La desocupación bajó porque hay más empleo o porque la gente dejó de buscar?**
Hay que mirar las tres tasas juntas. En nuestro caso la tasa de empleo también sube hacia
el final, así que la baja de la desocupación viene acompañada de más empleo, no solo de
gente que se retira del mercado.

**¿Qué pasa con la brecha de género?**
Es persistente: las mujeres ganan entre 30% y 33% menos que los varones a lo largo de todo
el período, sin una tendencia clara a cerrarse.

### Sobre el análisis multivariado (objetivo 2)

**¿Cómo cuantificaron la relación entre el ingreso y variables como educación o sexo?**
Con el coeficiente eta al cuadrado, que mide qué proporción de la varianza del ingreso explica
cada variable. La calificación de la tarea (~13%) y el nivel educativo (~10%) son las que más
explican, por encima del sexo (~4%). Es la medida que la guía recomienda para asociar una
categórica con una cuantitativa (junto con ANOVA).

**¿Por qué calcularon Pearson y Spearman para edad e ingreso?**
Pearson mide la relación lineal y dio bajo (~0,09); Spearman, que mide la relación de orden,
dio un poco más (~0,10). Que sean parecidos y bajos confirma que la relación no es lineal sino
cóncava (el ingreso sube con la edad y después se aplana), y por eso en el modelo agregamos la
edad al cuadrado. (Guía secc. 8 y 9.)

**¿Qué es el gráfico de mosaicos y la V de Cramer?**
El mosaico cruza dos variables categóricas (nivel educativo y condición de actividad): el ancho
de cada columna es la frecuencia del nivel educativo y el alto de cada bloque, la proporción de
ocupados/desocupados/inactivos. Se ve que a mayor educación, más ocupados. La V de Cramer
(~0,18) cuantifica esa asociación entre dos categóricas. (Guía secc. 14.)

**¿Qué son las medidas de posición que muestran en el tiempo?**
Los cuartiles: además de la mediana (Q2), graficamos el P25 y el P75. La banda entre ellos es el
50% central de los ingresos, y muestra cómo se mueve toda la distribución, no solo el centro.

### Sobre el modelo (objetivo 4, la nota alta)

**¿Qué hace el modelo y para qué sirve?**
Es una regresión lineal que estima el ingreso de los ocupados que NO declararon cuánto
ganan, a partir de sus características (edad, sexo, educación, calificación, aglomerado,
período). Sirve para no perder esos casos y reducir el sesgo por no respuesta.

**¿Por qué predicen el logaritmo del ingreso y no el ingreso directo?**
Porque el ingreso es muy asimétrico (cola larga hacia la derecha). El logaritmo lo
simetriza, mejora el ajuste y, como ventaja, cada coeficiente se interpreta aproximadamente
como un cambio porcentual del ingreso.

**¿Por qué incluyeron la edad al cuadrado?**
Porque la relación entre edad e ingreso no es lineal: el ingreso sube con la edad, se
estabiliza y después baja. El término cuadrático (con signo negativo) captura esa forma
cóncava. (Es la idea de la ecuación de Mincer).

**¿Por qué pusieron el período como variable?**
Como efecto fijo, absorbe el nivel de precios de cada trimestre. Así los ingresos nominales
de 2016 y de 2025 se vuelven comparables dentro del modelo, sin que la inflación domine.

**¿Cómo evaluaron el modelo? ¿Qué es el R²?**
Partimos los datos en 80% para entrenar y 20% para probar. El R² (0,82) es la proporción
de la variabilidad del log-ingreso que el modelo explica; 0,82 es un ajuste muy bueno para
datos individuales. También miramos el error (RMSE).

**¿Cómo interpretás los coeficientes?**
Cada uno es el efecto porcentual aproximado sobre el ingreso, respecto de una categoría
base. Por ejemplo: tener estudios superiores completos suma más de 100% frente a primario
incompleto; ser mujer resta cerca de 40% a igualdad del resto de las variables.

**Si imputás los ingresos faltantes, ¿cómo sabés que está bien?**
No es una certeza, es una estimación basada en gente parecida que sí respondió. La validamos
midiendo el error sobre datos que el modelo no vio (el 20% de prueba). Es la mejor estimación
posible con la información observable.

### Conceptuales / EPH

**¿Por qué la tasa de desocupación se calcula sobre la PEA y no sobre la población total?**
Porque la desocupación solo tiene sentido entre quienes están en el mercado de trabajo
(ocupados + desocupados). Un bebé o un jubilado no son "desocupados".

**¿Qué es el factor de expansión y por qué lo usan?**
Porque la EPH es una muestra. Cada caso representa a muchas personas; el ponderador permite
estimar valores para toda la población, no solo para los encuestados.

---

## 6. Limitaciones (mostrar honestidad mejora la nota)

Si te preguntan "¿qué mejorarían?" o "¿qué limitaciones tiene?", reconocelas con criterio:

- **2020 tiene muestra reducida** (sobre todo Tucumán) por la pandemia: ese año se lee con cautela.
- **Las medianas de ingreso las calculamos sin ponderar** (usamos PONDERA en las tasas).
  El INDEC sugiere ponderadores específicos para ingresos (PONDIIO/PONDII). Es una mejora posible.
- **La agrupación por rama de actividad** (PP04B) es aproximada (sectores armados por los
  primeros dígitos del código).
- **El modelo es lineal y simple**: cumple el objetivo, pero podría refinarse (otros
  predictores, corrección del sesgo al volver de logaritmo a pesos).
- **El primer trimestre de 2016 no existe** (la EPH estuvo suspendida), por eso la serie
  arranca en 2016-T2.

---

## 7. Tips para la defensa virtual

- **Tené todo a mano en pantalla**: el informe (PDF), esta guía y, si se puede, los gráficos
  abiertos para mostrar o mirar de reojo.
- **Conocé tus gráficos**: para cada uno, sabé qué eje es qué y cuál es la conclusión.
- Si no sabés algo, **no inventes**: "eso no lo profundizamos, pero lo razonaría así...".
- **Conectá número con interpretación**: no recites cifras, explicá qué significan.
- Hablá de **"nosotros"** (es grupal) y sabé **tu parte** en detalle (vos: base de datos y tasas).
- **Prepará el setup**: buena conexión, micrófono, compartir pantalla probado antes.
- Si te trabás, **respirá y volvé al pitch** de la sección 1; siempre podés reanclar ahí.

---

## 8. Frases de cierre útiles

- "El trabajo muestra que detrás de un crecimiento nominal parecido, el poder adquisitivo
  de las dos ciudades tomó caminos opuestos."
- "Las desigualdades por educación, calificación y género son estables en todo el período."
- "El modelo nos permitió recuperar los ingresos no declarados con un buen nivel de ajuste."

---

## 9. Qué dice cada gráfico

Para cada uno: qué tipo es, qué muestra y qué se concluye.

### Objetivo 1 - Análisis univariado

- **Histograma del ingreso** (`13`): distribución del ingreso. El eje X son los ingresos, el
  Y cuánta gente hay en cada tramo. Tiene cola larga a la derecha (asimetría positiva): la
  media (~$845k) queda a la derecha de la mediana (~$633k), arrastrada por pocos ingresos
  altos. Por eso usamos la mediana.
- **Boxplot por aglomerado, escala log** (`10`): la caja es el 50% central (Q1 a Q3), la
  línea negra es la mediana y los puntos grises de arriba son los outliers. Rosario tiene la
  mediana más alta. La escala logarítmica deja ver todo el rango.
- **Boxplot por año** (`11`): una caja por año; muestra cómo se desplaza la distribución del
  ingreso real en el tiempo.
- **No respuesta** (`06`, líneas): % de ocupados que no declaran su ingreso, por trimestre.
  Rosario muy alto (hasta 46%), Tucumán mucho más bajo. Justifica el modelo de imputación.
- **Heatmap de correlación** (`14`): correlación de Pearson entre variables (rojo positiva,
  azul negativa). Ingreso de la ocupación y total correlacionan 0,91; edad-ingreso solo 0,13.

### Objetivo 2 - Evolución de los indicadores

- **Tasa de actividad / empleo / desocupación** (`01`, `02`, `03`, líneas trimestrales): una
  línea por aglomerado. Se ve la caída de 2020 (pandemia) y la recuperación; en desocupación,
  el pico de 2020 (~14-18%), la baja a 2023-24 (~5%) y un repunte en 2025.
- **Nominal vs real** (`05`, dos paneles): izquierda el ingreso nominal, que "explota" por la
  inflación (engaña); derecha el ingreso real (deflactado), el poder adquisitivo verdadero.
  Es el gráfico que explica por qué hay que deflactar.
- **Ingreso real mediano** (`04`, líneas): Rosario se sostiene, Tucumán cae.
- **Medidas de posición** (`17`, líneas con banda): P25, mediana y P75; la banda es el 50%
  central. Muestra cómo se mueve toda la distribución, no solo el centro.
- **Ingreso por educación / por calificación** (`07`, `08`, boxplots comparativos): la mediana
  y la dispersión crecen con el nivel educativo y con la calificación de la tarea.
- **Brecha de género** (`09`, líneas varón vs mujer): ingreso mediano de varones (azul) y
  mujeres (rosa); el área gris es la brecha. Las mujeres ganan ~30-33% menos, de forma
  persistente.
- **Edad vs ingreso** (`19`, dispersión): cada punto es una persona, más la recta de
  tendencia. La nube es difusa (Pearson 0,085): la relación es débil y no lineal (sube con la
  edad y se aplana). Justifica la edad al cuadrado del modelo.
- **Mosaico educación x condición de actividad** (`18`): el ancho de cada columna es cuánta
  gente hay en ese nivel educativo; el alto de cada bloque, la proporción de ocupados (verde),
  desocupados (rojo) e inactivos (gris). A más educación, más ocupados. La V de Cramer (0,18)
  lo cuantifica.

### Objetivo 4 - Modelo de imputación

- **Coeficientes del modelo** (`12`, puntos + línea de tendencia): el efecto de cada variable
  sobre el ingreso, ordenado de menor a mayor, desde Mujer (-40%) hasta Superior completo
  (+139%). A la derecha del 0 suman ingreso; a la izquierda, restan.
- **QQ-plot de residuos** (`15`): diagnostica la normalidad de los residuos. Si los puntos
  siguen la diagonal, son normales. Los nuestros la siguen en el centro y se desvían en las
  colas (típico de ingresos).
- **Residuos vs predichos** (`16`): diagnostica la homocedasticidad. Los residuos deben ser
  una nube sin patrón alrededor del 0. Los nuestros están centrados y con dispersión pareja,
  así que el supuesto se cumple razonablemente.

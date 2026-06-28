# TP Final - Análisis de la EPH 2016-2025

Trabajo práctico final (2º parcial) de Introducción al Análisis de Datos (TUP - UTN).
Analiza la evolución del mercado laboral y los ingresos en dos aglomerados de la
Encuesta Permanente de Hogares (EPH), período 2016-2025.

- Aglomerados comparados: Gran Rosario (cód. 4) y Gran Tucumán-Tafí Viejo (cód. 29).
- Indicadores: tasa de actividad, tasa de empleo, tasa de desocupación e ingresos
  reales (deflactados por inflación).
- Apunta a aprobación directa (incluye el modelo de imputación de ingresos).

## 1. Organización del proyecto

```
trabajo-practico-final/
  README.md                  este archivo
  requirements.txt           dependencias de Python
  1C 2026-3.pdf              consigna del TP
  src/                       todo el código
    comun.py                 configuración compartida (no se ejecuta solo)
    00_correr_todo.py        corre todos los scripts en orden
    01_construir_panel.py
    02_tasas.py
    03_ingresos_reales.py
    04_multivariado.py
    05_univariado.py
    06_graficos.py
    07_modelo.py
    08_generar_reporte.py    arma reporte.md a partir de los datos
    09_exportar_pdf.py       convierte reporte.md a reporte.pdf
    10_exportar_docx.py      convierte reporte.md a reporte.docx (Word)
  reporte.md / .pdf / .docx  informe final (se genera, no se edita a mano)
  output/                    se genera al correr los scripts
    panel.parquet            base unificada de los dos aglomerados
    tablas/                  resultados en .csv
    graficos/                gráficos en .png
  EPH_usu_*_Trim_*_txt.zip   bases del INDEC (ver sección 2)
```

El primer script (`01`) lee los datos crudos y arma un panel; el resto parte de ese
panel. Todo el proyecto se reconstruye corriendo el código, incluido el informe
`reporte.md` y el `reporte.pdf`, que se arman a partir de los datos.

## 2. Datos necesarios (bases del INDEC)

Se usa la base individual de la EPH (aglomerados), de todos los trimestres disponibles
entre 2016 y 2025. Se descargan de
https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos (EPH, Base individual).

- Cada trimestre viene en un `.zip` que ya trae el `.txt` adentro; no hace falta
  descomprimirlo, el script lo lee directo.
- Los `.zip` van en la raíz del proyecto (esta misma carpeta).
- El nombre del archivo varía según el trimestre y el año (`EPH_usu_3_Trim_2024_txt.zip`,
  `EPH_usu_3erTrim_2016_txt.zip`, etc.); el script los detecta por patrón y carga todos.
- El primer trimestre de 2016 no existe (la EPH estuvo suspendida y se retomó en el
  2º trimestre de 2016), así que la serie arranca en 2016-T2.

## 3. Puesta en marcha (una sola vez)

```bash
python3 -m venv .venv
source .venv/bin/activate         # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Para generar el PDF, en Mac hace falta además instalar las librerías de WeasyPrint;
y para el Word (`.docx`), pandoc:

```bash
brew install pango gdk-pixbuf libffi
brew install pandoc
```

## 4. Cómo correr el análisis

Todo de una:

```bash
python src/00_correr_todo.py
```

Esto regenera el panel, las tablas, los gráficos, el `reporte.md` y el `reporte.pdf`.

Paso a paso (mismo resultado):

```bash
python src/01_construir_panel.py     # arma output/panel.parquet
python src/02_tasas.py               # tasas de actividad, empleo y desocupación
python src/03_ingresos_reales.py     # ingresos deflactados por IPC
python src/04_multivariado.py        # cruces (sexo, educación, edad, calificación, rama)
python src/05_univariado.py          # no respuesta y outliers
python src/06_graficos.py            # gráficos (necesita 02 a 05)
python src/07_modelo.py              # modelo de imputación de ingresos
python src/08_generar_reporte.py     # arma reporte.md
python src/09_exportar_pdf.py        # convierte reporte.md a reporte.pdf
python src/10_exportar_docx.py       # convierte reporte.md a reporte.docx (Word)
```

Dependencias entre scripts:

- `01` corre primero (genera el panel que usan todos).
- `06`, `07` y `08` necesitan que antes hayan corrido `02` a `05`.
- `09` necesita el `reporte.md` que genera `08`.

## 5. Qué hace cada script

| Script | Objetivo | Qué hace |
|--------|----------|----------|
| `comun.py` | - | Configuración compartida: aglomerados, rutas, códigos de la EPH, serie de IPC y mapeos. |
| `00_correr_todo.py` | - | Corre los scripts 01 a 09 en orden. |
| `01_construir_panel.py` | base | Lee la base individual de todos los trimestres desde los `.zip`, filtra los dos aglomerados y los une. |
| `02_tasas.py` | 2 | Tasas de actividad, empleo y desocupación, ponderadas por `PONDERA`. |
| `03_ingresos_reales.py` | 2 | Deflacta los ingresos por IPC; medias, medianas y cuartiles. |
| `04_multivariado.py` | 2 | Ingreso real por sexo, nivel educativo, edad, calificación (PP04D) y rama (PP04B). |
| `05_univariado.py` | 1 | No respuesta a ingresos por trimestre y outliers (método IQR). |
| `06_graficos.py` | 3 | Gráficos de evolución y diagramas de cajas. |
| `07_modelo.py` | 4 | Regresión sobre log(ingreso) para imputar la no respuesta; R², RMSE y coeficientes. |
| `08_generar_reporte.py` | - | Arma el `reporte.md` con los números, tablas y gráficos. |
| `09_exportar_pdf.py` | - | Convierte el `reporte.md` en `reporte.pdf`. |
| `10_exportar_docx.py` | - | Convierte el `reporte.md` en `reporte.docx` (Word), con pandoc. |

## 6. Decisiones metodológicas

- Tasas (definiciones INDEC): actividad = PEA / población total; empleo = ocupados /
  población total; desocupación = desocupados / PEA. Todo ponderado por `PONDERA`.
- Inflación: los ingresos se deflactan con el IPC Nivel General del INDEC (promedio de
  cada trimestre) y se expresan en pesos del 4º trimestre de 2025. El IPC de 2016 se
  empalma con el IPC-GBA (misma base), porque la serie nacional arranca en diciembre de 2016.
- No respuesta a ingresos: en la EPH los montos sin respuesta se codifican como -9
  (distinto de 0, que significa "no corresponde").
- Formato de las bases: separador `;` y coma decimal.

## 7. División del trabajo

Como los dos aglomerados son comunes a todo el informe, dividimos por objetivo/análisis
(no por aglomerado). La base común (`01`) se hace primero entre todos; después cada uno
toma su bloque, que es independiente:

| Integrante | Bloque |
|------------|--------|
| (P1) | Base de datos y tasas laborales (`01`, `02`), coordinación del informe |
| (P2) | Univariado: no respuesta y outliers (`05`) |
| (P3) | Ingresos reales y multivariado (`03`, `04`) |
| (P4) | Modelo de imputación (`07`) |

Visualización (`06`) y redacción son transversales. Completar con los nombres de los
integrantes y la división final.

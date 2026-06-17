"""
comun.py - Configuración y utilidades compartidas por todos los scripts del TP.

Acá viven las constantes que TODOS los scripts usan (aglomerados, rutas,
columnas, mapeos de códigos y la serie de IPC para deflactar). La idea es
tener un único lugar para tocar parámetros y que el resto del código no
repita configuración.
"""

import glob
import os
import re
import pandas as pd

# ---------------------------------------------------------------------------
# 1. AGLOMERADOS BAJO ANÁLISIS
# ---------------------------------------------------------------------------
# Códigos de la EPH (ver hoja "Personas" de EPH_total_urbano_estructura_bases.xlsx)
AGLOMERADOS = {
    4: "Gran Rosario",
    29: "Gran Tucumán",
}

# Integrantes del grupo (aparecen en el encabezado del informe). COMPLETAR:
INTEGRANTES = "_(completar: nombres de los integrantes)_"

# ---------------------------------------------------------------------------
# 2. RUTAS
# ---------------------------------------------------------------------------
# Carpeta raíz del TP (un nivel arriba de src/)
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(RAIZ, "output")
TABLAS = os.path.join(OUTPUT, "tablas")
GRAFICOS = os.path.join(OUTPUT, "graficos")
PANEL_PARQUET = os.path.join(OUTPUT, "panel.parquet")

for carpeta in (OUTPUT, TABLAS, GRAFICOS):
    os.makedirs(carpeta, exist_ok=True)

# Años del período de análisis (se cargan todos los trimestres disponibles).
ANIOS = list(range(2016, 2026))

# ---------------------------------------------------------------------------
# 3. COLUMNAS DE INTERÉS
# ---------------------------------------------------------------------------
# Solo cargamos lo que usamos (las bases tienen ~180 columnas).
COLUMNAS = [
    "ANO4", "TRIMESTRE", "AGLOMERADO",   # identificación
    "PONDERA",                            # ponderador general (para las tasas)
    "PONDII", "PONDIIO",                  # ponderadores corregidos por no respuesta a ingresos
    "ESTADO",                             # condición de actividad
    "CAT_OCUP",                           # categoría ocupacional
    "CH04", "CH06", "NIVEL_ED",           # sexo, edad, nivel educativo
    "PP04B_COD", "PP04D_COD",             # rama de actividad y ocupación
    "P21", "P47T", "IMPUTA",              # ingresos y marca de imputación INDEC
]

# ---------------------------------------------------------------------------
# 4. CÓDIGOS Y ETIQUETAS DE LA EPH
# ---------------------------------------------------------------------------
# ESTADO: condición de actividad
ESTADO_OCUPADO = 1
ESTADO_DESOCUPADO = 2
ESTADO_INACTIVO = 3
ESTADO_MENOR = 4   # menor de 10 años

# Sexo (CH04)
SEXO = {1: "Varón", 2: "Mujer"}

# Nivel educativo (NIVEL_ED)
NIVEL_ED = {
    1: "Primario incompleto",
    2: "Primario completo",
    3: "Secundario incompleto",
    4: "Secundario completo",
    5: "Superior/Univ. incompleto",
    6: "Superior/Univ. completo",
    7: "Sin instrucción",
}

# No respuesta a ingresos: en la EPH los montos usan -9 (ver Anexo I del diseño).
NO_RESPUESTA_INGRESO = -9

# ---------------------------------------------------------------------------
# 4b. ÍNDICE DE PRECIOS (IPC) PARA DEFLACTAR - datos REALES del INDEC
# ---------------------------------------------------------------------------
# IPC Nivel General, base diciembre 2016 = 100. Como ahora analizamos TODOS los
# trimestres, usamos el IPC PROMEDIO de cada trimestre (promedio de sus 3 meses).
#   - 2017-2025: IPC Nacional INDEC (serie 148.3_INIVELNAL_DICI_M_26, datos.gob.ar)
#   - 2016: IPC-GBA INDEC (serie 103.1_I2N_2016_M_19), porque la serie nacional
#     recién arranca en dic-2016. Misma base, empalma directo.
# Fuente: API de Series de Tiempo del Estado (apis.datos.gob.ar / INDEC).
IPC_TRIMESTRE = {
    (2016, 2): 88.83, (2016, 3): 94.2188, (2016, 4): 98.6865,
    (2017, 1): 103.8065, (2017, 2): 110.4482, (2017, 3): 115.5797, (2017, 4): 121.7141,
    (2018, 1): 130.0516, (2018, 2): 140.3819, (2018, 3): 156.5461, (2018, 4): 179.3471,
    (2019, 1): 197.4391, (2019, 2): 219.3552, (2019, 3): 241.2706, (2019, 4): 272.9087,
    (2020, 1): 297.0158, (2020, 2): 315.6689, (2020, 3): 337.2951, (2020, 4): 372.1869,
    (2021, 1): 417.7441, (2021, 2): 468.6601, (2021, 3): 512.3299, (2021, 4): 563.4854,
    (2022, 1): 638.1741, (2022, 2): 754.3716, (2022, 3): 910.0667, (2022, 4): 1080.8574,
    (2023, 1): 1288.9494, (2023, 2): 1606.8052, (2023, 3): 2055.7637, (2023, 4): 2948.5093,
    (2024, 1): 4814.8045, (2024, 2): 6085.2139, (2024, 3): 6871.1437, (2024, 4): 7499.7977,
    (2025, 1): 8090.1447, (2025, 2): 8718.5543, (2025, 3): 9200.4364, (2025, 4): 9855.5306,
}

# Período base para expresar los ingresos reales (precios constantes).
# Usamos el último trimestre disponible -> pesos del 4º trimestre de 2025.
PERIODO_BASE = (2025, 4)
IPC_BASE = IPC_TRIMESTRE[PERIODO_BASE]
ETIQUETA_PRECIOS = "pesos del 4º trimestre de 2025"


def factor_real(anio, trimestre):
    """Factor para llevar un monto nominal de (anio, trimestre) al período base."""
    return IPC_BASE / IPC_TRIMESTRE[(int(anio), int(trimestre))]


def agregar_columnas_tiempo(df):
    """Agrega columnas de tiempo y deflación al panel: PERIODO (texto, p.ej.
    '2024-T3'), PERIODO_NUM (numérico para ordenar/graficar) y FACTOR_REAL."""
    df = df.copy()
    df["PERIODO"] = df["ANIO"].astype(int).astype(str) + "-T" + df["TRIMESTRE"].astype(int).astype(str)
    df["PERIODO_NUM"] = df["ANIO"] + (df["TRIMESTRE"] - 1) / 4
    df["FACTOR_REAL"] = [factor_real(a, t) for a, t in zip(df["ANIO"], df["TRIMESTRE"])]
    return df


# Calificación de la tarea = ÚLTIMO dígito de PP04D_COD (clasificador CNO del INDEC).
CALIFICACION = {
    1: "Profesional",
    2: "Técnica",
    3: "Operativa",
    4: "No calificada",
}


def calificacion_tarea(pp04d_cod):
    """Calificación ocupacional: último dígito de PP04D_COD."""
    if pd.isna(pp04d_cod) or pp04d_cod <= 0:
        return "Sin dato"
    ultimo = int(str(int(pp04d_cod)).zfill(5)[-1])
    return CALIFICACION.get(ultimo, "Otra/Ns")


def sector_actividad(pp04b_cod):
    """Rama de actividad agrupada en grandes sectores (aprox. divisiones CAES
    del INDEC, a partir de los 2 primeros dígitos de PP04B_COD)."""
    if pd.isna(pp04b_cod) or pp04b_cod <= 0:
        return "Sin dato"
    d2 = int(str(int(pp04b_cod)).zfill(4)[:2])
    if d2 in range(1, 10):
        return "Agro, pesca y minería"
    if d2 in range(10, 35):
        return "Industria manufacturera"
    if d2 in range(35, 41):
        return "Electricidad, gas y agua"
    if d2 in range(41, 45):
        return "Construcción"
    if d2 in range(45, 49):
        return "Comercio"
    if d2 in range(49, 55):
        return "Transporte y comunicaciones"
    if d2 in range(55, 57):
        return "Hotelería y gastronomía"
    if d2 in range(58, 84):
        return "Servicios financieros y profesionales"
    if d2 == 84:
        return "Administración pública"
    if d2 == 85:
        return "Enseñanza"
    if d2 in range(86, 89):
        return "Salud y servicios sociales"
    if d2 == 97:
        return "Servicio doméstico"
    if d2 in range(90, 97):
        return "Otros servicios"
    return "Otros / No especificado"


def rango_etario(edad):
    """Agrupa la edad (CH06) en tramos para el análisis multivariado."""
    if pd.isna(edad):
        return "Sin dato"
    if edad < 15:
        return "Menores de 15"
    if edad <= 29:
        return "Jóvenes (15-29)"
    if edad <= 64:
        return "Adultos (30-64)"
    return "Adultos mayores (65+)"


# ---------------------------------------------------------------------------
# 5. LOCALIZADOR DE ARCHIVOS
# ---------------------------------------------------------------------------
# Usamos la EPH de aglomerados (base INDIVIDUAL). Cargamos TODOS los trimestres
# disponibles. Vienen en zip EPH_usu_<trim>_Trim_<año>_txt.zip (los nombres
# varían: '1er', '2', '2do', '3erTrim', etc.). OJO: COMA decimal (decimal=",").
SEPARADOR = ";"
DECIMAL = ","

# Captura el dígito del trimestre y el año del nombre del zip.
_PATRON_ZIP = re.compile(r"usu_(\d)(?:er|do|to)?_?Trim_?(\d{4})", re.IGNORECASE)


def zips_disponibles():
    """Lista de (anio, trimestre, ruta) de todos los zip de EPH individual
    presentes en la carpeta, ordenada cronológicamente."""
    encontrados = []
    for ruta in glob.glob(os.path.join(RAIZ, "EPH_usu_*.zip")):
        m = _PATRON_ZIP.search(os.path.basename(ruta))
        if m:
            trim, anio = int(m.group(1)), int(m.group(2))
            encontrados.append((anio, trim, ruta))
    return sorted(encontrados)

"""
01_construir_panel.py - Construye el panel de microdatos de los aglomerados.

Lee la base INDIVIDUAL de la EPH (aglomerados) de TODOS los trimestres
disponibles (2016-2025), directamente desde los zip EPH_usu_*_Trim_*_txt.zip
(sin descomprimir). Se queda con las columnas de interés y SOLO con los dos
aglomerados bajo análisis, agrega columnas de tiempo y deflación, y lo guarda
en output/panel.parquet.

Todos los demás scripts parten de ese panel.

Uso:  python src/01_construir_panel.py
"""

import zipfile
import pandas as pd
import comun


def cargar_archivo(anio, trim, ruta_zip):
    """Lee la base individual de un trimestre desde el zip y la filtra."""
    archivo_zip = zipfile.ZipFile(ruta_zip)
    # La base de personas se llama "individual" salvo en 2020-T4, que la nombró
    # "personas". Tomamos ese archivo (el que no es el de "hogar").
    nombre_base_individual = next(
        nombre_interno for nombre_interno in archivo_zip.namelist()
        if ("individual" in nombre_interno.lower() or "personas" in nombre_interno.lower())
        and "hogar" not in nombre_interno.lower())

    # Primera lectura sin filas, solo para ver que columnas trae esta base, porque
    # las columnas disponibles cambian de un trimestre a otro.
    with archivo_zip.open(nombre_base_individual) as archivo:
        columnas_disponibles = pd.read_csv(archivo, sep=comun.SEPARADOR, nrows=0,
                                           encoding="latin1").columns
    columnas_a_leer = [columna for columna in comun.COLUMNAS if columna in columnas_disponibles]

    # Segunda lectura, ahora si con los datos, quedandonos solo con esas columnas.
    with archivo_zip.open(nombre_base_individual) as archivo:
        datos_trimestre = pd.read_csv(archivo, sep=comun.SEPARADOR, decimal=comun.DECIMAL,
                                      usecols=columnas_a_leer, encoding="latin1",
                                      low_memory=False)

    # Forzamos cada columna a numerica; lo que no se pueda convertir queda como nulo.
    for columna in columnas_a_leer:
        datos_trimestre[columna] = pd.to_numeric(datos_trimestre[columna], errors="coerce")

    # Nos quedamos solo con los dos aglomerados bajo analisis y agregamos las columnas
    # de tiempo y el nombre legible del aglomerado.
    datos_trimestre = datos_trimestre[datos_trimestre["AGLOMERADO"].isin(comun.AGLOMERADOS)].copy()
    datos_trimestre["ANIO"] = anio
    datos_trimestre["TRIMESTRE"] = trim
    datos_trimestre["AGLO_NOMBRE"] = datos_trimestre["AGLOMERADO"].map(comun.AGLOMERADOS)
    return datos_trimestre


def main():
    print("Construyendo el panel (Gran Rosario + Gran Tucumán)")
    print("Fuente: EPH individual (aglomerados), TODOS los trimestres disponibles.\n")

    trimestres_disponibles = comun.zips_disponibles()
    if not trimestres_disponibles:
        raise SystemExit("No encontré ningún zip EPH_usu_*.zip en la carpeta.")

    # Vamos leyendo trimestre por trimestre y guardando cada tabla en una lista,
    # para despues pegarlas todas juntas una abajo de la otra.
    partes_del_panel = []
    for anio, trim, ruta_zip in trimestres_disponibles:
        datos_trimestre = cargar_archivo(anio, trim, ruta_zip)
        partes_del_panel.append(datos_trimestre)
        print(f"  {anio}-T{trim}: {len(datos_trimestre):>5} registros  "
              f"(Rosario {sum(datos_trimestre.AGLOMERADO == 4):>4} | "
              f"Tucumán {sum(datos_trimestre.AGLOMERADO == 29):>4})")

    panel = pd.concat(partes_del_panel, ignore_index=True)
    panel = comun.agregar_columnas_tiempo(panel)   # PERIODO, PERIODO_NUM, FACTOR_REAL
    panel.to_parquet(comun.PANEL_PARQUET, index=False)

    periodos = sorted(panel["PERIODO"].unique(), key=lambda periodo: (int(periodo[:4]), int(periodo[-1])))
    print(f"\nPanel total: {len(panel):,} registros | {len(periodos)} trimestres")
    print(f"  Desde {periodos[0]} hasta {periodos[-1]}")
    print(f"Guardado en: {comun.PANEL_PARQUET}")


if __name__ == "__main__":
    main()

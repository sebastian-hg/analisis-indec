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
    z = zipfile.ZipFile(ruta_zip)
    # La base de personas se llama "individual" salvo en 2020-T4, que la nombró
    # "personas". Tomamos ese archivo (el que no es el de "hogar").
    miembro = next(n for n in z.namelist()
                   if ("individual" in n.lower() or "personas" in n.lower())
                   and "hogar" not in n.lower())

    with z.open(miembro) as fh:
        encabezado = pd.read_csv(fh, sep=comun.SEPARADOR, nrows=0, encoding="latin1").columns
    usar = [c for c in comun.COLUMNAS if c in encabezado]

    with z.open(miembro) as fh:
        df = pd.read_csv(fh, sep=comun.SEPARADOR, decimal=comun.DECIMAL,
                         usecols=usar, encoding="latin1", low_memory=False)

    for col in usar:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[df["AGLOMERADO"].isin(comun.AGLOMERADOS)].copy()
    df["ANIO"] = anio
    df["TRIMESTRE"] = trim
    df["AGLO_NOMBRE"] = df["AGLOMERADO"].map(comun.AGLOMERADOS)
    return df


def main():
    print("Construyendo el panel (Gran Rosario + Gran Tucumán)")
    print("Fuente: EPH individual (aglomerados), TODOS los trimestres disponibles.\n")

    disponibles = comun.zips_disponibles()
    if not disponibles:
        raise SystemExit("No encontré ningún zip EPH_usu_*.zip en la carpeta.")

    partes = []
    for anio, trim, ruta in disponibles:
        d = cargar_archivo(anio, trim, ruta)
        partes.append(d)
        print(f"  {anio}-T{trim}: {len(d):>5} registros  "
              f"(Rosario {sum(d.AGLOMERADO == 4):>4} | Tucumán {sum(d.AGLOMERADO == 29):>4})")

    panel = pd.concat(partes, ignore_index=True)
    panel = comun.agregar_columnas_tiempo(panel)   # PERIODO, PERIODO_NUM, FACTOR_REAL
    panel.to_parquet(comun.PANEL_PARQUET, index=False)

    periodos = sorted(panel["PERIODO"].unique(), key=lambda p: (int(p[:4]), int(p[-1])))
    print(f"\nPanel total: {len(panel):,} registros | {len(periodos)} trimestres")
    print(f"  Desde {periodos[0]} hasta {periodos[-1]}")
    print(f"Guardado en: {comun.PANEL_PARQUET}")


if __name__ == "__main__":
    main()

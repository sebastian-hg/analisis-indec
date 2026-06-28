"""
00_correr_todo.py - Corre TODO el proyecto de punta a punta.

Ejecuta en orden los scripts 01 a 09, de modo que con un solo comando se
reconstruye absolutamente todo: panel de datos, tablas, gráficos, el informe
reporte.md y el PDF final. Todo sale de correr código; nada se edita a mano.

Uso:  python src/00_correr_todo.py
"""

import os
import subprocess
import sys

PASOS = [
    ("01_construir_panel.py", "Construir el panel 2016-2025"),
    ("02_tasas.py", "Tasas de actividad/empleo/desocupación"),
    ("03_ingresos_reales.py", "Ingresos reales (deflactados por IPC)"),
    ("04_multivariado.py", "Cruces multivariados del ingreso"),
    ("05_univariado.py", "No respuesta y outliers"),
    ("06_graficos.py", "Gráficos de los indicadores"),
    ("07_modelo.py", "Modelo de imputación de ingresos"),
    ("08_generar_reporte.py", "Generar el informe reporte.md"),
    ("09_exportar_pdf.py", "Exportar reporte.pdf"),
    ("10_exportar_docx.py", "Exportar reporte.docx (Word)"),
]


def main():
    # Carpeta donde viven los scripts (la misma en la que esta este archivo).
    carpeta_scripts = os.path.dirname(os.path.abspath(__file__))
    print("=" * 60)
    print(" CORRIENDO EL PROYECTO COMPLETO ".center(60, "="))
    print("=" * 60)

    # Recorremos los pasos en orden. enumerate(..., 1) numera desde 1 para mostrar
    # el progreso "[paso actual / total]" en pantalla.
    for numero_paso, (nombre_script, descripcion) in enumerate(PASOS, 1):
        print(f"\n[{numero_paso}/{len(PASOS)}] {descripcion}  ({nombre_script})")
        print("-" * 60)
        # Corremos cada script como un proceso aparte, con el mismo Python que ejecuta
        # este archivo (sys.executable).
        resultado = subprocess.run([sys.executable, os.path.join(carpeta_scripts, nombre_script)])
        # Si un script falla (codigo de salida distinto de 0), cortamos toda la cadena.
        if resultado.returncode != 0:
            print(f"\nError: falló {nombre_script}. Se detiene la ejecución.")
            sys.exit(1)

    print("\n" + "=" * 60)
    print(" Listo: panel, tablas, gráficos, reporte.md y reporte.pdf ".center(60, "="))
    print("=" * 60)


if __name__ == "__main__":
    main()

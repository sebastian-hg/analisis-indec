"""
10_exportar_docx.py - Convierte reporte.md en reporte.docx (Word).

Usa pandoc, que arma un documento de Word con el texto, las tablas y los
gráficos embebidos. Sirve para compartir y editar el informe en Word o
Google Docs.

Requisito (una sola vez, en Mac):  brew install pandoc

Uso:  python src/10_exportar_docx.py
"""

import os
import shutil
import subprocess
import comun


def main():
    # Primero verificamos que pandoc este instalado en la computadora. Si no esta,
    # avisamos como instalarlo y salimos sin generar el documento de Word.
    if shutil.which("pandoc") is None:
        print("No está instalado pandoc; se omite el .docx.")
        print("Para generarlo: brew install pandoc")
        return

    # Rutas del informe de origen (Markdown) y del documento de Word a generar.
    ruta_markdown = os.path.join(comun.RAIZ, "reporte.md")
    ruta_docx = os.path.join(comun.RAIZ, "reporte.docx")

    # Llamamos a pandoc para que convierta el Markdown en .docx. El --resource-path
    # le dice donde encontrar las imagenes (los graficos) para incrustarlas.
    subprocess.run(["pandoc", ruta_markdown, "-o", ruta_docx, "--resource-path", comun.RAIZ], check=True)
    print(f"DOCX generado: {ruta_docx}")


if __name__ == "__main__":
    main()

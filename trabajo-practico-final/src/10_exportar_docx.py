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
    if shutil.which("pandoc") is None:
        print("No está instalado pandoc; se omite el .docx.")
        print("Para generarlo: brew install pandoc")
        return

    md = os.path.join(comun.RAIZ, "reporte.md")
    docx = os.path.join(comun.RAIZ, "reporte.docx")
    subprocess.run(["pandoc", md, "-o", docx, "--resource-path", comun.RAIZ], check=True)
    print(f"DOCX generado: {docx}")


if __name__ == "__main__":
    main()

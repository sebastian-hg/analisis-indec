"""
08_exportar_pdf.py - Convierte reporte.md en reporte.pdf (y reporte.html).

Usa `markdown` para pasar el informe a HTML y `weasyprint` para generar el PDF
con un estilo prolijo (A4, tipografía, tablas e imágenes formateadas).

Requisitos del sistema (una sola vez, en Mac):
    brew install pango gdk-pixbuf libffi

Uso:  python src/08_exportar_pdf.py
"""

import os
# WeasyPrint necesita encontrar las librerías de Homebrew (Pango/Cairo).
os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib")

import markdown
from weasyprint import HTML
import comun

CSS = """
@page { size: A4; margin: 2.5cm; }
body { font-family: 'Times New Roman', Times, serif; font-size: 12pt;
       line-height: 1.5; color: #000; }
h1 { font-size: 16pt; text-align: center; margin-bottom: 4px; }
h2 { font-size: 13pt; margin-top: 20px; }
h3 { font-size: 12pt; margin-top: 14px; }
p, li { text-align: justify; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 11pt; }
th, td { border: 1px solid #000; padding: 4px 7px; }
th { font-weight: bold; text-align: left; }
img { max-width: 100%; max-height: 9.5cm; display: block; margin: 10px auto; }
blockquote { margin: 10px 0 10px 1.5em; font-style: italic; }
code { font-family: 'Courier New', monospace; font-size: 11pt; }
hr { border: none; border-top: 1px solid #000; margin: 16px 0; }
/* Evitar que tablas e imágenes se corten entre páginas */
table, img, blockquote { page-break-inside: avoid; }
h1, h2, h3 { page-break-after: avoid; }
"""


def main():
    md_path = os.path.join(comun.RAIZ, "reporte.md")
    html_path = os.path.join(comun.RAIZ, "reporte.html")
    pdf_path = os.path.join(comun.RAIZ, "reporte.pdf")

    with open(md_path, encoding="utf-8") as f:
        texto = f.read()

    cuerpo = markdown.markdown(texto, extensions=["tables", "extra", "sane_lists"])
    html = f"<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'>" \
           f"<style>{CSS}</style></head><body>{cuerpo}</body></html>"

    # Guardamos también el HTML (se puede abrir en el navegador e imprimir a PDF).
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # base_url = carpeta del proyecto, para que resuelva las imágenes output/graficos/*.
    HTML(string=html, base_url=comun.RAIZ).write_pdf(pdf_path)

    print(f"PDF generado: {pdf_path}")
    print(f"   HTML generado: {html_path}  (alternativa: abrir en el navegador)")


if __name__ == "__main__":
    main()

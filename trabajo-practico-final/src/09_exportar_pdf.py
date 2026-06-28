"""
08_exportar_pdf.py - Convierte reporte.md en reporte.pdf (y reporte.html).

Usa `markdown` para pasar el informe a HTML y `weasyprint` para generar el PDF
con un estilo prolijo (A4, tipografía, tablas e imágenes formateadas).

Requisitos del sistema (una sola vez, en Mac):
    brew install pango gdk-pixbuf libffi

Uso:  python src/08_exportar_pdf.py
"""

import os
# WeasyPrint necesita encontrar las librerias de Homebrew (Pango/Cairo) para
# poder dibujar el texto y generar el PDF; por eso le indicamos donde buscarlas.
os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib")

import markdown
from weasyprint import HTML
import comun

CSS = """
@page { size: A4; margin: 1.8cm; }
body { font-family: 'Times New Roman', Times, serif; font-size: 11.5pt;
       line-height: 1.34; color: #000; }
h1 { font-size: 15pt; text-align: center; margin-bottom: 4px; }
h2 { font-size: 13pt; margin-top: 16px; }
h3 { font-size: 11.5pt; margin-top: 12px; }
p, li { text-align: justify; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 10.5pt; }
th, td { border: 1px solid #000; padding: 3px 6px; }
th { font-weight: bold; text-align: left; }
img { max-width: 87%; max-height: 6.65cm; display: block; margin: 8px auto; }
blockquote { margin: 10px 0 10px 1.5em; font-style: italic; }
code { font-family: 'Courier New', monospace; font-size: 11pt; }
hr { border: none; border-top: 1px solid #000; margin: 16px 0; }
/* Evitar que imágenes y citas se corten entre páginas (las tablas sí pueden partirse) */
img, blockquote { page-break-inside: avoid; }
h1, h2, h3 { page-break-after: avoid; }
"""


def main():
    # Armamos las tres rutas: el informe de origen (Markdown) y los dos archivos
    # que vamos a generar a partir de el (la pagina HTML y el PDF final).
    ruta_markdown = os.path.join(comun.RAIZ, "reporte.md")
    ruta_html = os.path.join(comun.RAIZ, "reporte.html")
    ruta_pdf = os.path.join(comun.RAIZ, "reporte.pdf")

    # Leemos el texto completo del informe en Markdown.
    with open(ruta_markdown, encoding="utf-8") as archivo_markdown:
        texto_markdown = archivo_markdown.read()

    # Convertimos ese texto a HTML. Las extensiones permiten interpretar tablas,
    # listas y otros elementos del Markdown del informe.
    cuerpo_html = markdown.markdown(texto_markdown, extensions=["tables", "extra", "sane_lists"])

    # Envolvemos ese cuerpo en una pagina HTML completa, pegandole nuestro estilo
    # CSS para que se vea prolijo (tipografia, tablas, margenes, etc.).
    documento_html = f"<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'>" \
                     f"<style>{CSS}</style></head><body>{cuerpo_html}</body></html>"

    # Guardamos tambien el HTML (se puede abrir en el navegador e imprimir a PDF).
    with open(ruta_html, "w", encoding="utf-8") as archivo_html:
        archivo_html.write(documento_html)

    # base_url = carpeta del proyecto, para que resuelva las imagenes output/graficos/*.
    HTML(string=documento_html, base_url=comun.RAIZ).write_pdf(ruta_pdf)

    print(f"PDF generado: {ruta_pdf}")
    print(f"   HTML generado: {ruta_html}  (alternativa: abrir en el navegador)")


if __name__ == "__main__":
    main()

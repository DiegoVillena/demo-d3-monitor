"""Monitor de precios (demo D3): scrapea una categoría de books.toscrape.com
y añade los libros a data/prices.csv — una fila por (título, día UTC).

Ejecución: python scraper.py — idempotente (re-ejecutar el mismo día no
duplica filas). El Actions lo corre a diario y commitea el CSV si cambió.
"""

from __future__ import annotations

import csv
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# --- Configuración (el único punto que cambia de un cliente a otro) ---------
CATEGORIA_URL = "http://books.toscrape.com/catalogue/category/books/fiction_10/index.html"
CSV_PATH = Path(__file__).resolve().parent / "data" / "prices.csv"
PAUSA_ENTRE_PAGINAS = 0.7  # segundos entre página y página (sin martilleo)
USER_AGENT = (
    "demo-d3-monitor/1.0 (portfolio demo de Diego Villena; "
    "+https://github.com/DiegoVillena/demo-d3-monitor)"
)

CAMPOS = ["fecha", "titulo", "precio_gbp", "rating", "disponible", "url"]
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_pagina(html: str, url_pagina: str) -> tuple[list[dict], str | None]:
    """Extrae los libros de un listado de categoría y la URL de la siguiente
    página (None si no hay más). url_pagina resuelve los href relativos."""
    sopa = BeautifulSoup(html, "html.parser")
    libros = []
    for art in sopa.select("article.product_pod"):
        rating_clase = next(c for c in art.select_one("p.star-rating")["class"] if c in RATINGS)
        libros.append({
            "titulo": art.select_one("h3 > a")["title"],
            "precio_gbp": float(art.select_one("p.price_color").text.replace("£", "")),
            "rating": RATINGS[rating_clase],
            "disponible": art.select_one("p.instock").text.strip(),
            "url": urljoin(url_pagina, art.select_one("h3 > a")["href"]),
        })
    siguiente = sopa.select_one("li.next > a")
    return libros, (urljoin(url_pagina, siguiente["href"]) if siguiente else None)


def scrape_categoria(categoria_url: str) -> tuple[list[dict], int]:
    """Descarga y parsea todas las páginas de la categoría (siguiendo el
    enlace 'next' hasta agotar la paginación). Devuelve (libros, páginas)."""
    url, libros, paginas = categoria_url, [], 0
    while url:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        r.raise_for_status()
        # El Content-Type del sitio no declara charset y requests caería en
        # latin-1: el £ se corrompería ('Â£'). El HTML del sitio es UTF-8.
        r.encoding = "utf-8"
        paginas += 1
        page_libros, url = parse_pagina(r.text, url)
        libros += page_libros
        if url:
            time.sleep(PAUSA_ENTRE_PAGINAS)
    return libros, paginas


def append_csv(libros: list[dict], csv_path: Path, fecha: str) -> int:
    """Añade al CSV los libros que aún no tengan fila en esa fecha.

    Idempotente por (fecha, título): si el Actions corre dos veces el mismo
    día, no duplica. Devuelve el número de filas añadidas.
    """
    existentes = set()
    if csv_path.exists():
        with csv_path.open(encoding="utf-8", newline="") as f:
            existentes = {(fila["fecha"], fila["titulo"]) for fila in csv.DictReader(f)}
    nuevas = [libro for libro in libros if (fecha, libro["titulo"]) not in existentes]
    if not nuevas:
        return 0
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("a", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS)
        if not existentes:
            escritor.writeheader()
        escritor.writerows({"fecha": fecha, **libro} for libro in nuevas)
    return len(nuevas)


def contar_filas(csv_path: Path) -> int:
    """Filas de datos del CSV (sin la cabecera); 0 si aún no existe."""
    if not csv_path.exists():
        return 0
    with csv_path.open(encoding="utf-8", newline="") as f:
        return sum(1 for _ in csv.reader(f)) - 1


def main() -> int:
    hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Monitor de precios (demo D3) — {hoy}")
    print(f"  categoría: {CATEGORIA_URL}")
    libros, paginas = scrape_categoria(CATEGORIA_URL)
    anadidas = append_csv(libros, CSV_PATH, hoy)
    print(f"  páginas vistas: {paginas}")
    print(f"  libros vistos: {len(libros)}")
    print(f"  filas añadidas hoy: {anadidas}")
    print(f"  total filas del CSV: {contar_filas(CSV_PATH)} ({CSV_PATH})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
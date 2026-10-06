"""Tests del monitor de precios — SOLO HTML local, sin red (ficha D3 §5)."""

import csv
from pathlib import Path

import scraper

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "fiction-p1.html"


def test_parse_pagina_extrae_los_20_libros():
    html = FIXTURE.read_text(encoding="utf-8")

    libros, siguiente = scraper.parse_pagina(html, scraper.CATEGORIA_URL)

    assert len(libros) == 20
    assert siguiente == "http://books.toscrape.com/catalogue/category/books/fiction_10/page-2.html"

    # Primer libro del listado, verificado contra el sitio al generar el fixture
    primero = libros[0]
    assert primero["titulo"] == "Soumission"
    assert primero["precio_gbp"] == 50.10
    assert primero["rating"] == 1
    assert primero["disponible"] == "In stock"
    assert primero["url"] == "http://books.toscrape.com/catalogue/soumission_998/index.html"


def test_append_csv_es_idempotente(tmp_path):
    html = FIXTURE.read_text(encoding="utf-8")
    libros, _ = scraper.parse_pagina(html, scraper.CATEGORIA_URL)
    csv_path = tmp_path / "prices.csv"
    dia = "2026-10-05"

    # Primera corrida añade las 20; re-corrida el mismo día no duplica
    assert scraper.append_csv(libros, csv_path, dia) == 20
    assert scraper.append_csv(libros, csv_path, dia) == 0

    with csv_path.open(encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    assert len(filas) == 20
    assert filas[0]["fecha"] == dia
    assert filas[1]["titulo"] == libros[1]["titulo"]
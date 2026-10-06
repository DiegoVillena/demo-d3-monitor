# DOC-USO — Monitor de precios de libros (demo D3)

Guía de uso del scraper `scraper.py` — "Librería Meridiana" (negocio 100% ficticio;
los datos vienen de **books.toscrape.com**, un sitio público para practicar scraping).

---

## 1. Qué mira el monitor

La **categoría *Fiction*** de `books.toscrape.com`: **65 títulos** repartidos en
**4 páginas** que el scraper recorre solo, siguiendo el enlace "next". De cada
libro guarda 5 campos:

- **título** (el del listado de la categoría)
- **precio en GBP** (p. ej. `50.1` = £50.10 — sin el símbolo, para poder calcular)
- **rating** de 1 a 5 (que el sitio codifica como clase CSS: `One`…`Five`)
- **disponibilidad** (texto crudo del listado: `In stock`)
- **URL** de la ficha del libro

## 2. Cómo leer `data/prices.csv`

| Columna | Significado |
|---|---|
| `fecha` | Día de la corrida en **UTC** (`2026-10-05`) — la unicidad es por (fecha, título) |
| `titulo` | Título del libro |
| `precio_gbp` | Precio numérico (£, sin símbolo) |
| `rating` | 1-5 |
| `disponible` | `In stock` |
| `url` | Ficha del libro |

El archivo es un **append diario**: cada día añade 65 filas (una por título) y
nunca replica una fila existente del mismo día — si el Actions corre dos veces
(date + manual), la segunda añade **0**. El historial de commits del archivo es
toda la vida del monitor.

## 3. Correrlo localmente

```bash
python -m venv venv              # primera vez
source venv/Scripts/activate     # Windows Git Bash · Linux/macOS: venv/bin/activate
pip install -r requirements.txt  # primera vez
python scraper.py                # scrape + append del día al CSV
```

Salida esperada: nº de páginas vistas, libros vistos, filas añadidas hoy y total
del CSV. Vuelve a ejecutarlo en el mismo día: verás `filas añadidas hoy: 0` — eso
es la idempotencia trabajando.

## 4. Tests

```bash
pytest
```

Dos tests en verde: el parseo de una página real (guardada una vez como
`tests/fixtures/fiction-p1.html`) y la idempotencia del CSV. **Ningún test
lanza peticiones de red.**

## 5. Cambiar de categoría

Edita la constante `CATEGORIA_URL` al principio de `scraper.py` con la URL de la
categoría de books.toscrape.com que quieras (p. ej. la de *Travel*:
`http://books.toscrape.com/catalogue/category/books/travel_2/index.html`). El
scraper recorre solo la paginación de esa categoría (pausa de `PAUSA_ENTRE_PAGINAS`
segundos entre páginas).

Si quieres que la serie empiece de cero, borra `data/prices.csv` antes de la
primera corrida; sin borrarlo, los títulos de la nueva categoría se añaden al fin
del CSV (al ser títulos distintos no chocan con los anteriores).

## 6. El monitor automático (GitHub Actions)

El workflow `.github/workflows/monitor.yml` corre el scraper **a diario a las
~07:00 UTC** (cron `0 7 * * *`, mejor esfuerzo de GitHub: se retrasa algún minuto)
y, si el CSV cambió, **commitea la nueva fila de días** con el bot
`github-actions[bot]` — verás esos commits en el historial de `data/prices.csv`.

Para una corrida manual sin esperar el cron: pestaña **Actions** del repo →
"Monitor de precios" → **Run workflow**. El estado de la última ejecución es el
badge que hay al principio del README. No necesita ninguna clave: usa el
`GITHUB_TOKEN` estándar del workflow (`contents: write`).
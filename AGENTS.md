# AGENTS.md — demo-d3-monitor

Instrucciones para sesiones de ZCode (o cualquier agente) que trabajen en este repo.

## Qué es este proyecto
**Demo D3 de Operación Freelancer**: scraper + monitor programado sobre
**books.toscrape.com** (sitio público hecho para practicar scraping) que entrega
un **CSV histórico de precios** en este mismo repo, actualizado **cada día por
GitHub Actions**. Es la demo del servicio S3: *"monitor de precios que corre solo
y deja la serie histórica"*.

Requisitos: ficha congelada en
`C:\Users\Diego\Desktop\OperacionFreelancer\plantillas\ficha-d3.md` — trabajad
contra esa ficha. **El alcance NO se amplía** sin ficha nueva (fase B: Google
Sheet y alertas email → fuera).

## Stack
- **Python 3.11** en **venv local** (`venv/`): `requests`, `beautifulsoup4`,
  `pytest` — pins EXACTOS en `requirements.txt`. CSV con stdlib (sin pandas).
- **GitHub Actions**: `.github/workflows/monitor.yml` — `workflow_dispatch`
  (botón manual) + `schedule:` (cron diario ~07:00 UTC). El job corre el scraper
  y hace **commit automático del CSV si cambió** con `GITHUB_TOKEN`
  (`contents: write`). Cero claves externas.

## Cómo ejecutar (Windows, Git Bash)
```bash
python -m venv venv                     # primera vez
source venv/Scripts/activate            # Git Bash (en Linux/macOS: venv/bin/activate)
pip install -r requirements.txt         # primera vez
python scraper.py                       # scrape + append a data/prices.csv (idempotente)
pytest                                  # tests — NO lanzan peticiones de red
```

## Estructura
- `scraper.py` — constantes de configuración arriba (`CATEGORIA_URL`, `CSV_PATH`,
  `PAUSA_ENTRE_PAGINAS`): el punto de cambio para otra categoría.
- `tests/` — pytest sobre un **fixture HTML local** (`tests/fixtures/`), sin red.
- `data/prices.csv` — la serie histórica (append diario, idempotente por
  `(fecha UTC, título)`); la commitea el Actions cuando cambia.
- `.github/workflows/monitor.yml` — el monitor programado.

## Reglas de este proyecto (no negociables)
- **Commits/push solo con confirmación de Diego** — EXCEPCIÓN: el commit
  automático del CSV hecho por el bot del Actions (parte del diseño).
- **Los tests no hacen red** — parsean el fixture local.
- **Cero secretos commiteados** — solo el `GITHUB_TOKEN` estándar del Actions.
- Amabilidad con el sitio: User-Agent identificativo, 1 pasada diaria, pausa
  entre páginas, sin proxies/anti-bloqueo. Solo `books.toscrape.com`.
- Tras una tarea: actualizar la sección **Estado actual** de este archivo.

## Estado actual
- **Fase A TERMINADA**: repo público https://github.com/DiegoVillena/demo-d3-monitor
  (3 commits en `feat/fase-a-ficcion` mergeados a `main` + push). Corrida manual del
  Actions **en verde** (run #1) y badge "passing". Serie histórica: 2 días, 130 filas.
  En mesa: pulido local listo (banner de la corrida, bump `checkout@v7`/`setup-python@v7`,
  fixes del README) — pendiente de confirmación de Diego para el commit.
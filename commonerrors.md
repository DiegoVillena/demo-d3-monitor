# commonerrors.md — memoria de errores comunes (demo-d3-monitor)

Sesiones anteriores ya pisaron la piedra: si un problema no trivial te atasca
(bug oscuro, issue de configuración, cacheo, CI malhumorado), anótalo aquí al
final de la tarea como paso de documentación.

Formato: bullet conciso y categorizado — **síntoma → causa → solución**.
Lectura rápida al inicio de la siguiente sesión, sin prosa larga.

(Este archivo se creó vacío al iniciar la demo D3 — ya tiene su primera entrada abajo.)

## 2026-10-05 — Mojibake del £ en los precios (encoding de requests)
- **Síntoma:** `ValueError: could not convert string to float: 'Â50.10'` al parsear `price_color` de books.toscrape.com.
- **Causa:** el Content-Type del sitio no declara charset y `requests` decodifica con latin-1 por defecto: el `£` (bytes `0xC2 0xA3` en UTF-8) llega como `Â£`.
- **Solución:** fijar `r.encoding = "utf-8"` antes de leer `r.text` (el HTML del sitio es UTF-8) — en `scrape_categoria` de `scraper.py`.

## 2026-10-06 — El commit dijo más de lo que cambió (aviso persistente en Actions)
- **Síntoma:** la corrida #2 seguía lanzando el aviso "ubuntu-latest migrará a Ubuntu 26" tras un commit cuyo mensaje decía "runner ubuntu-24.04 fijo".
- **Causa:** apliqué solo el bump de las `uses` (v4/v5 → v7) y el mensaje del commit adelantaba el pin del runner que nunca llegué a editar.
- **Solución:** commit inmediato con el pin real (`runs-on: ubuntu-24.04`) + corrida de verificación sin anotaciones. Lección: contrastar el diff con lo que el mensaje promete ANTES de commitear; y no fiarse de campos jq que pueden venir vacíos para contar anotaciones — leer la sección de anotaciones del run.
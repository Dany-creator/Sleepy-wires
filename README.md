# Sleepy-wires — Design Evaluator

Resumen
-------
Proyecto para extraer métricas estructurales de diseños en Figma y evaluar cambios de UX/UI frente a un diseño de referencia. Soporta:
- Extracción de estructura desde la API de Figma
- Generación de un `reference_profile.json`
- Comparación basada en reglas deterministas y análisis por IA (Anthropic/Claude)
- Análisis visual opcional usando la API de OpenAI (usuario puede pegar su propia API key)
- Publicación de comentarios en Figma (opcional)

Instalación (requisitos)
------------------------
Recomendado: Python 3.10+ en un virtualenv. Dependencias principales:
- requests
- python-dotenv
- flask
- flask-cors
- openai
- anthropic

Puedes instalar paquetes básicos con:

```bash
pip install -r requirements.txt
```
(El repo no incluye `requirements.txt` por defecto; crear uno con las librerías arriba ayuda.)

Variables de entorno importantes
--------------------------------
Coloca estas variables en `.env` (o exportarlas en tu entorno):

- `FIGMA_TOKEN` — Token de API de Figma (obligatorio para extracción)
- `ANTHROPIC_KEY` — API key para Anthropic (opcional; si no existe se saltará la comparación AI)
- `REFERENCE_FILE_KEY` — File key de Figma usado como referencia (opcional, se puede pasar en interfaz)
- `REFERENCE_PREFIX` — Prefijo para filtrar frames de referencia (opcional)
- `OPENAI_API_KEY` — (opcional) para análisis visual por defecto; los usuarios también pueden pegar su propia key en la UI
- Opciones para reintentos Figma (opcional): `FIGMA_MAX_RETRIES`, `FIGMA_MAX_WAIT`, `FIGMA_TOTAL_WAIT_CAP`, `FIGMA_REQUEST_TIMEOUT`

Módulos y archivos (descripción exacta)
---------------------------------------
- `app.py` — Servidor Flask principal que sirve la UI (`templates/figma.html`) y expone endpoints:
  - `POST /api/evaluate` — evaluación completa basada en Figma (usa `evaluate.py`). Acepta `file_key`, `post_comments` y opcional `openai_key`.
  - `POST /api/evaluate_visual` — endpoint para subir dos imágenes (reference + candidate) y evaluar visualmente (acepta `openai_key` en `multipart/form-data`).

- `evaluate.py` — Pipeline orquestador que coordina extracción (si hace falta), generación de perfil y comparación. Firma actual: `evaluate_design(candidate_file_key, post_comments=True, openai_key=None)`.

- `extract_design.py` — Lógica para llamar a la API de Figma y recorrer el árbol JSON, extrayendo nodos TEXT, botones, inputs, indicadores de progreso y métricas por frame. Maneja reintentos, timeouts y tiene fallback a archivo cacheado.

- `generate_profile.py` — Lee frames (lista) y genera `reference_profile.json` con métricas agregadas: `step_count`, `avg_words_per_screen`, `word_count_range`, `avg_buttons_per_screen`, `button_consistency`, `progress_indicator_usage`, `avg_input_fields`, `component_usage`.

- `compare_designs.py` — Contiene integración con Anthropic/Claude para comparar dos perfiles y producir JSON con `deviations` y `overall_assessment`. También contiene scoring determinista (`calculate_score`).

- `post_to_figma.py` — Funciones para publicar comentarios en la API de Figma. Maneja errores y no publica si falta token.

- `evaluate_visual.py` — Pipeline para análisis visual (imagen a JSON y comparación) usando OpenAI Vision API. Ahora admite pasar `api_key` por llamada para que usuarios usen su propia cuenta.

- `config.py` — Centraliza lectura de `.env` y rutas por defecto (FIGMA_TOKEN, ANTHROPIC_KEY, REFERENCE_FILE_KEY, REFERENCE_PREFIX, paths, API base).

- `templates/figma.html` — UI principal (nuevo diseño). Permite subir imágenes, pegar OpenAI key opcional y lanzar evaluación visual.

- `templates/index.html` — UI alternativa (app anterior). Actualmente no es el punto de entrada principal si usas `figma.html`.

Archivos detectados en el repo
------------------------------
Listado actual (relevante):
- app.py
- app_visual.py
- evaluate.py
- evaluate_visual.py
- extract_design.py
- generate_profile.py
- compare_designs.py
- post_to_figma.py
- config.py
- cache_manager.py
- templates/figma.html
- templates/index.html

Archivos propuestos para eliminar (no esenciales)
-------------------------------------------------
Basado en la estructura actual y las rutas activas, propongo eliminar o archivar (si quieres) los siguientes archivos para simplificar el proyecto:

- `app_visual.py` — Variante previa de la app; `app.py` ya sirve `figma.html` y contiene los endpoints necesarios.
- `cache_manager.py` — No es crítico; la funcionalidad de cache/fallback está dentro de `extract_design.py` y `evaluate.py`.
- `templates/index.html` — Interfaz alternativa; si todas las rutas apuntan a `figma.html`, `index.html` puede eliminarse o moverse a `templates/legacy_index.html`.

Antes de borrar, recomiendo hacer un commit o mover a un folder `archive/`.

Cómo borrar (si confirmas)
--------------------------
Comandos (Windows PowerShell) para eliminar los archivos recomendados:

```powershell
# guardar cambios en git si aplica
git add -A && git commit -m "chore: backup before cleanup"
# borrar archivos
rm templates/index.html
rm app_visual.py
rm cache_manager.py
# o moverlos a archive/
mkdir archive
mv app_visual.py archive/
mv cache_manager.py archive/
mv templates/index.html archive/
```

Restauración
------------
Si usas `git`, puedes recuperar archivos con `git checkout -- <file>` o resetear a una commit anterior. Si no usas git, puedo mover los archivos a `archive/` en vez de borrarlos para mantener un backup.

Siguientes pasos (elige)
-----------------------
- [A] Crear `README.md` (hecho). Ahora: procedo a BORRAR los archivos propuestos.
- [B] Mover los archivos propuestos a `archive/` (recomendado si no quieres pérdida permanente).
- [C] No borrar nada; solo mantener README y marcar manualmente.

Dime si procedo con [A] borrar, [B] mover a `archive/`, o [C] no tocar archivos. Si eliges [A] o [B], procederé y actualizaré la lista de tareas.

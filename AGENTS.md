# Generador de Wikis (Obsidian + LLM · OKF v0.2) — Instrucciones del repositorio para agentes (Antigravity)

Este repositorio contiene la receta portable y estandarizada para construir y mantener una base de conocimiento viva estructurada como un **Knowledge Bundle conforme a Open Knowledge Format (OKF v0.2)** y materializada como **vault navegable de Obsidian**, siguiendo el principio fundacional de Karpathy:
> *"El LLM escribe y mantiene el wiki; el humano lee y pregunta."*

El wiki es un artefacto persistente que **se compone (compounding) con el tiempo**, adaptándose de forma **completamente agnóstica a cualquier dominio** (cursos universitarios, investigación técnica, productos, análisis de datos o proyectos personales).

- **Documentación del proceso y diagramas:** [`docs/PROCESO.md`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/docs/PROCESO.md)
- **Especificación canónica del estándar:** [`OKF-SPEC-v0.2.md`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/OKF-SPEC-v0.2.md)
- **README principal:** [`README.md`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/README.md)
- **Instrucciones heredadas (Claude Code):** [`CLAUDE.md`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/CLAUDE.md)

---

## 1. Entorno de ejecución y convenciones del agente

- **Plataforma:** Google Antigravity (CLI, IDE y entorno Desktop) y sistemas multi-agente autónomos compatibles.
- **Sistema Operativo y Shell:** Windows / PowerShell.
- **Herramientas nativas del agente:**
  - Emplear exclusivamente las herramientas del runtime (`view_file`, `write_to_file`, `replace_file_content`, `run_command`, `ask_question`, `list_dir`, `grep_search`, `find_by_name`).
  - **Prohibición de comandos `cd`:** No ejecutar `cd` interactivo en `run_command`. Especificar siempre el directorio de trabajo mediante el parámetro `Cwd` o usar rutas completas/relativas a la raíz del repositorio.
  - **Enlaces clickables en Markdown:** En cualquier salida o reporte, todos los enlaces a ficheros y símbolos del workspace deben usar la sintaxis clickable estándar con esquema `file:///` y barras normales `/` (ej. `[README.md](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/README.md)`).
- **Codificación:** UTF-8 estricto sin BOM en todos los ficheros `.md`, `.json`, `.py` y de configuración generados o actualizados.
- **Idioma:** Responder e interactuar en el idioma del usuario (por defecto, español en este repositorio).
- **Enrutamiento de skills locales:**
  - Las skills locales residen en [`.claude/skills/`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/.claude/skills/).
  - **No duplicar** estas carpetas en `.agents/skills/`. El agente debe consultar, orquestar y ejecutar los `SKILL.md` directamente desde su ubicación canónica:
    1. [`karpathy-llm-wiki`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/.claude/skills/karpathy-llm-wiki/SKILL.md): orquestador de ingesta, consultas, lint y ciclo de vida.
    2. [`obsidian-vault-builder`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/.claude/skills/obsidian-vault-builder/SKILL.md): andamiaje del vault y configuración `.obsidian/`.
    3. [`obsidian-graph-colors`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/.claude/skills/obsidian-graph-colors/SKILL.md): auditoría OKF y grupos de color del grafo.
- **Scripts y entorno Python:**
  - Python 3 (stdlib):
    - Generador de workspace: `python .claude/skills/obsidian-vault-builder/build_workspace.py`
    - Auditor de grafo y OKF: `python .claude/skills/obsidian-graph-colors/audit.py`
  - Extracción de PDFs: usar `pdfplumber` únicamente cuando el corpus contenga documentos PDF.

---

## 2. Modelo general e invariantes del repositorio

El sistema opera bajo una arquitectura desacoplada de cuatro capas unidas **por fichero y no por estado en memoria** (`sources/` → `raw/` → `wiki/` → `wiki/.obsidian/`):

```
corpus de fuentes (PDF/DOCX/web/notas)          🔒 Inmutable (Read-Only)
        │  extracción determinista a texto plano
        ▼
raw/<topic>/YYYY-MM-DD-slug.md                  🔒 Inmutable una vez creado
        │  compilación OKF v0.2 (type, sources, footnotes, generated)
        ▼
wiki/ (OKF v0.2 Knowledge Bundle)               ← Propiedad plena del agente LLM
  ├── index.md (okf_version: "0.2")
  ├── log.md (ISO 8601 audit history)
  └── <topic>/<concept>.md (un solo nivel de subdirectorios)
        │
        ▼
wiki/.obsidian/ (graph.json, app.json...)       ← Configuración (⚠ Obsidian cerrado)
```

### Invariantes críticas de seguridad
1. **Fuentes originales inalterables:** Los ficheros binarios o crudos de las fuentes jamás se modifican, renombran ni eliminan.
2. **`raw/` inmutable:** Los archivos de texto extraídos en `raw/<topic>/` no se sobreescriben una vez generados. Cualquier re-compilación del wiki se realiza siempre desde `raw/`, nunca re-extrayendo el binario.
3. **Subdirectorios planos en `wiki/`:** Se admite **un único nivel** de carpetas por topic bajo `wiki/` (`wiki/<topic>/<concept>.md`). No anidar tópicos.
4. **Regla de oro de Obsidian:** **Obsidian debe estar cerrado** antes de editar `wiki/.obsidian/graph.json`. Si Obsidian estuviera abierto al modificarlo, sobreescribirá el JSON desde memoria descartando los cambios.
5. **Prohibido editar `workspace.json` a mano:** Dicho fichero contiene UUIDs y estructuras internas complejas; se genera siempre mediante `build_workspace.py`.

### Autonomía operativa
- **Autónomo (proceder sin interrupción):** Extracción de texto a `raw/`, verificación estructural de documentos, compilación de conceptos en `wiki/`, cascade updates de conceptos vinculados, actualización rutinaria de `wiki/index.md` y `wiki/log.md`, resolución de consultas (Query) y ejecución de auditorías con `audit.py`.
- **Detenerse y solicitar confirmación (`ask_question`):**
  - Si no existe certeza sobre el topic al que pertenece una fuente y no hay topic previo afín.
  - Si se detecta un vault preexistente al invocar bootstrap y se requiere sobrescribir.
  - Confirmación explícita del usuario de que Obsidian está cerrado antes de escribir en `.obsidian/graph.json`.

---

## 3. Categorías principales y procedimientos paso a paso

### 3.0. Protocolo de inicialización de sesión
Al iniciar cualquier sesión en este repositorio, el agente debe:
1. Leer este archivo canónico ([`AGENTS.md`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/AGENTS.md)).
2. Consultar el skill orquestador ([`.claude/skills/karpathy-llm-wiki/SKILL.md`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/.claude/skills/karpathy-llm-wiki/SKILL.md)).
3. Leer [`wiki/index.md`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/wiki/index.md) para orientarse sobre el estado actual del vault si ya existe.
4. Si la carpeta `wiki/` no existe, ofrecer al usuario realizar el **bootstrap inicial** delegando en `obsidian-vault-builder`.

---

### 3.1. Bootstrap del Vault (`obsidian-vault-builder`)
- **Disparadores:** *"bootstrap vault"*, *"crear vault"*, *"nuevo vault obsidian"*, *"inicializar wiki"*.
- **Cadencia:** Una sola vez por proyecto o al reiniciar el vault.
- **Procedimiento:**
  1. Verificar que Obsidian esté cerrado (advertir al usuario).
  2. Comprobar la existencia del directorio destino (`wiki/`).
  3. Crear `wiki/.obsidian/`.
  4. Copiar `.claude/skills/obsidian-vault-builder/templates/app.json` → `wiki/.obsidian/app.json` (garantiza `"useMarkdownLinks": true`).
  5. Escribir `wiki/.obsidian/appearance.json` (`{}`).
  6. Configurar `core-plugins.json` (perfiles: `minimal`, `full`, `bayesiano` [default]).
  7. Instalar plantilla de grafo `graph.json` (elegir `vacio` para nuevos dominios no bayesianos).
  8. Generar `workspace.json` ejecutando:
     ```powershell
     python .claude/skills/obsidian-vault-builder/build_workspace.py --layout graph-center --out wiki/.obsidian/workspace.json
     ```
  9. Inicializar archivos reservados OKF v0.2:
     - `wiki/index.md`:
       ```markdown
       ---
       okf_version: "0.2"
       ---

       # Topics
       ```
     - `wiki/log.md`:
       ```markdown
       # Directory Update Log
       ```

---

### 3.2. Bucle de Ingesta (`karpathy-llm-wiki`)
- **Disparadores:** *"add to wiki"*, *"ingesta esta fuente"*, *"build a wiki"*, *"agrega este documento"*.
- **Cadencia:** Recurrente (una pasada completa por cada documento o fuente).
- **Procedimiento:**

#### Paso 1: Fetch (`raw/`)
1. Extraer fuentes binarias a texto plano (usar `pdfplumber` para PDF si aplica).
2. **Verificar estructura:** Comprobar que los encabezados de sección correspondan fielmente al contenido substantivo real. Si hay discrepancias, documentarlo en los metadatos de `raw/` (`note: <rotulo>-pertenece-a-<otra-seccion>`).
3. Nombrar y guardar en `raw/<topic>/YYYY-MM-DD-slug.md` incluyendo cabecera con URL/ruta de origen, fecha de recolección, autor/organización y notas estructurales.

#### Paso 2: Compile (OKF v0.2 en `wiki/`)
Determinar el destino del contenido:
- **Misma tesis que concepto existente:** Realizar merge, actualizar `sources:`, refrescar `generated.at`.
- **Nuevo concepto:** Crear `wiki/<topic>/<concept-name>.md`.
- **Múltiples temas:** Asignar al topic primario y añadir enlaces cruzados en la sección `## See Also`.
- **Fórmulas o queries ejecutables:** Crear documento con `type: Attested Computation`.

**Esquema obligatorio de Frontmatter OKF v0.2:**
```markdown
---
type: Concept                      # OBLIGATORIO: Concept | Playbook | Metric | Reference | Attested Computation
title: Nombre del Concepto         # Recomendado: título legible
description: Resumen en una frase. # Recomendado: frase concisa
resource: https://canonico.ejemplo # Opcional: URI del activo físico subyacente
tags: [topico-tag]                 # Controla los colores del Graph View en Obsidian
status: stable                     # draft | stable | deprecated (default: stable)
stale_after: 2027-01-01            # Opcional: fecha ISO límite de frescura
generated:
  by: antigravity/gemini-2.5-pro   # OBLIGATORIO: sintaxis de actor <productor>/<modelo>
  at: 2026-09-19T09:30:00Z         # ISO 8601 UTC
sources:                           # Proveniencia obligatoria
  - id: id-fuente-estable          # ID para footnote markdown [^id-fuente-estable]
    resource: ../../raw/topico/2026-09-19-documento.md
    title: Título de la Fuente
    author: Autor u Organización
    last_modified: 2026-09-19
---

# Nombre del Concepto

## Resumen
Afirmación central extraída de la fuente acreditada con trazabilidad.[^id-fuente-estable]

## See Also
- [Concepto Relacionado](../otro-topic/otro-concepto.md)

[^id-fuente-estable]: Autor u Organización, *Título de la Fuente* (2026).
```

#### Paso 3: Cascade Updates
Escanear conceptos existentes que se vean afectados por el nuevo conocimiento. Actualizar su texto, refresh de `generated.at` e incorporar cross-references en `## See Also`.

#### Paso 4: Post-Ingest (Archivos reservados)
1. **Actualizar [`wiki/index.md`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/wiki/index.md):** Mantener lista agrupada bajo encabezados de topic (§8 OKF):
   ```markdown
   ---
   okf_version: "0.2"
   ---

   # Topic
   * [Nombre del Concepto](topic/concepto.md) - Resumen en una frase.
   ```
2. **Registrar en [`wiki/log.md`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/wiki/log.md):** Cabecera de fecha ISO 8601 con prefijos estructurados de acción (§9 OKF):
   ```markdown
   ## YYYY-MM-DD
   * **Creation**: Ingested [Nombre del Concepto](topic/concepto.md) from [id-fuente-estable].
   * **Update**: Cascade update to [Concepto Relacionado](topic/relacionado.md).
   ```

---

### 3.3. Consultas y Síntesis (Query)
- **Disparadores:** *"¿qué sé de X?"*, *"what do I know about X?"*, *"compara A y B según el wiki"*.
- **Procedimiento:**
  1. Consultar `wiki/index.md` para ubicar conceptos relevantes.
  2. Leer los conceptos en disco y sintetizar la respuesta anteponiendo el contenido del wiki a memorias previas.
  3. Citar siempre usando enlaces Markdown estándar: `[Título](topic/articulo.md)`.
  4. **Modo no destructivo:** Query **no escribe** en disco por defecto.
  5. **Archivado explícito:** Si el usuario solicita archivar la respuesta, guardar como nuevo concepto (`type: Synthesis` o `type: Note`) en el topic correspondiente con frontmatter OKF v0.2, actualizar `wiki/index.md` (prefijo `[Archived]`) y registrar en `wiki/log.md`.

---

### 3.4. Auditoría y Control de Calidad (Lint & OKF Conformance)
- **Disparadores:** *"lint del wiki"*, *"auditar okf"*, *"verificar coherencia"*.
- **Procedimiento:**
  - **Corrección determinista (auto-fix):**
    - Verificar presencia de `type:` no vacío en todo `.md` no reservado (asignar `type: Concept` si faltara).
    - Migrar metadatos antiguos (`updated:` → `generated: { by, at }`, `raw:` → `sources[].resource`).
    - Validar que cada footnote `[^id]` tenga su objeto correspondiente en `sources:`.
    - Reparar enlaces rotos y registrar entradas huérfanas en `wiki/index.md`.
  - **Detección heurística (reporte):**
    - Detectar contradicciones entre notas, conceptos con fecha posterior a `stale_after`, conceptos en borrador (`status: draft`) y notas huérfanas sin backlinks.
  - **Registro en log:**
    ```markdown
    ## YYYY-MM-DD
    * **Lint**: Completed OKF audit. <N> issues found, <M> auto-fixed.
    ```

---

### 3.5. Mantenimiento y Colores del Grafo (`obsidian-graph-colors`)
- **Disparadores:** *"/graph-colors"*, *"colorear el grafo"*, *"grupos de color"*, *"asignar colores por tag"*.
- **Procedimiento:**
  1. **Auditoría inicial:** Ejecutar siempre el script de diagnóstico:
     ```powershell
     python .claude/skills/obsidian-graph-colors/audit.py --okf-check
     ```
  2. Evaluar anomalías reportadas: `[SIN COLOR]`, `[HUÉRFANO]`, `[ESPACIOS]`, `[DUPLICADO]`.
  3. Convertir colores hexadecimales a formato RGB decimal requerido por Obsidian:
     $$\text{Decimal} = (R \times 65536) + (G \times 256) + B$$
  4. **Pausa de seguridad:** Comprobar y confirmar con el usuario que Obsidian está cerrado.
  5. Actualizar `wiki/.obsidian/graph.json` en la clave `colorGroups` preservando el resto de propiedades de simulación física.
  6. Re-ejecutar `audit.py` para certificar la consistencia del grafo resultante.

---

## 4. Otras categorías y estructura del workspace

- [`docs/PROCESO.md`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/docs/PROCESO.md): Guía de arquitectura conceptual, ciclo de vida y diagramas de flujo.
- [`docs/svg/`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/docs/svg/): Diagramas vectoriales del pipeline, artefactos y operaciones.
- [`OKF-SPEC-v0.2.md`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/OKF-SPEC-v0.2.md): Especificación normativa de referencia de Open Knowledge Format.
- [`Audit-AntiGravity/`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/Audit-AntiGravity/): Registro histórico de auditorías de conformidad y notas técnicas.
- [`wiki/references/`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/wiki/references/): Directorio opcional para atestadores de cómputo (`type: Attested Computation`), scripts de verificación o activos reproducibles.

### Procedimiento para dar de alta nuevos topics
1. Convenir con el usuario un nombre de topic en minúsculas y formato slug (ej. `redes-complejas`).
2. Crear la carpeta correspondiente con un solo nivel: `raw/<topic>/` y `wiki/<topic>/`.
3. Asignar un tag canónico idéntico al topic (`#redes-complejas`).
4. Añadir una nueva sección en `wiki/index.md` con el encabezado `# <Nombre del Topic>`.
5. Asignar un color distintivo al tag mediante `obsidian-graph-colors`.

---

## 5. Criterios de aceptación (Definition of Done)

Toda tarea ejecutada en el repositorio por un agente se considera completada únicamente si cumple rigurosamente con los siguientes puntos:

1. **Invariabilidad de fuentes y `raw/`:** Las fuentes originales no han sido alteradas y los documentos en `raw/` mantienen fidelidad al texto extraído con sus metadatos de origen.
2. **Conformidad OKF v0.2 estricta:**
   - Todo fichero en `wiki/<topic>/` incluye bloque frontmatter YAML delimitado por `---`.
   - Campo obligatorio `type:` presente y válido (`Concept`, `Playbook`, `Metric`, `Reference`, `Attested Computation`, `Synthesis`).
   - Bloque `generated:` con identificador de actor (`by: antigravity/...`) y timestamp ISO 8601 UTC (`at:`).
   - Bloque `sources:` estructurado (`id`, `resource`, `title`, `author`, `last_modified`).
   - Citas internas per-claim formalizadas mediante footnotes markdown `[^id]` enlazadas con `sources[].id`.
3. **Enlaces y navegación estándar:** Todos los vínculos internos utilizan enlaces Markdown estándar relativos (`[Título](../topic/doc.md)` o `[Título](topic/doc.md)`), compatibles con `"useMarkdownLinks": true`.
4. **Sincronización de índices y registros:**
   - [`wiki/index.md`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/wiki/index.md) contiene `okf_version: "0.2"` en su frontmatter y refleja cada nuevo concepto con su enlace y descripción.
   - [`wiki/log.md`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/wiki/log.md) contiene la entrada cronológica bajo fecha `## YYYY-MM-DD` con prefijos normativos (`**Creation**:`, `**Update**:`, `**Lint**:`, `**Deprecation**:`).
5. **Obsidian & Graph Integrity:** No se ha editado manualmente `workspace.json` y cualquier actualización de `graph.json` se ha ejecutado con Obsidian cerrado y validada con `audit.py`.
6. **No regresión:** [`CLAUDE.md`](file:///C:/Users/brjap/Documents/__CODE_gpu/_ToolKits%20&%20ARTEFACTOS/obsidian-llm-wiki/CLAUDE.md) permanece intacto para garantizar compatibilidad con Claude Code.

# CLAUDE.md — Generador de Wikis (Obsidian + LLM · OKF v0.2)

## Rol

Eres un **agente constructor de bases de conocimiento**. Mantienes un **Knowledge Bundle conforme a Open Knowledge Format (OKF v0.2)** como vault de Obsidian a partir de un corpus de fuentes, siguiendo el principio de Karpathy: **el LLM escribe y mantiene el wiki; el humano lee y pregunta**. El wiki es un artefacto que **se compone (compounding) con el tiempo**.

Este repositorio es **domain-agnostic**: sirve para cualquier tema. Adáptate al dominio del corpus que te den; no asumas una asignatura ni un campo concreto.

## Skills

El proceso se apoya en tres skills (en `.claude/skills/`). Lee su `SKILL.md` antes de operar.

| Skill | Cuándo | Qué hace |
|---|---|---|
| `obsidian-vault-builder` | una vez, al empezar | crea `wiki/` (OKF `index.md`, `log.md`) + `.obsidian/` sin abrir Obsidian |
| `karpathy-llm-wiki` | punto de entrada · recurrente | Ingest / Query / Lint (conforme a OKF v0.2); orquesta a los otros dos |
| `obsidian-graph-colors` | mantenimiento | colores del Graph view por tags |

## Inicialización de sesión

En cada nueva sesión, antes de cualquier otra cosa:

1. Leer este archivo (`CLAUDE.md`).
2. Leer `.claude/skills/karpathy-llm-wiki/SKILL.md` (el skill orquestador).
3. Leer `wiki/index.md` para orientarte al estado actual del wiki (si ya existe).
4. Si no existe `wiki/`, ofrecer el **bootstrap** con `obsidian-vault-builder`.

## Arquitectura de capas (inmutabilidad y OKF)

- **Corpus de fuentes** — originales (PDF/DOCX/web/notas). 🔒 **Nunca** se modifican.
- **`raw/<topic>/`** — texto extraído de cada fuente. 🔒 **Inmutable una vez creado**; el wiki se recompone desde aquí, nunca se re-extrae el binario.
- **`wiki/<topic>/`** — conceptos compilados como **OKF v0.2 Knowledge Bundle** + `index.md` (`okf_version: "0.2"`) + `log.md`. Propiedad plena del agente.
- **`wiki/.obsidian/`** — config del vault (`useMarkdownLinks: true`, `graph.json`…). Editar **solo con Obsidian cerrado**.

## Reglas de comportamiento y conformidad OKF v0.2

- Responde en el idioma del usuario.
- **Frontmatter obligatorio OKF v0.2** en cada concepto `.md`:
  - `type:` (OBLIGATORIO: `Concept`, `Metric`, `Playbook`, `Reference`, `Attested Computation`, etc.).
  - `title:` y `description:` recomendados.
  - `tags:` para categorías y colores del grafo.
  - `generated:` `{ by: claude-code/<model>, at: <ISO-8601-UTC> }` (actor convention).
  - `sources:` lista de objetos `{ id, resource, title, author, last_modified }`.
- **Atribución de afirmaciones**: usar footnotes markdown `[^source-id]` asociadas a `sources[].id`.
- Cada **Ingest** ejecuta **siempre** Fetch (a `raw/`) **y** Compile (a `wiki/`), y actualiza `index.md` (formato lista agrupada §8) + `log.md` (formato fechas ISO §9). Sin excepción.
- **Verifica la estructura de la fuente** antes de compilar: que los rótulos de sección describan de verdad el contenido.
- Al responder consultas (**Query**), **cita** los conceptos del wiki con enlaces markdown estándar (`[Título](topic/articulo.md)` o `/topic/articulo.md`). Query **no escribe** ficheros salvo que se pida archivar.
- **Obsidian cerrado** antes de editar `graph.json`. **Nunca** edites `workspace.json` a mano.
- `wiki/` admite **un solo nivel** de subdirectorios de topic.

## Documentación del proceso

El diseño completo (visión, artefactos, operaciones, topología bootstrap+bucle+mantenimiento, checklist de portabilidad, triggers y decisiones) está en `docs/PROCESO.md`, con especificación canónica en `OKF-SPEC-v0.2.md`.

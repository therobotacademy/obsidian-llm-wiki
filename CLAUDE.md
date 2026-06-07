# CLAUDE.md — Generador de Wikis (Obsidian + LLM)

## Rol

Eres un **agente constructor de bases de conocimiento**. Mantienes un **wiki persistente** como
vault de Obsidian a partir de un corpus de fuentes, siguiendo el principio de Karpathy: **el LLM
escribe y mantiene el wiki; el humano lee y pregunta**. El wiki es un artefacto que **se compone
(compounding) con el tiempo**.

Este repositorio es **domain-agnostic**: sirve para cualquier tema. Adáptate al dominio del corpus
que te den; no asumas una asignatura ni un campo concreto.

## Skills

El proceso se apoya en tres skills (en `.claude/skills/`). Lee su `SKILL.md` antes de operar.

| Skill | Cuándo | Qué hace |
|---|---|---|
| `obsidian-vault-builder` | una vez, al empezar | crea `wiki/` + `.obsidian/` sin abrir Obsidian |
| `karpathy-llm-wiki` | punto de entrada · recurrente | Ingest / Query / Lint; orquesta a los otros dos |
| `obsidian-graph-colors` | mantenimiento | colores del Graph view por tags |

## Inicialización de sesión

En cada nueva sesión, antes de cualquier otra cosa:

1. Leer este archivo (`CLAUDE.md`).
2. Leer `.claude/skills/karpathy-llm-wiki/SKILL.md` (el skill orquestador).
3. Leer `wiki/index.md` para orientarte al estado actual del wiki (si ya existe).
4. Si no existe `wiki/`, ofrecer el **bootstrap** con `obsidian-vault-builder`.

## Arquitectura de capas (inmutabilidad)

- **Corpus de fuentes** — originales (PDF/DOCX/web/notas). 🔒 **Nunca** se modifican.
- **`raw/<topic>/`** — texto extraído de cada fuente. 🔒 **Inmutable una vez creado**; el wiki se
  recompone desde aquí, nunca se re-extrae el binario.
- **`wiki/<topic>/`** — artículos compilados + `index.md` + `log.md`. Propiedad plena del agente.
- **`wiki/.obsidian/`** — config del vault. Editar **solo con Obsidian cerrado**.

## Reglas de comportamiento

- Responde en el idioma del usuario.
- Cada **Ingest** ejecuta **siempre** Fetch (a `raw/`) **y** Compile (a `wiki/`), y actualiza
  `index.md` + `log.md`. Sin excepción.
- **Verifica la estructura de la fuente** antes de compilar: que los rótulos de sección describan de
  verdad el contenido (algunos materiales desplazan o reetiquetan secciones).
- Al responder consultas (**Query**), **cita** los artículos del wiki; prefiere el wiki a tu
  conocimiento de entrenamiento. Query **no escribe** ficheros salvo que se pida archivar.
- **Obsidian cerrado** antes de editar `graph.json`. **Nunca** edites `workspace.json` a mano.
- `wiki/` admite **un solo nivel** de subdirectorios de topic.
- Etiqueta cada artículo con un `tag` por topic en el frontmatter — es lo que conecta el artículo
  con el color del grafo.

## Documentación del proceso

El diseño completo (visión, artefactos, operaciones, topología bootstrap+bucle+mantenimiento,
checklist de portabilidad, triggers y decisiones) está en `docs/PROCESO.md`, con diagramas en
`docs/svg/`.

# Generador de Wikis — Obsidian + LLM

Una **receta portable** para construir y mantener una base de conocimiento personal como **vault de
Obsidian**, usando un LLM (vía [Claude Code](https://claude.com/claude-code)) que escribe el wiki
mientras tú lees y preguntas. Funciona para **cualquier dominio**: un curso, un campo de
investigación, un producto, un interés personal.

> *"The LLM writes and maintains the wiki; the human reads and asks questions."* — A. Karpathy

El proceso encadena **tres skills** acoplados por fichero (ninguno lee la salida en memoria del
otro; se comunican a través de artefactos en disco, lo que lo hace **reanudable y auditable**):

| Skill | Rol | Cadencia |
|---|---|---|
| [`obsidian-vault-builder`](.claude/skills/obsidian-vault-builder/SKILL.md) | crea el vault y su config `.obsidian/` sin abrir Obsidian | **bootstrap** (una vez) |
| [`karpathy-llm-wiki`](.claude/skills/karpathy-llm-wiki/SKILL.md) | ingiere fuentes, responde consultas, hace lint; **orquesta** a los otros dos | **bucle** (por fuente) |
| [`obsidian-graph-colors`](.claude/skills/obsidian-graph-colors/SKILL.md) | colorea el Graph view por los tags del frontmatter | **mantenimiento** |

`karpathy-llm-wiki` es el **punto de entrada**: delega el bootstrap en `obsidian-vault-builder` y el
coloreado en `obsidian-graph-colors`.

## Arquitectura en cuatro capas

```
corpus de fuentes (PDF/DOCX/web/notas)   🔒 inmutable, read-only
        │  extracción a texto (p.ej. pdfplumber)
        ▼
raw/<topic>/YYYY-MM-DD-slug.md           🔒 inmutable una vez creado
        │  compile (merge / new / cross-topic)
        ▼
wiki/<topic>/articulo.md + index.md + log.md     ← propiedad del LLM, «compounding»
        │
        ▼
wiki/.obsidian/graph.json                ← config (⚠ editar con Obsidian cerrado)
```

## Quick start

1. **Requisitos:** [Obsidian](https://obsidian.md), [Claude Code](https://claude.com/claude-code),
   Python 3 (los scripts de los skills usan solo stdlib) y, opcional, `pdfplumber` para extraer PDFs
   (`pip install pdfplumber`).
2. Abre esta carpeta con Claude Code. Los tres skills se autodescubren en `.claude/skills/`.
3. **Bootstrap del vault** (una vez): *"bootstrap vault"* → `obsidian-vault-builder` crea `wiki/` +
   `.obsidian/` (te pregunta perfil de plugins y layout). Con Obsidian cerrado.
4. **Ingesta** (por cada fuente): *"add this to the wiki"* / *"ingesta esta fuente"* →
   `karpathy-llm-wiki` extrae la fuente a `raw/`, compila el artículo en `wiki/` y actualiza
   `index.md` + `log.md`.
5. **Colorea el grafo:** etiqueta cada artículo con un `tag` por topic y pide *"colorea el grafo"* →
   `obsidian-graph-colors` escribe los `colorGroups` en `graph.json` (Obsidian cerrado).
6. **Consume:** *"what do I know about X?"* → Query sintetiza y cita desde el wiki; *"lint del wiki"*
   revisa la higiene. Tus preguntas guían qué ingestar a continuación.

## Portar a un dominio nuevo

El checklist completo (6 pasos) está en [`docs/PROCESO.md` §7](docs/PROCESO.md). En resumen: define
topics → bootstrap → reúne el corpus → ingesta iterativa → tag + color → consume. **Ningún paso
depende del dominio concreto.**

## Documentación

- [`docs/PROCESO.md`](docs/PROCESO.md) — el proceso completo (visión, artefactos, operaciones,
  topología, portabilidad, triggers, decisiones de diseño) con cuatro diagramas en `docs/svg/`.

## Reglas de Obsidian (importantes)

- **Obsidian debe estar cerrado** al editar `graph.json` externamente; si está abierto, vuelca su
  estado en memoria y revierte el cambio.
- **`workspace.json` no se edita a mano:** `obsidian-vault-builder` lo genera con un script.

## Créditos y licencia

El skill `karpathy-llm-wiki` deriva de [Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki)
(MIT), aquí enriquecido con el ciclo de vida del vault y la delegación en los skills compañeros.
Publicado bajo licencia MIT — ver [`LICENSE`](LICENSE).

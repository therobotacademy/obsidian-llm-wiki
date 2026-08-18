# Generador de Wikis — Obsidian + LLM (OKF v0.2)

Una **receta portable** para construir y mantener una base de conocimiento estructurada como un **Knowledge Bundle conforme a Open Knowledge Format (OKF v0.2)** y materializada como **vault de Obsidian**, usando un LLM (vía [Claude Code](https://claude.com/claude-code)) que escribe el wiki mientras tú lees y preguntas. Funciona para **cualquier dominio**: un curso, un campo de investigación, un producto, un interés personal.

> *"The LLM writes and maintains the wiki; the human reads and asks questions."* — A. Karpathy

El proceso encadena **tres skills** acoplados por fichero (ninguno lee la salida en memoria del otro; se comunican a través de artefactos en disco, lo que lo hace **reanudable y auditable**):

| Skill | Rol | Cadencia |
|---|---|---|
| [`obsidian-vault-builder`](.claude/skills/obsidian-vault-builder/SKILL.md) | crea el vault, archivos OKF y su config `.obsidian/` sin abrir Obsidian | **bootstrap** (una vez) |
| [`karpathy-llm-wiki`](.claude/skills/karpathy-llm-wiki/SKILL.md) | ingiere fuentes (conforme a OKF v0.2), responde consultas, hace lint/auditoría; **orquesta** a los otros dos | **bucle** (por fuente) |
| [`obsidian-graph-colors`](.claude/skills/obsidian-graph-colors/SKILL.md) | audita conformidad OKF y colorea el Graph view por tags del frontmatter | **mantenimiento** |

`karpathy-llm-wiki` es el **punto de entrada**: delega el bootstrap en `obsidian-vault-builder` y el coloreado en `obsidian-graph-colors`.

## Arquitectura en cuatro capas (OKF v0.2)

```
corpus de fuentes (PDF/DOCX/web/notas)          🔒 inmutable, read-only
        │  extracción a texto (p.ej. pdfplumber)
        ▼
raw/<topic>/YYYY-MM-DD-slug.md                  🔒 inmutable una vez creado
        │  compilación OKF v0.2 (type, sources, generated, footnotes)
        ▼
wiki/ (OKF v0.2 Knowledge Bundle)               ← propiedad del LLM, «compounding»
  ├── index.md (okf_version: "0.2")
  ├── log.md (ISO 8601 audit history)
  └── <topic>/<concept>.md
        │
        ▼
wiki/.obsidian/ (graph.json, app.json...)       ← config (⚠ editar con Obsidian cerrado)
```

## Características OKF v0.2

- **Conformidad Estándar (§11)**: Cada documento incluye `type:` (`Concept`, `Metric`, `Playbook`, `Reference`, `Attested Computation`, etc.).
- **Trazabilidad y Proveniencia (§5.1)**: Lista estructurada `sources:` con identificadores estables y atribución mediante footnotes (`[^id]`).
- **Niveles de Confianza (§5.2, §5.3)**: Metadatos `generated: { by, at }` y `verified: [{ by, at }]` con convención de actores.
- **Cómputos Atestados (§10)**: Soporte de contratos de ejecución determinista (`type: Attested Computation`, `runtime`, `parameters`, `executor`, `attester`).
- **Portabilidad de Enlaces (§6.1)**: Enlaces markdown estándar compatibles con herramientas deterministas y visores web.

## Quick start

1. **Requisitos:** [Obsidian](https://obsidian.md), [Claude Code](https://claude.com/claude-code), Python 3 con solo stdlib; instalar `pdfplumber` únicamente si hay PDFs en el corpus (`pip install pdfplumber`).
2. Abre esta carpeta con Claude Code. Los tres skills se autodescubren en `.claude/skills/`.
3. **Bootstrap del vault** (una vez): *"bootstrap vault"* → `obsidian-vault-builder` crea `wiki/` + `.obsidian/` (configurando `useMarkdownLinks: true`, `index.md` con `okf_version: "0.2"` y `log.md`). Con Obsidian cerrado.
4. **Ingesta** (por cada fuente): *"add this to the wiki"* / *"ingesta esta fuente"* → `karpathy-llm-wiki` extrae la fuente a `raw/`, compila el concepto en `wiki/` con frontmatter OKF v0.2 y actualiza `index.md` + `log.md`.
5. **Colorea el grafo:** etiqueta cada concepto con un `tag` por topic y pide *"colorea el grafo"* → `obsidian-graph-colors` escribe los `colorGroups` en `graph.json` (Obsidian cerrado).
6. **Consume:** *"what do I know about X?"* → Query sintetiza y cita desde el wiki; *"lint del wiki"* revisa la higiene y conformidad OKF v0.2. Tus preguntas guían qué ingestar a continuación.

## Portar a un dominio nuevo

El checklist completo (6 pasos) está en [`docs/PROCESO.md` §7](docs/PROCESO.md). En resumen: define topics → bootstrap → reúne el corpus → ingesta iterativa → tag + color → consume. **Ningún paso depende del dominio concreto.**

## Documentación

- [`docs/PROCESO.md`](docs/PROCESO.md) — el proceso completo (visión, artefactos, operaciones, topología, portabilidad, triggers, decisiones de diseño) con cuatro diagramas en `docs/svg/`.
- [`OKF-SPEC-v0.2.md`](OKF-SPEC-v0.2.md) — especificación canónica del Open Knowledge Format v0.2.

## Reglas de Obsidian (importantes)

- **Obsidian debe estar cerrado** al editar `graph.json` externamente; si está abierto, vuelca su estado en memoria y revierte el cambio.
- **`workspace.json` no se edita a mano:** `obsidian-vault-builder` lo genera con un script.

## Créditos y licencia

El skill `karpathy-llm-wiki` deriva de [Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki) (MIT), aquí enriquecido con el ciclo de vida del vault, la conformidad con OKF v0.2 y la delegación en los skills compañeros. Publicado bajo licencia MIT — ver [`LICENSE`](LICENSE).

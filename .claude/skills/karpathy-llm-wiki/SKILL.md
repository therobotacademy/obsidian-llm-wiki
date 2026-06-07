---
name: karpathy-llm-wiki
description: Build and maintain a personal, LLM-powered Obsidian knowledge base for any domain. This skill is the entry point for the whole vault lifecycle — it bootstraps the vault, ingests sources, answers queries, lints quality, and keeps the graph colored — delegating vault scaffolding to obsidian-vault-builder and graph coloring to obsidian-graph-colors. Triggers: 'build a wiki', 'bootstrap a vault', ingesting sources into a wiki, querying wiki knowledge, linting wiki quality, 'add to wiki', 'what do I know about', or any mention of 'LLM wiki' or 'Karpathy wiki'.
---

# Karpathy LLM Wiki

Build and maintain a personal knowledge base using LLMs, materialized as an **Obsidian vault**. This skill is the **orchestrator** of a three-skill family: it owns the knowledge (ingest, query, lint) and **delegates** the two ends of the vault lifecycle — scaffolding and graph coloring — to its companion skills. Sources go into `raw/`, you compile them into `wiki/` articles, and the wiki compounds over time.

Core ideas from Karpathy:

* "The LLM writes and maintains the wiki; the human reads and asks questions."
* "The wiki is a persistent, compounding artifact."

This skill is **domain-agnostic**: the same recipe builds a wiki for a university course, a research field, a product, or a personal interest. Nothing below is tied to a specific subject — see §*Porting to a new domain* at the end.

---

## The vault lifecycle (orchestration)

The process is **not a linear pipeline**. It has three phases with different cadences:

| Phase | Cadence | Skill | What happens |
|---|---|---|---|
| **0 · Bootstrap** | once | `obsidian-vault-builder` *(delegated)* | scaffold `wiki/` + `.obsidian/` config without opening Obsidian |
| **1 · Ingest loop** | recurring (one pass per source) | **karpathy-llm-wiki** *(this skill)* | Fetch → Compile → Cascade → Post-ingest; the wiki grows incrementally |
| **2 · Maintenance** | on demand | **karpathy-llm-wiki** (Lint, Query) + `obsidian-graph-colors` *(delegated)* | quality checks, answer questions, recolor the graph by tag |

Coupling between phases is **by file, not by code** (`raw/` → `wiki/` → `.obsidian/graph.json`), which makes the whole process resumable and auditable.

---

## Architecture

Four layers, all under the user's project root:

**sources/** (or any immutable source corpus) — Original material exactly as received (PDFs, DOCX, slide decks, web captures, notes). You read, never modify. May live anywhere the user keeps originals; this skill treats it as read-only.

**raw/** — Extracted, plain-text representation of each source. Immutable once created. For opaque/binary sources you extract text into this layer first (see Fetch). Organized by topic subdirectories (e.g., `raw/<topic>/`). The wiki is always recompiled from `raw/`, never re-extracted from the binary.

**wiki/** — Compiled knowledge articles. You have full ownership. Organized by topic subdirectories, one level only: `wiki/<topic>/<article>.md`. Contains two special files:

* `wiki/index.md` — Global index. One row per article, grouped by topic, with link + summary + Updated date.
* `wiki/log.md` — Append-only operation log (vault-internal only; see Conventions).

**wiki/.obsidian/** — Vault configuration (`graph.json`, plugins, layout). Scaffolded by `obsidian-vault-builder`; the `colorGroups` are owned by `obsidian-graph-colors`. Edit only with Obsidian closed.

**SKILL.md** (this file) — Schema layer. Defines structure and workflow rules.

---

## Phase 0 — Bootstrap (delegate)

Run **once**, before the first ingest, when no vault exists yet.

**Do not hand-write `.obsidian/`.** Delegate to `obsidian-vault-builder` ("bootstrap vault"), which creates the five `.obsidian/` JSON files (`app.json`, `appearance.json`, `core-plugins.json`, `graph.json`, `workspace.json`) from validated templates. It will ask for a plugin profile, a graph template, a layout, and an initial file. Confirm Obsidian is closed first.

After bootstrap you own `wiki/` and may create the first topic subdirectory plus `index.md` and `log.md`. If a vault already exists, skip this phase.

---

## Phase 1 — Ingest

Fetch a source into `raw/`, then compile it into `wiki/`. Always both steps, no exceptions.

### Fetch (raw/)

1. Get the source content using whatever web or file tools your environment provides. If nothing can reach the source, ask the user to paste it directly.
2. **Extract opaque/binary sources to text first.** For PDFs, DOCX, slide decks, or scans, run an extractor (e.g. `pdfplumber` for PDFs) and save the **extracted plain text** as the `raw/` artifact. The `raw/` file is the immutable text representation; the binary original stays in the source layer.
3. **Verify the source's structure before compiling.** Confirm that section headings/labels actually describe the content beneath them. Some publishers mislabel or offset sections (e.g. a "key ideas" summary that actually recaps the *previous* chapter). On mismatch: note it in the `raw/` file's metadata (`note: <heading>-belongs-to-<other-section>`) and compile from the **real substantive content**, not the label.
4. Pick a topic directory. Check existing `raw/` subdirectories first; reuse one if the topic is close enough. Create a new subdirectory only for genuinely distinct topics.
5. Save as `raw/<topic>/YYYY-MM-DD-descriptive-slug.md`.
   * Slug from source title, kebab-case, max 60 characters.
   * Published date unknown → omit date prefix. Metadata Published field = `Unknown`.
   * If file with same name exists, append numeric suffix.
   * Include metadata header: source URL/path, collected date, published date, and any structure note from step 3.
   * Preserve original text. Clean formatting noise. Do not rewrite opinions.

### Compile (wiki/)

Determine where the new content belongs:

* **Same core thesis as existing article** → Merge into that article. Add the new source to Sources/Raw. Update affected sections.
* **New concept** → Create a new article in the most relevant topic directory. Name the file after the concept, not the raw file.
* **Spans multiple topics** → Place in the most relevant directory. Add See Also cross-references.

If the new source contradicts existing content, annotate the disagreement with source attribution.

**Article format:**

```markdown
---
title: [Concept Name]
topic: [directory name]
tags: [topic-tag]          # drives graph coloring (see Phase 2)
sources: [Author/Org, Date; Author/Org, Date]
raw: [../../raw/topic/file.md]
updated: YYYY-MM-DD
---

# [Concept Name]

## Summary
[2-3 sentence overview]

## [Section]
[Content]

## See Also
- [Related Article](../topic/article.md)
```

Add at least one `tags:` entry per article (typically one per topic). The graph's color groups key off these tags, so consistent tagging is what makes Phase 2 work.

### Cascade Updates

After the primary article, check for ripple effects in related articles. Update every article whose content is materially affected. Refresh their Updated date.

### Post-Ingest

Update `wiki/index.md`: add or update entries for every touched article.

Index row format:
```
| [Article Title](topic/article.md) | [One-line summary] | YYYY-MM-DD |
```

Append to `wiki/log.md`:
```
## [YYYY-MM-DD] ingest | <primary article title>
- Updated: <cascade-updated article title>
```

---

## Phase 2 — Query, Lint, and graph maintenance

### Query

Search the wiki and answer questions. Triggers: "What do I know about X?", "Summarize everything related to Y", "Compare A and B based on my wiki".

1. Read `wiki/index.md` to locate relevant articles.
2. Read those articles and synthesize an answer.
3. Prefer wiki content over training knowledge. Cite sources: `[Article Title](wiki/topic/article.md)`.
4. Output in conversation. Do not write files unless asked.

**Archiving.** When the user asks to archive the answer:

1. Write as new wiki page in the most relevant topic directory.
2. Update `wiki/index.md` with `[Archived]` prefix in summary.
3. Append to `wiki/log.md`: `## [YYYY-MM-DD] query | Archived: <page title>`

### Lint

Quality checks. Two categories.

**Deterministic (auto-fix):**

* **Index consistency** — file exists but missing from index → add entry. Index entry points to nonexistent file → mark `[MISSING]`.
* **Internal links** — broken link → search wiki/ for same filename. One match → fix. Zero/multiple → report.
* **Raw references** — broken Raw field link → search raw/ for same filename. One match → fix. Zero/multiple → report.
* **See Also** — add obvious missing cross-references. Remove links to deleted files.

**Heuristic (report only):**

* Factual contradictions across articles
* Outdated claims superseded by newer sources
* Orphan pages with no inbound links
* Concepts frequently mentioned but lacking a dedicated page

Post-lint log: `## [YYYY-MM-DD] lint | <N> issues found, <M> auto-fixed`

### Graph maintenance (delegate)

Coloring the Graph view by topic is delegated to `obsidian-graph-colors` ("color the graph"). It keys color groups off the `tags:` in article frontmatter and writes `colorGroups` into `graph.json` as decimal RGB (`R×65536 + G×256 + B`).

Two hard constraints (the skill enforces them, but know them):

* **Obsidian must be closed** when editing `graph.json`. An open Obsidian flushes its in-memory state to disk and reverts external edits.
* **Never hand-edit `workspace.json`.** Obsidian generates its own UUIDs and accented text; a malformed external `workspace.json` makes Obsidian reject it and reset `graph.json` too.

---

## Conventions

* Standard markdown with relative links.
* `wiki/` supports one level of topic subdirectories only. No deeper nesting.
* Inside wiki/ files: paths relative to current file. In conversation output: project-root-relative paths.
* Ingest updates both `wiki/index.md` and `wiki/log.md`. Plain queries do not write files.
* **Immutability invariants:** the source corpus is never modified; `raw/` files are immutable once created (recompile the wiki from `raw/`, never re-extract); `wiki/` is fully owned by this skill.
* **`wiki/log.md` is strictly vault-internal:** it records only vault operations (ingest, query, lint, graph-colors). Process/skill engineering work (code changes, pipeline decisions) belongs in the project's session logs, not here. *(Defer to the project's own CLAUDE.md if it states otherwise.)*

---

## Companion skills

| Task | Skill | Role |
|---|---|---|
| Create / reconfigure `.obsidian/` (bootstrap) | `obsidian-vault-builder` | Phase 0 — scaffolding (once) |
| Ingest / Query / Lint the knowledge | **karpathy-llm-wiki** *(this skill)* | Phase 1–2 — the core loop |
| Color the Graph view by tag | `obsidian-graph-colors` | Phase 2 — maintenance |

This skill is the entry point; it calls the other two at the moments shown above. The three stay modular and coupled only by files on disk.

---

## Porting to a new domain

To stand up a wiki for a new subject, reuse the recipe unchanged:

1. **Define topics** — the `wiki/<topic>/` subdirectories (one level) and a tag per topic.
2. **Bootstrap** — `obsidian-vault-builder` scaffolds the vault (plugin profile + layout).
3. **Gather the source corpus** — keep originals immutable; extract opaque sources to `raw/`.
4. **Ingest iteratively** — one Fetch+Compile pass per source; the wiki compounds.
5. **Tag + color** — consistent `tags:` per topic, then `obsidian-graph-colors` paints the graph.
6. **Consume** — Query for answers, Lint for hygiene; the human's questions guide what to ingest next.

---

*Source: https://github.com/Astro-Han/karpathy-llm-wiki — MIT License*
*Installed: 2026-04-30 · Enriched: 2026-06-06 — vault lifecycle (bootstrap → ingest loop → maintenance), companion-skill delegation (obsidian-vault-builder, obsidian-graph-colors), and generalized source-extraction / editorial-check / immutability conventions. Documented as a portable process in `docs/PROCESO.md`.*

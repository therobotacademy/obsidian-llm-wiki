---
name: karpathy-llm-wiki
description: Build and maintain a personal, LLM-powered knowledge base adhering to the Open Knowledge Format (OKF v0.2) and materialized as an Obsidian vault. This skill is the entry point for the whole vault lifecycle — it bootstraps the vault, ingests sources, answers queries, lints quality and OKF conformance, and keeps the graph colored — delegating vault scaffolding to obsidian-vault-builder and graph coloring to obsidian-graph-colors. Triggers: 'build a wiki', 'bootstrap a vault', ingesting sources into a wiki, querying wiki knowledge, linting wiki quality, 'add to wiki', 'what do I know about', 'OKF', or any mention of 'LLM wiki' or 'Karpathy wiki'.
---

# Karpathy LLM Wiki (OKF v0.2 Compatible)

Build and maintain a personal knowledge base using LLMs, structured as an **Open Knowledge Format (OKF v0.2) Knowledge Bundle** and materialized as an **Obsidian vault**. This skill is the **orchestrator** of a three-skill family: it owns the knowledge (ingest, query, lint) and **delegates** the two ends of the vault lifecycle — scaffolding and graph coloring — to its companion skills. Sources go into `raw/`, you compile them into `wiki/` concepts, and the knowledge bundle compounds over time.

Core ideas from Karpathy & OKF:

* "The LLM writes and maintains the wiki; the human reads and asks questions."
* "The wiki is a persistent, compounding artifact."
* "Knowledge is self-describing, trustable, provenance-tracked, and portable across tools and agents." (OKF v0.2)

This skill is **domain-agnostic**: the same recipe builds a wiki for a university course, a research field, a product, or a personal interest. Nothing below is tied to a specific subject — see §*Porting to a new domain* at the end.

---

## The vault lifecycle (orchestration)

The process is **not a linear pipeline**. It has three phases with different cadences:

| Phase | Cadence | Skill | What happens |
|---|---|---|---|
| **0 · Bootstrap** | once | `obsidian-vault-builder` *(delegated)* | scaffold `wiki/` (with OKF `index.md` & `log.md`) + `.obsidian/` config without opening Obsidian |
| **1 · Ingest loop** | recurring (one pass per source) | **karpathy-llm-wiki** *(this skill)* | Fetch → Compile (OKF v0.2) → Cascade → Post-ingest; the bundle grows incrementally |
| **2 · Maintenance** | on demand | **karpathy-llm-wiki** (Lint/OKF Conformance, Query) + `obsidian-graph-colors` *(delegated)* | quality & OKF checks, answer questions, recolor graph by tags/topics |

Coupling between phases is **by file, not by code** (`raw/` → `wiki/` → `.obsidian/graph.json`), which makes the whole process resumable and auditable.

---

## Architecture & OKF Mapping

Four layers, all under the user's project root:

1. **sources/** (or any immutable source corpus) — Original material exactly as received (PDFs, DOCX, slide decks, web captures, notes). You read, never modify. Treated as read-only external assets.
2. **raw/** — Extracted, plain-text representation of each source. Immutable once created. For opaque/binary sources you extract text into this layer first (see Fetch). Organized by topic subdirectories (e.g., `raw/<topic>/`). The wiki is always recompiled from `raw/`, never re-extracted from binary originals.
3. **wiki/** — **The OKF Knowledge Bundle** (and Obsidian Vault root). Compiled concepts and articles. You have full ownership. Organized by topic subdirectories, one level only: `wiki/<topic>/<concept>.md`. Contains reserved files:
   * `wiki/index.md` — Bundle root index with `okf_version: "0.2"`. Grouped list of concepts with descriptions.
   * `wiki/log.md` — Chronological update log in OKF ISO 8601 date format.
   * `wiki/references/` (optional) — Mirrored external references, run instructions, scripts, or attesters.
4. **wiki/.obsidian/** — Vault configuration (`graph.json`, `app.json` with `useMarkdownLinks: true`, plugins, layout). Scaffolded by `obsidian-vault-builder`; `colorGroups` owned by `obsidian-graph-colors`. Edit only with Obsidian closed.

---

## Phase 0 — Bootstrap (delegate)

Run **once**, before the first ingest, when no vault exists yet.

**Do not hand-write `.obsidian/`.** Delegate to `obsidian-vault-builder` ("bootstrap vault"), which creates:
- The five `.obsidian/` JSON files (`app.json`, `appearance.json`, `core-plugins.json`, `graph.json`, `workspace.json`).
- The root `wiki/index.md` with `okf_version: "0.2"` frontmatter.
- The initial `wiki/log.md` header.

Confirm Obsidian is closed first. After bootstrap, `wiki/` is ready for topic creation and concept compilation.

---

## Phase 1 — Ingest

Fetch a source into `raw/`, then compile it into `wiki/`. Always both steps, no exceptions.

### Fetch (raw/)

1. Get the source content using whatever web or file tools your environment provides. If nothing can reach the source, ask the user to paste it directly.
2. **Extract opaque/binary sources to text first.** For PDFs, DOCX, slide decks, or scans, run an extractor (e.g. `pdfplumber` for PDFs) and save the **extracted plain text** as the `raw/` artifact.
3. **Verify the source's structure before compiling.** Confirm that section headings/labels actually describe the content beneath them. On mismatch: note it in the `raw/` file's metadata (`note: <heading>-belongs-to-<other-section>`) and compile from the **real substantive content**, not the label.
4. Pick a topic directory. Check existing `raw/` subdirectories first; reuse one if close enough.
5. Save as `raw/<topic>/YYYY-MM-DD-descriptive-slug.md`.
   * Include metadata header: source URL/path, collected date, published date, author/org, and any structure notes.
   * Preserve original text. Clean formatting noise. Do not rewrite opinions.

### Compile (wiki/)

Determine where the new content belongs:

* **Same core thesis as existing concept** → Merge into that concept document. Add the new source to `sources:`. Update affected sections and refresh `generated.at`.
* **New concept** → Create a new concept file in the most relevant topic directory (`wiki/<topic>/<concept-name>.md`).
* **Spans multiple topics** → Place in the primary topic directory. Add cross-references in `## See Also`.
* **Executable computation / sanctioned formula** → Create a dedicated `type: Attested Computation` concept (see below).

If the new source contradicts existing content, annotate the disagreement with source attribution.

#### Standard OKF v0.2 Concept Format

Every concept document in `wiki/` must contain valid YAML frontmatter conforming to OKF v0.2:

```markdown
---
type: Concept                      # REQUIRED: Concept | Playbook | Metric | Reference | Attested Computation
title: Customer Lifetime Value     # Recommended: human-readable display title
description: Metric and calculation model for customer long-term value. # Recommended: single sentence
resource: https://analytics.corp/metrics/clv  # Optional: canonical URI of underlying physical asset
tags: [metrics, finance]           # Drives Obsidian Graph View coloring
status: stable                     # draft | stable | deprecated (default: stable)
stale_after: 2027-01-01            # Optional: ISO date when content should be re-verified
generated:
  by: karpathy-llm-wiki/claude-code # REQUIRED within generated: Actor format <producer>/<version>
  at: 2026-08-18T12:00:00Z         # ISO 8601 UTC timestamp
verified:                          # Optional: trust tier events
  - by: human:reviewer-id
    at: 2026-08-18T14:00:00Z
sources:                           # Provenance: structured list of source materials
  - id: clv-whitepaper             # Stable ID for per-claim footnote attribution
    resource: ../../raw/metrics/2026-05-10-clv-whitepaper.md # Bundle-relative or relative path / URL
    title: Customer Lifetime Value Whitepaper
    author: Analytics Team
    last_modified: 2026-05-10
---

# Customer Lifetime Value

## Summary
Customer Lifetime Value (CLV) represents the total net revenue a customer generates over their relationship.[^clv-whitepaper]

## Calculation Model
The core predictive equation integrates churn hazard rate and average revenue per user (ARPU).[^clv-whitepaper]

## See Also
- [Customer Churn Rate](../metrics/churn-rate.md)
- [ARPU Model](../metrics/arpu.md)

[^clv-whitepaper]: Analytics Team, *Customer Lifetime Value Whitepaper* (2026).
```

#### Actor Convention (§7)
- Agents: `<producer>/<version>` (e.g. `karpathy-llm-wiki/claude-code`, `claude-code/sonnet-3.7`).
- Humans: `human:<id>` (e.g. `human:admin`, `human:brjap`).
- Automated processes: `process:<id>` (e.g. `process:nightly-sync`).

#### Per-Claim Footnote Attribution (§5.1)
Use markdown footnotes keyed to `sources[].id` (`[^source-id]`) for citing specific claims in the text. This allows deterministic provenance resolution.

#### Attested Computations Concept Format (§10)
When capturing sanctioned calculations, SQL queries, or data formulas:

```markdown
---
type: Attested Computation
title: Monthly Active Users Calculation
description: Sanctioned BigQuery SQL query to compute MAU.
status: stable
runtime: bigquery
parameters:
  - { name: target_month, type: string, required: true }
executor:
  resource: references/skills/run-bq.md
  receipt: [job_id, executed_sql, result]
attester:
  resource: references/attesters/sql-equality.py
generated:
  by: karpathy-llm-wiki/claude-code
  at: 2026-08-18T12:00:00Z
sources:
  - id: mau-definition
    resource: https://wiki.corp/definitions/mau
    title: MAU Official Standard
---

# Computation

    SELECT COUNT(DISTINCT user_id) AS mau
    FROM analytics.user_events
    WHERE event_month = @target_month

The computation binds `target_month` according to the standard definition.[^mau-definition]

[^mau-definition]: MAU Official Standard
```

### Cascade Updates

After updating the primary concept, scan related concepts for ripple effects. Update affected documents, refresh their `generated.at` timestamps, and add cross-references where appropriate.

### Post-Ingest

1. **Update `wiki/index.md`**:
   The bundle index follows OKF v0.2 §8 (grouped list under section headings, with descriptions):

   ```markdown
   ---
   okf_version: "0.2"
   ---

   # Metrics

   * [Customer Lifetime Value](metrics/customer-lifetime-value.md) - Metric and calculation model for customer long-term value.
   * [Customer Churn Rate](metrics/churn-rate.md) - Monthly percentage of customer contract terminations.

   # Architecture

   * [Data Pipeline Overview](architecture/data-pipeline.md) - End-to-end ingestion and ETL architecture.
   ```

2. **Append to `wiki/log.md`**:
   The log follows OKF v0.2 §9 (ISO 8601 date heading with bulleted action prefixes):

   ```markdown
   # Directory Update Log

   ## YYYY-MM-DD
   * **Creation**: Ingested [Customer Lifetime Value](metrics/customer-lifetime-value.md) from [clv-whitepaper].
   * **Update**: Cascade update to [Customer Churn Rate](metrics/churn-rate.md).
   ```

---

## Phase 2 — Query, Lint, and Graph Maintenance

### Query

Search the wiki and answer questions. Triggers: "What do I know about X?", "Summarize everything related to Y", "Compare A and B based on my wiki".

1. Read `wiki/index.md` to locate relevant concepts.
2. Read those concepts and synthesize an answer.
3. Prefer wiki content over general training knowledge. Cite concepts using standard markdown links: `[Title](topic/concept.md)`.
4. Output in conversation. Do not write files unless explicitly asked to archive.

**Archiving Answers**:
When asked to archive:
1. Write as a new concept file (`type: Synthesis` or `type: Note`) in the most relevant topic directory with full OKF v0.2 frontmatter.
2. Update `wiki/index.md` with `[Archived]` prefix in description.
3. Append to `wiki/log.md`: `* **Creation**: Archived query response [Title](topic/concept.md).`

### Lint & OKF Conformance

Quality and specification checks.

**Deterministic (auto-fix):**
* **OKF Conformance**:
  - Verify every non-reserved `.md` has valid YAML frontmatter containing a non-empty `type:` field (if missing, default to `type: Concept`).
  - Auto-migrate legacy `updated: YYYY-MM-DD` to `generated: { by: karpathy-llm-wiki/claude-code, at: YYYY-MM-DDT00:00:00Z }`.
  - Auto-migrate legacy `raw: [path]` into `sources: [{ id: raw-source, resource: path }]`.
  - Ensure root `wiki/index.md` contains `okf_version: "0.2"` frontmatter.
* **Footnote & Provenance Integrity**:
  - Every `[^id]` footnote in body must match an `id` in `sources`. Report unreferenced sources or orphan footnotes.
* **Index consistency**:
  - File exists in `wiki/` but missing from `index.md` → add entry with description.
  - Index entry points to nonexistent file → mark `[MISSING]` or remove.
* **Internal links & sources**:
  - Broken link → search `wiki/` or `raw/` for matching filename; 1 match → auto-fix; 0/multiple → report.
* **See Also**:
  - Add missing reciprocal cross-references; clean up links to deleted files.

**Heuristic (report only):**
* Factual contradictions across concepts.
* Stale concepts where current date $\ge$ `stale_after`.
* Unverified draft concepts (`status: draft`).
* Orphan pages with no inbound links.
* Missing pages for frequently mentioned terms.

**Post-lint log**:
Append to `wiki/log.md`:
```markdown
## YYYY-MM-DD
* **Lint**: Completed OKF audit. <N> issues found, <M> auto-fixed.
```

### Graph Maintenance (delegate)

Coloring the Obsidian Graph view is delegated to `obsidian-graph-colors` ("color the graph"). It maps `tags:` from concept frontmatter to `colorGroups` in `graph.json` as decimal RGB (`R×65536 + G×256 + B`).

Constraints:
* **Obsidian must be closed** when editing `graph.json`.
* **Never hand-edit `workspace.json`.**

---

## Conventions & Invariants

* **OKF Conformance**: All concepts must have `type:`, `generated: { by, at }`, and structured `sources:`.
* **Standard Markdown Links**: Use relative paths `[Target](../topic/concept.md)` or bundle-relative paths `[Target](/topic/concept.md)`.
* **One Level of Topic Subdirectories**: `wiki/<topic>/<concept>.md`.
* **Immutability Invariants**:
  - `sources/` is strictly read-only.
  - `raw/` is immutable once created.
  - `wiki/` is fully maintained by the LLM and user.
* **`wiki/log.md` is strictly vault-internal**: Records knowledge operations (Creation, Update, Deprecation, Lint).

---

## Porting to a New Domain

1. **Define topics** — subdirectories `wiki/<topic>/` and a tag per topic.
2. **Bootstrap** — `obsidian-vault-builder` scaffolds the vault + OKF `index.md` & `log.md`.
3. **Gather source corpus** — keep originals immutable; extract text to `raw/`.
4. **Ingest iteratively** — one Fetch+Compile pass per source; bundle compounds with OKF provenance.
5. **Tag + color** — consistent `tags:` per topic, then `obsidian-graph-colors` paints the graph.
6. **Consume** — Query for answers, Lint for OKF conformance & quality.

---

*Open Knowledge Format (OKF v0.2) compliant · Derived from Astro-Han/karpathy-llm-wiki (MIT License)*

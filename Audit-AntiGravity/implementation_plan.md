# Implementation Plan — OKF v0.2 Compatibility

Adapt the repository and its three skills (`karpathy-llm-wiki`, `obsidian-graph-colors`, `obsidian-vault-builder`) to produce and maintain **Open Knowledge Format (OKF) v0.2** compliant Knowledge Bundles as Obsidian vaults.

## User Review Required

> [!NOTE]
> All changes preserve complete backwards-compatibility with Obsidian and the Karpathy compounding wiki methodology while aligning with the normative requirements of [OKF-SPEC-v0.2.md](file:///c:/Users/brjap/Documents/__CODE_gpu/_2027-xGNN-obsidian-llm-wiki/OKF-SPEC-v0.2.md).

## Proposed Changes

### Core Orchestrator Skill & Rules

#### [MODIFY] [.claude/skills/karpathy-llm-wiki/SKILL.md](file:///c:/Users/brjap/Documents/__CODE_gpu/_2027-xGNN-obsidian-llm-wiki/.claude/skills/karpathy-llm-wiki/SKILL.md)
- Replace article frontmatter schema with OKF v0.2 standard (`type`, `title`, `description`, `tags`, `status`, `generated: { by, at }`, `verified`, `sources: [{ id, resource, title, author, usage_count, last_modified }]`, `stale_after`).
- Deprecate custom `raw:` field in favor of `sources[].resource`.
- Migrate `wiki/index.md` format from markdown table to OKF §8 list grouped under headings (`* [Title](relative-url) - description`) with root `okf_version: "0.2"`.
- Migrate `wiki/log.md` format from operational headings to OKF §9 ISO 8601 date headings (`## YYYY-MM-DD`) with structured action bullets (`* **Creation**: ...`, `* **Update**: ...`).
- Add per-claim attribution convention using footnotes `[^source-id]` keyed to `sources[].id`.
- Add Attested Computations (`type: Attested Computation`, `# Computation`) handling.
- Expand Lint rules with deterministic OKF conformance validation and auto-fixing of legacy fields.

#### [MODIFY] [CLAUDE.md](file:///c:/Users/brjap/Documents/__CODE_gpu/_2027-xGNN-obsidian-llm-wiki/CLAUDE.md)
- Update system rules for article creation, frontmatter schema (`type`, `generated`, `sources`), actor convention (`claude-code/<model>`), and OKF-compliant `index.md`/`log.md`.

---

### Graph Colors & Audit Tooling

#### [MODIFY] [.claude/skills/obsidian-graph-colors/audit.py](file:///c:/Users/brjap/Documents/__CODE_gpu/_2027-xGNN-obsidian-llm-wiki/.claude/skills/obsidian-graph-colors/audit.py)
- Make frontmatter parser robust to complex OKF v0.2 YAML frontmatter blocks.
- Add `--okf-check` audit flag to validate OKF v0.2 conformance (missing `type`, invalid YAML, unlinked footnote keys, legacy fields).

#### [MODIFY] [.claude/skills/obsidian-graph-colors/SKILL.md](file:///c:/Users/brjap/Documents/__CODE_gpu/_2027-xGNN-obsidian-llm-wiki/.claude/skills/obsidian-graph-colors/SKILL.md)
- Document OKF compatibility and the `--okf-check` feature.

---

### Obsidian Vault Builder & Templates

#### [NEW] [.claude/skills/obsidian-vault-builder/templates/app.json](file:///c:/Users/brjap/Documents/__CODE_gpu/_2027-xGNN-obsidian-llm-wiki/.claude/skills/obsidian-vault-builder/templates/app.json)
- Default config template with `"useMarkdownLinks": true` to ensure Obsidian creates standard markdown links.

#### [MODIFY] [.claude/skills/obsidian-vault-builder/SKILL.md](file:///c:/Users/brjap/Documents/__CODE_gpu/_2027-xGNN-obsidian-llm-wiki/.claude/skills/obsidian-vault-builder/SKILL.md)
- Update bootstrap documentation to include `app.json` template and initialization of OKF v0.2 `wiki/index.md` (`okf_version: "0.2"`) and `wiki/log.md`.

---

### Documentation & Overview

#### [MODIFY] [README.md](file:///c:/Users/brjap/Documents/__CODE_gpu/_2027-xGNN-obsidian-llm-wiki/README.md)
- Update architecture explanation: explain that the wiki is an OKF v0.2 Knowledge Bundle.
- Update quickstart instructions, article format example, and features.

#### [MODIFY] [docs/PROCESO.md](file:///c:/Users/brjap/Documents/__CODE_gpu/_2027-xGNN-obsidian-llm-wiki/docs/PROCESO.md)
- Update process documentation, article schemas, provenance and trust layers, Attested Computations, and OKF v0.2 compatibility checklist.

#### [MODIFY] [docs/PROCESO.html](file:///c:/Users/brjap/Documents/__CODE_gpu/_2027-xGNN-obsidian-llm-wiki/docs/PROCESO.html)
- Regenerate HTML export from `docs/PROCESO.md`.

---

## Verification Plan

### Automated Tests
1. Run `python .claude/skills/obsidian-graph-colors/audit.py --help` / `audit.py` with mock / sample OKF vault to verify frontmatter extraction and `--okf-check`.
2. Run `python .claude/skills/obsidian-vault-builder/build_workspace.py --help` to ensure script sanity.
3. Validate YAML frontmatter in all updated markdown files and templates.

### Manual Verification
- Inspect generated files and verify 100% adherence to all sections of `OKF-SPEC-v0.2.md`.

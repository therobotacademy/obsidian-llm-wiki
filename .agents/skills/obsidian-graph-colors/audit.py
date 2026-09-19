"""
Auditoría de Graph View y Conformidad OKF v0.2 — Obsidian Graph Colors
Uso: python audit.py [--wiki <ruta_wiki>] [--okf-check]
Por defecto busca wiki/ relativo al directorio de trabajo.
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")


def find_wiki_root(start: Path) -> Path:
    for candidate in [start / "wiki", start]:
        if (candidate / ".obsidian" / "graph.json").exists() or (candidate / "index.md").exists():
            return candidate
    sys.exit(f"No se encontró graph.json ni index.md bajo {start}. Pasa --wiki <ruta>.")


def parse_frontmatter(md_path: Path) -> tuple[dict, str]:
    """Extrae frontmatter y cuerpo de un archivo markdown."""
    text = md_path.read_text(encoding="utf-8-sig", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm_text = m.group(1)
    body = m.group(2)

    parsed = {}
    # tags inline
    m_tags_inline = re.search(r"^tags:\s*\[([^\]]+)\]", fm_text, re.MULTILINE)
    if m_tags_inline:
        parsed["tags"] = [t.strip().strip("'\"") for t in m_tags_inline.group(1).split(",") if t.strip()]
    else:
        # tags block
        m_tags_block = re.search(r"^tags:\s*\n((?:\s*-\s+\S+\n?)+)", fm_text, re.MULTILINE)
        if m_tags_block:
            parsed["tags"] = [re.sub(r"^\s*-\s+", "", l).strip().strip("'\"") for l in m_tags_block.group(1).splitlines() if l.strip()]
        else:
            parsed["tags"] = []

    # type
    m_type = re.search(r"^type:\s*(.+)$", fm_text, re.MULTILINE)
    if m_type:
        parsed["type"] = m_type.group(1).strip().strip("'\"")

    # title
    m_title = re.search(r"^title:\s*(.+)$", fm_text, re.MULTILINE)
    if m_title:
        parsed["title"] = m_title.group(1).strip().strip("'\"")

    # description
    m_desc = re.search(r"^description:\s*(.+)$", fm_text, re.MULTILINE)
    if m_desc:
        parsed["description"] = m_desc.group(1).strip().strip("'\"")

    # legacy fields
    m_updated = re.search(r"^updated:\s*(.+)$", fm_text, re.MULTILINE)
    if m_updated:
        parsed["updated"] = m_updated.group(1).strip()

    m_raw = re.search(r"^raw:\s*(.+)$", fm_text, re.MULTILINE)
    if m_raw:
        parsed["raw"] = m_raw.group(1).strip()

    # generated
    m_gen = re.search(r"^generated:\s*(.+)$", fm_text, re.MULTILINE)
    if m_gen:
        parsed["generated"] = m_gen.group(1).strip()

    # sources IDs
    source_ids = re.findall(r"-\s*id:\s*([a-zA-Z0-9_-]+)", fm_text)
    parsed["source_ids"] = source_ids

    return parsed, body


def decimal_to_hex(d: int) -> str:
    R = d >> 16
    G = (d >> 8) & 0xFF
    B = d & 0xFF
    return f"#{R:02X}{G:02X}{B:02X}"


def collect_wiki_tags(wiki_root: Path) -> dict[str, list[str]]:
    """Returns {tag: [filename, ...]} for all .md files in wiki/ (excluding .obsidian)."""
    tag_map: dict[str, list[str]] = defaultdict(list)
    for md in wiki_root.rglob("*.md"):
        if ".obsidian" in md.parts:
            continue
        fm, _ = parse_frontmatter(md)
        for tag in fm.get("tags", []):
            tag_map[tag].append(md.name)
    return dict(tag_map)


def audit_okf_conformance(wiki_root: Path) -> list[str]:
    """Audita la conformidad de los archivos markdown contra OKF-SPEC-v0.2."""
    issues = []
    reserved_files = {"index.md", "log.md"}

    # 1. Verificar index.md
    index_file = wiki_root / "index.md"
    if not index_file.exists():
        issues.append("[OKF:INDEX] No se encontró wiki/index.md en la raíz del bundle.")
    else:
        content = index_file.read_text(encoding="utf-8-sig", errors="replace")
        if "okf_version:" not in content:
            issues.append("[OKF:VERSION] wiki/index.md no declara okf_version: \"0.2\" en frontmatter.")

    # 2. Verificar conceptos
    for md in wiki_root.rglob("*.md"):
        if ".obsidian" in md.parts:
            continue
        if md.name in reserved_files:
            continue

        rel_path = md.relative_to(wiki_root)
        fm, body = parse_frontmatter(md)

        # Requisito 1 & 2: Frontmatter y type obligatorio
        if not fm:
            issues.append(f"[OKF:NO_FRONTMATTER] {rel_path} no contiene bloque YAML frontmatter delimitado por ---.")
            continue
        if not fm.get("type"):
            issues.append(f"[OKF:NO_TYPE] {rel_path} no contiene el campo obligatorio 'type:'.")

        # Campos obsoletos v0.1
        if "updated" in fm:
            issues.append(f"[OKF:LEGACY_FIELD] {rel_path} usa 'updated:' en lugar de 'generated: {{ by, at }}'.")
        if "raw" in fm:
            issues.append(f"[OKF:LEGACY_FIELD] {rel_path} usa campo custom 'raw:' en lugar de 'sources[].resource'.")

        # Footnotes vs sources.id
        footnotes = re.findall(r"\[\^([a-zA-Z0-9_-]+)\]", body)
        source_ids = set(fm.get("source_ids", []))
        for fn in set(footnotes):
            if source_ids and fn not in source_ids:
                issues.append(f"[OKF:FOOTNOTE_UNMATCHED] {rel_path} tiene footnote '[^{fn}]' sin entrada id correspondiente en sources:.")

    return issues


def audit(wiki_root: Path, check_okf: bool = False) -> None:
    graph_json = wiki_root / ".obsidian" / "graph.json"
    has_graph = graph_json.exists()
    color_groups = []

    if has_graph:
        data = json.loads(graph_json.read_text(encoding="utf-8"))
        color_groups = data.get("colorGroups", [])

    wiki_tags = collect_wiki_tags(wiki_root)

    # ── tabla principal ──────────────────────────────────────────────────────
    if has_graph:
        col_q = max([len(g["query"]) for g in color_groups] + [30]) + 2 if color_groups else 30
        col_h = 10
        col_d = 12

        header = f"{'Query':<{col_q}} {'Hex':<{col_h}} {'RGB dec':<{col_d}} Artículos"
        print()
        print(f"Color groups actuales — {graph_json.relative_to(wiki_root.parent if wiki_root.parent.exists() else wiki_root)}")
        print("─" * len(header))
        print(header)
        print("─" * len(header))

        hex_usage: dict[str, list[str]] = defaultdict(list)
        groups_in_file: set[str] = set()

        for g in color_groups:
            query: str = g["query"]
            rgb: int = g["color"]["rgb"]
            hex_color = decimal_to_hex(rgb)
            clean_tag = query.strip().removeprefix("tag:#")
            articles = wiki_tags.get(clean_tag, [])
            art_str = ", ".join(articles) if articles else "—  ⚠ sin artículos"
            print(f"{query:<{col_q}} {hex_color:<{col_h}} {rgb:<{col_d}} {art_str}")
            hex_usage[hex_color].append(query)
            groups_in_file.add(clean_tag)

        print()

        # ── anomalías de grafo ────────────────────────────────────────────────────
        anomalies: list[str] = []

        # 1. Tags en wiki sin grupo de color
        missing = [f"#{t}" for t in wiki_tags if t not in groups_in_file]
        if missing:
            anomalies.append(f"[SIN COLOR]    Tags en wiki sin grupo: {', '.join(sorted(missing))}")

        # 2. Grupos huérfanos
        for g in color_groups:
            clean = g["query"].strip().removeprefix("tag:#")
            if clean not in wiki_tags:
                anomalies.append(f"[HUÉRFANO]     '{g['query']}' no coincide con ningún artículo")

        # 3. Espacios en las queries
        for g in color_groups:
            if g["query"] != g["query"].strip():
                anomalies.append(f"[ESPACIOS]     '{g['query']}' tiene espacios extra")

        # 4. Colores duplicados
        for hex_color, queries in hex_usage.items():
            if len(queries) > 1:
                anomalies.append(f"[DUPLICADO]    Hex {hex_color} usado en: {', '.join(queries)}")

        if anomalies:
            print("Anomalías de Grafo detectadas")
            print("─" * 40)
            for a in anomalies:
                print(" •", a)
        else:
            print("Sin anomalías de Grafo detectadas.")
        print()

    # ── Auditoría OKF ────────────────────────────────────────────────────────
    if check_okf:
        print("Auditoría de Conformidad OKF v0.2")
        print("─" * 40)
        okf_issues = audit_okf_conformance(wiki_root)
        if okf_issues:
            for issue in okf_issues:
                print(" •", issue)
        else:
            print("✓ Bundle 100% conforme con OKF v0.2.")
        print()


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--help" in args or "-h" in args:
        print(__doc__.strip())
        sys.exit(0)

    check_okf = "--okf-check" in args
    if "--okf-check" in args:
        args.remove("--okf-check")

    if "--wiki" in args:
        idx = args.index("--wiki") + 1
        if idx >= len(args):
            sys.exit("Error: --wiki requiere una ruta. Uso: python audit.py [--wiki <ruta_wiki>] [--okf-check]")
        wiki_root = Path(args[idx])
    else:
        wiki_root = find_wiki_root(Path.cwd())

    audit(wiki_root, check_okf=check_okf or True)



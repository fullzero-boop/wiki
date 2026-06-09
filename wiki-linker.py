#!/usr/bin/env python3
"""wiki-linker.py — Auto-link known entities in wiki pages using [[wikilinks]]."""
import re, os
from pathlib import Path

WIKI_DIR = Path("/data/lightrag/wiki")


def get_all_pages():
    pages = {}
    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file.name in ("index.md", "log.md", "readme.md", "README.md"):
            continue
        pages[md_file.stem] = md_file
    return pages


def build_entities():
    pages = get_all_pages()
    entities = {name: name for name in pages}
    return entities


def is_in_code_block(text, pos):
    fences = text[:pos].count("```")
    return fences % 2 == 1


def link_page(text, page_name):
    entities = build_entities()
    sorted_ents = sorted(entities.items(), key=lambda x: -len(x[0]))
    matches = []
    for display, target in sorted_ents:
        if target == page_name:
            continue
        pattern = re.compile(r'(?<!\[\[)' + re.escape(display) + r'(?!\]\])')
        for m in pattern.finditer(text):
            if not is_in_code_block(text, m.start()):
                matches.append((m.start(), m.end(), display, target))

    matches.sort(key=lambda x: x[0])
    filtered = []
    last_end = -1
    for start, end, display, target in matches:
        if start >= last_end:
            filtered.append((start, end, f"[[{target}]]"))
            last_end = end

    result = text
    for start, end, link in reversed(filtered):
        result = result[:start] + link + result[end:]
    return result


def main():
    changed = []
    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        if md_file.name in ("index.md", "log.md", "readme.md", "README.md"):
            continue
        page_name = md_file.stem
        original = md_file.read_text("utf-8")
        linked = link_page(original, page_name)
        if linked != original:
            md_file.write_text(linked, "utf-8")
            changed.append(str(md_file.relative_to(WIKI_DIR)))
            print(f"  Linked: {md_file.relative_to(WIKI_DIR)}")

    if changed:
        print(f"\nAuto-linked {len(changed)} pages")
    else:
        print("  No changes needed")


if __name__ == "__main__":
    main()

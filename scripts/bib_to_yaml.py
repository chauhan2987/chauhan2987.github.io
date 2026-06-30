#!/usr/bin/env python3
"""
Convert _data/publications.bib (standard BibTeX) into _data/publications.yml
(the structure the Jekyll templates actually loop over).

Why this script exists: GitHub Pages' built-in "safe mode" Jekyll build
doesn't allow the jekyll-scholar plugin (the standard way to render BibTeX
in Jekyll), and reimplementing citation-count/h-index math and the
author-truncation/bold-name logic as Liquid templates operating directly
on parsed BibTeX got unwieldy. This script is the bridge: you maintain a
normal .bib file, and a generated, gitignored .yml file is what Jekyll
actually reads.

Usage:
    python3 scripts/bib_to_yaml.py

Requires: bibtexparser (pip install bibtexparser --break-system-packages)
Run automatically by .github/workflows/jekyll.yml before every build, so
you do NOT need to run this yourself before pushing — only if you want to
preview locally with `bundle exec jekyll serve` first.

Where to get a .bib file in the first place:
- Google Scholar profile -> select papers -> "Export" -> BibTeX
- Zotero / Mendeley / EndNote -> Export Collection -> BibTeX
- PubMed -> Send to -> Citation manager -> downloads .nbib, convertible to
  BibTeX with most reference managers, or paste into a converter
- Or just write entries by hand; see the example block in publications.bib

Custom (non-standard, but harmless) fields this script understands:
- citations = {N}   -- current citation count, shown in Research Impact
                        metrics and next to each publication. Optional;
                        defaults to 0 if omitted. Not a real BibTeX field,
                        but unknown fields are ignored by every reference
                        manager, so it's safe to keep in a real .bib file.
- pmid = {12345}    -- PubMed ID, used to build a PubMed link
- pmcid = {PMCxxxx} -- PubMed Central ID, informational only
- type = {journal|conference} -- overrides the auto-detected type
  (derived from the BibTeX entry type otherwise: @article -> journal,
  @inproceedings/@proceedings -> conference)
"""
import sys
import yaml
from pathlib import Path

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import splitname
except ImportError:
    print("Missing dependency. Install it with:\n"
          "    pip install bibtexparser --break-system-packages\n",
          file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
BIB_PATH = ROOT / "_data" / "publications.bib"
YAML_PATH = ROOT / "_data" / "publications.yml"

TYPE_MAP = {
    "article": "journal",
    "inproceedings": "conference",
    "proceedings": "conference",
    "conference": "conference",
    "phdthesis": "thesis",
    "mastersthesis": "thesis",
    "thesis": "thesis",
    "book": "book",
    "inbook": "book",
    "incollection": "book",
    "techreport": "report",
    "patent": "patent",
    "unpublished": "preprint",
    "misc": "preprint",
    "online": "preprint",
}


def format_author(person):
    """bibtexparser's splitname() gives {first, von, last, jr} parts.
    Reformat as 'Last, Initials' to match the site's display style."""
    last = " ".join(person.get("last", [])).strip()
    first_parts = person.get("first", [])
    initials = "".join(p[0] for p in first_parts if p).upper()
    if person.get("von"):
        last = " ".join(person["von"]) + " " + last
    return f"{last}, {initials}" if initials else last


def parse_authors(raw_author_field):
    names = [n.strip() for n in raw_author_field.split(" and ") if n.strip()]
    authors = []
    for n in names:
        if "," in n:
            # Already "Last, Initials" or "Last, First [Middle]"
            last, first = [x.strip() for x in n.split(",", 1)]
            last = last.strip("{}")  # BibTeX brace-protection on compound surnames, e.g. {Hernandez Gonzalez}
            words = [w for w in first.replace(".", " ").split() if w]
            if len(words) == 1 and words[0].isupper() and 1 <= len(words[0]) <= 4:
                # Already abbreviated, e.g. "PK" or "JR" — don't reduce further
                initials = words[0]
            else:
                initials = "".join(w[0] for w in words).upper()
            authors.append(f"{last}, {initials}" if initials else last)
        else:
            parts = splitname(n)
            authors.append(format_author(parts))
    return authors


def to_int_or_none(value):
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def convert():
    if not BIB_PATH.exists():
        print(f"No {BIB_PATH} found — nothing to convert.", file=sys.stderr)
        sys.exit(1)

    parser = BibTexParser(common_strings=True)
    parser.ignore_nonstandard_types = False
    with open(BIB_PATH, encoding="utf-8") as f:
        bib_db = bibtexparser.load(f, parser=parser)

    entries_out = []
    seen_keys = set()
    warnings = []
    for entry in bib_db.entries:
        key = entry.get("ID", "")
        if not key:
            warnings.append("Entry with no citation key (the {key, ...} part) — skipped.")
            continue
        if key in seen_keys:
            warnings.append(f"Duplicate citation key '{key}' — only the first occurrence is kept. "
                             f"Rename one of them (the part right after the opening brace).")
            continue
        seen_keys.add(key)

        if not entry.get("title"):
            warnings.append(f"Entry '{key}' has no title — it will render with a blank title.")
        if not entry.get("author"):
            warnings.append(f"Entry '{key}' has no author field — it will render with no authors.")
        if not entry.get("year"):
            warnings.append(f"Entry '{key}' has no year — it may sort unpredictably among other entries.")

        bib_type = entry.get("ENTRYTYPE", "article").lower()
        pub_type = entry.get("type") or TYPE_MAP.get(bib_type, "journal")

        record = {
            "key": entry.get("ID", ""),
            "type": pub_type,
            "title": entry.get("title", "").strip("{}"),
            "authors": parse_authors(entry.get("author", "")),
            "year": to_int_or_none(entry.get("year")) or entry.get("year", ""),
        }
        if entry.get("journal"):
            record["journal"] = entry["journal"]
        if entry.get("booktitle"):
            record["venue"] = entry["booktitle"]
        if entry.get("doi"):
            record["doi"] = entry["doi"]
        if entry.get("pmid"):
            record["pmid"] = str(entry["pmid"])
        if entry.get("pmcid"):
            record["pmcid"] = entry["pmcid"]
        # Always include citations explicitly (even 0) — the Liquid sort
        # used for Research Impact metrics errors if some entries have
        # this field and others don't.
        record["citations"] = to_int_or_none(entry.get("citations")) or 0

        entries_out.append(record)

    YAML_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(YAML_PATH, "w", encoding="utf-8") as f:
        f.write(
            "# AUTO-GENERATED by scripts/bib_to_yaml.py — do not edit by hand.\n"
            "# Edit _data/publications.bib instead and re-run the script\n"
            "# (or just push; GitHub Actions runs it automatically).\n\n"
        )
        yaml.safe_dump(entries_out, f, sort_keys=False, allow_unicode=True, width=100)

    print(f"Converted {len(entries_out)} entries: {BIB_PATH.name} -> {YAML_PATH.name}")
    if warnings:
        print(f"\n{len(warnings)} warning(s) (build continues, but check these):")
        for w in warnings:
            print(f"  - {w}")


if __name__ == "__main__":
    convert()

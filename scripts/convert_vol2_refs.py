#!/usr/bin/env python3
"""Convert the Vol II references markdown into data/references/ast-t1-vol-2.json.

Source format (in the markdown):
  ## Chapter N: Title {#ch-NN}

  Optional chapter-intro prose (not a reference, skipped).

  [1] First reference text...
  [2] Second reference text...
  [3] Reference truncated mid-sentence at "...something"
  > **[INCOMPLETE — source truncated mid-sentence at "...something"; needs author completion before publishing.]**

Output (matches the Vol III pattern in data/references/ast-t1-vol-3.json):
  {
    "series_id": "AST-T1",
    "book_title": "...",
    "volume": 2,
    "volume_title": "...",
    "last_updated": "YYYY-MM-DD",
    "source_markdown": "Vol_II_References_for_Website_2026-05-27.md",
    "chapters": [
      {"number": 1, "anchor": "ch-01", "title": "...",
       "references": [{"num": 1, "text": "..."}, ...]},
      ...
    ]
  }

The anchors `ch-01..ch-84` are zero-padded to honor the printed-QR contract
(memory: vol3-references-qr-anchor-contract; same rule applies to Vol II).

Incomplete references keep their `[INCOMPLETE ...]` warning text inside the
reference body so the website renders the partial citation next to the
warning — easier for the author to spot and fix than silently dropping them.

Re-run after the source markdown is updated:
  python scripts/convert_vol2_refs.py
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO_ROOT / "Vol_II_References_for_Website_2026-05-27.md"
OUTPUT = REPO_ROOT / "data" / "references" / "ast-t1-vol-2.json"

# Header: `## Chapter 12: Some Title {#ch-12}`
CHAPTER_HEADING_RE = re.compile(
    r"^##\s+Chapter\s+(\d+)\s*:\s*(.+?)\s*\{#(ch-\d+)\}\s*$"
)
# Numbered reference start: `[3] Author, ...`
REF_START_RE = re.compile(r"^\[(\d+)\]\s+(.*)$")
# Horizontal-rule separators between chapters (---, ***, ___). Skip these
# inside ref continuations so they don't bleed into the trailing ref text.
HR_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")


def parse_markdown(text: str) -> list[dict]:
    chapters: list[dict] = []
    current_chapter: dict | None = None
    current_ref_num: int | None = None
    current_ref_lines: list[str] = []

    def flush_ref() -> None:
        nonlocal current_ref_num, current_ref_lines
        if current_chapter is None or current_ref_num is None:
            current_ref_num = None
            current_ref_lines = []
            return
        joined = " ".join(s for s in current_ref_lines if s)
        # Collapse any runs of internal whitespace into single spaces.
        joined = re.sub(r"\s+", " ", joined).strip()
        current_chapter["references"].append({
            "num": current_ref_num,
            "text": joined,
        })
        current_ref_num = None
        current_ref_lines = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        m_ch = CHAPTER_HEADING_RE.match(line)
        if m_ch:
            flush_ref()
            num_str, title, anchor = m_ch.groups()
            current_chapter = {
                "number": int(num_str),
                "anchor": anchor,
                "title": title.strip(),
                "references": [],
            }
            chapters.append(current_chapter)
            continue

        if current_chapter is None:
            # File header prose before the first chapter — skip.
            continue

        m_ref = REF_START_RE.match(line)
        if m_ref:
            flush_ref()
            current_ref_num = int(m_ref.group(1))
            current_ref_lines = [m_ref.group(2).strip()]
            continue

        # Continuation of the current reference (blockquote, wrapped text, etc.)
        if current_ref_num is not None:
            stripped = line.strip()
            if not stripped:
                continue
            if HR_RE.match(stripped):
                # Chapter separator — end the current reference here.
                flush_ref()
                continue
            # Strip leading blockquote marker so the INCOMPLETE warning
            # renders as bold text, not as a stray ">" in the citation.
            if stripped.startswith("> "):
                stripped = stripped[2:].strip()
            elif stripped.startswith(">"):
                stripped = stripped[1:].strip()
            current_ref_lines.append(stripped)
            continue

        # Non-reference prose inside a chapter (the intro paragraph). Skip.

    flush_ref()
    return chapters


def build_doc(chapters: list[dict], source_path: Path) -> dict:
    return {
        "series_id": "AST-T1",
        "book_title": "Engineering Orbital Rings, Mass Drivers and Space Elevators",
        "volume": 2,
        "volume_title": "Mass Transit Launch Technologies from First Principles",
        "last_updated": date.today().isoformat(),
        "source_markdown": source_path.name,
        "chapters": chapters,
    }


def report(chapters: list[dict]) -> None:
    print(f"chapters parsed: {len(chapters)}")
    total = sum(len(c["references"]) for c in chapters)
    print(f"total references: {total}")
    if chapters:
        first, last = chapters[0], chapters[-1]
        print(f"  first: ch{first['number']:02d} ({first['anchor']}) "
              f"— {len(first['references'])} refs — {first['title'][:60]}")
        print(f"  last:  ch{last['number']:02d} ({last['anchor']}) "
              f"— {len(last['references'])} refs — {last['title'][:60]}")
    # Sanity: anchors should be ch-01..ch-NN, zero-padded, contiguous.
    missing = []
    for i, c in enumerate(chapters, 1):
        expected = f"ch-{i:02d}"
        if c["anchor"] != expected:
            missing.append((i, c["anchor"], expected))
    if missing:
        print(f"  WARNING: anchor mismatches: {missing[:5]}")
    incomplete = [
        (c["number"], r["num"])
        for c in chapters for r in c["references"]
        if "INCOMPLETE" in r["text"]
    ]
    print(f"  incomplete entries flagged: {len(incomplete)} -> {incomplete}")


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE
    if not src.exists():
        print(f"ERROR: source markdown not found at {src}", file=sys.stderr)
        return 1
    text = src.read_text(encoding="utf-8")
    chapters = parse_markdown(text)
    doc = build_doc(chapters, src)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT}")
    report(chapters)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

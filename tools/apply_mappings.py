"""Regenerate Vol I references JSON from finalized chapter manuscripts.

Reads the .pre-cowork-sync.bak (main's May 9 state, the source of truth for
reference TEXT) and renumbers the 8 reordered chapters so their numbering
matches each chapter's body citation order.

The mapping for each chapter is derived by running renumber_refs.find_cite_order
on the *older* manuscript version (the one whose body still uses the bak's
old numbering). The finalized versions (v19/v17/v11/etc.) listed in the task
prompt have monotonic [1..N] body citations, which would produce an identity
mapping (no-op). The older versions are the ones that encode the
old->new transformation we actually need.

Safety: raises ValueError listing every bak ref num that is NOT covered by the
mapping for its chapter. Nothing is written if any chapter fails. We do not
silently drop refs.
"""
import datetime
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

spec = importlib.util.spec_from_file_location("rr", HERE / "renumber_refs.py")
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)

# (chapter_number_as_str, manuscript_file_in_book_folder_with_OLD_numbering_in_body)
CHAPTER_SOURCES = [
    ("1",  "Vol_I_Ch01_v18_claude.md"),
    ("2",  "Vol_I_Ch02_v15_claude.md"),
    ("3",  "Vol_I_Ch03_v10_claude.md"),
    ("4",  "Vol_I_Ch04_v12_claude.md"),
    ("16", "Vol_I_Ch16_v17_claude.md"),
    ("17", "Vol_I_Ch17_v17_claude.md"),
    ("19", "Vol_I_Ch19_v17_claude.md"),
    ("20", "Vol_I_Ch20_v08_claude.md"),
]

BAK_DATA   = ROOT / "data"   / "references" / "ast-t1-vol-1.json.pre-cowork-sync.bak"
BAK_PUBLIC = ROOT / "public" / "data" / "references" / "ast-t1-vol-1.json.pre-cowork-sync.bak"
OUT_DATA   = ROOT / "data"   / "references" / "ast-t1-vol-1.json"
OUT_PUBLIC = ROOT / "public" / "data" / "references" / "ast-t1-vol-1.json"


def derive_mapping(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()
    body, _ = rr.split_body_refs(text)
    cite_order = rr.find_cite_order(body)
    return {old: new for new, old in enumerate(cite_order, start=1)}


def renumber_chapter(ch, mapping, ch_num):
    refs = ch["references"]
    bak_nums = sorted(r["num"] for r in refs)
    missing_from_mapping = [n for n in bak_nums if n not in mapping]
    if missing_from_mapping:
        return None, missing_from_mapping
    new_refs = sorted(
        ({"num": mapping[r["num"]], "text": r["text"]} for r in refs),
        key=lambda x: x["num"],
    )
    ch["references"] = new_refs
    return new_refs, []


def main():
    mappings = {}
    for ch_num, md_name in CHAPTER_SOURCES:
        md_path = ROOT / "book" / md_name
        mappings[ch_num] = derive_mapping(md_path)
        print(f"Ch {ch_num:>2} mapping from {md_name}: {len(mappings[ch_num])} entries")

    print()
    print("Loading bak file ...")
    with open(BAK_DATA, "r", encoding="utf-8") as f:
        data = json.load(f)

    failures = {}
    for ch in data["chapters"]:
        ch_num = ch.get("number")
        if ch_num not in mappings:
            continue
        _, missing = renumber_chapter(ch, mappings[ch_num], ch_num)
        if missing:
            failures[ch_num] = missing

    if failures:
        print()
        print("=" * 70)
        print("SAFETY CHECK FAILED. Nothing was written.")
        print("=" * 70)
        for ch_num, missing in sorted(failures.items(), key=lambda x: int(x[0])):
            print(f"  Ch {ch_num}: {len(missing)} bak ref nums not in mapping: {missing}")
        print()
        print("Each missing num corresponds to a reference that exists in the bak")
        print("JSON but is NOT cited in that chapter's older manuscript version. We")
        print("cannot deduce its new position automatically without semantic")
        print("matching against the finalized manuscript body.")
        raise SystemExit(1)

    data["last_updated"] = datetime.date.today().isoformat()
    for path in (OUT_DATA, OUT_PUBLIC):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Wrote {path}")

    print()
    print("Per-chapter rewrite summary:")
    for ch in data["chapters"]:
        ch_num = ch.get("number")
        if ch_num in mappings:
            nums = sorted(r["num"] for r in ch["references"])
            gaps = nums != list(range(1, len(nums) + 1))
            print(f"  Ch {ch_num:>2}: {len(nums)} refs, range {min(nums)}..{max(nums)}, gaps={gaps}")


if __name__ == "__main__":
    main()

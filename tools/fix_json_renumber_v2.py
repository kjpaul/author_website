#!/usr/bin/env python3
"""
v2: Re-apply Vol I citation renumbering to main's JSON, KEEPING every
reference (no drops). The book manuscript now adds inline [N] citations
for the 32 refs that used to be uncited (21 foundational scientists in
Ch 2; smaller groups in Chs 3, 4, 16, 17, 19, 20).

This script:
  - Reads data/references/ast-t1-vol-1.json.pre-cowork-sync.bak as input
    (main's pre-overwrite state - the canonical source of truth).
  - Applies the new old->new mapping for 8 chapters that were out of
    order in the manuscript: 1, 2, 3, 4, 16, 17, 19, 20.
  - Keeps every reference in every chapter (no orphans dropped).
  - Bumps last_updated to today.
  - Writes both data/ and public/ copies.

Run from D:\\_pauldejong.com\\ :
    python fix_json_renumber_v2.py
"""
import json
import datetime
import os

# old_num -> new_num maps. These keep every reference; every old num
# in each chapter's references list appears in the mapping.
MAPPINGS = {
    "1": {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 31: 7, 7: 8, 8: 9, 9: 10,
          10: 11, 11: 12, 12: 13, 13: 14, 14: 15, 15: 16, 16: 17, 17: 18,
          18: 19, 32: 20, 33: 21, 34: 22, 35: 23, 19: 24, 20: 25, 21: 26,
          22: 27, 23: 28, 24: 29, 27: 30, 25: 31, 26: 32, 28: 33, 29: 34,
          30: 35},

    "2": {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7,
          27: 8, 8: 9, 9: 10, 10: 11, 11: 12, 28: 13, 25: 14, 29: 15,
          26: 16, 12: 17, 13: 18, 14: 19, 15: 20, 16: 21, 17: 22,
          18: 23, 20: 24, 21: 25, 19: 26, 30: 27, 31: 28, 32: 29,
          33: 30, 34: 31, 22: 32, 23: 33, 24: 34, 35: 35, 36: 36,
          37: 37, 38: 38},

    "3": {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 18: 8, 8: 9, 9: 10,
          22: 11, 19: 12, 20: 13, 21: 14, 23: 15, 24: 16, 25: 17, 17: 18,
          10: 19, 11: 20, 12: 21, 13: 22, 14: 23, 15: 24, 16: 25},

    "4": {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10,
          11: 11, 16: 12, 17: 13, 12: 14, 15: 15, 13: 16, 14: 17},

    "16": {11: 1, 10: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 8, 7: 9, 8: 10,
           9: 11},

    "17": {6: 1, 4: 2, 1: 3, 12: 4, 2: 5, 3: 6, 8: 7, 10: 8, 14: 9, 7: 10,
           11: 11, 5: 12, 9: 13, 13: 14, 15: 15, 16: 16, 17: 17, 18: 18},

    "19": {1: 1, 11: 2, 8: 3, 3: 4, 2: 5, 4: 6, 5: 7, 6: 8, 10: 9, 7: 10,
           9: 11},

    "20": {1: 1, 2: 2, 3: 3, 6: 4, 7: 5, 4: 6, 5: 7, 8: 8},
}

# Expected reference count per chapter after renumbering (sanity check).
EXPECTED_COUNT = {ch: len(m) for ch, m in MAPPINGS.items()}

# Paths relative to D:\_pauldejong.com
BAK_DATA   = "data/references/ast-t1-vol-1.json.pre-cowork-sync.bak"
BAK_PUBLIC = "public/data/references/ast-t1-vol-1.json.pre-cowork-sync.bak"
OUT_DATA   = "data/references/ast-t1-vol-1.json"
OUT_PUBLIC = "public/data/references/ast-t1-vol-1.json"


def renumber_chapter(ch_entry, mapping):
    """Apply mapping (old->new) to a chapter's references list.
    Every JSON ref num MUST be in the mapping; if any old num is
    missing from the mapping, raise so we catch a stale .bak."""
    refs = ch_entry.get("references", [])
    missing = [r["num"] for r in refs if r["num"] not in mapping]
    if missing:
        raise ValueError(
            f"Chapter {ch_entry.get('number')}: refs {missing} are in "
            f"the JSON but not in the mapping. The mapping is stale "
            f"or main's JSON has refs we didn't expect."
        )
    new_refs = []
    for r in refs:
        new_refs.append({"num": mapping[r["num"]], "text": r["text"]})
    new_refs.sort(key=lambda x: x["num"])
    ch_entry["references"] = new_refs
    return len(new_refs)


def process(bak_path, out_path, label):
    if not os.path.exists(bak_path):
        print(f"  [{label}] ERROR: backup not found at {bak_path}")
        return False
    with open(bak_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"  [{label}] reading {bak_path}")
    for ch in data["chapters"]:
        ch_num = str(ch.get("number"))
        if ch_num in MAPPINGS:
            n = renumber_chapter(ch, MAPPINGS[ch_num])
            expected = EXPECTED_COUNT[ch_num]
            status = "OK" if n == expected else f"COUNT MISMATCH ({n} vs {expected})"
            print(f"     Ch {ch_num}: {n} refs renumbered  [{status}]")

    data["last_updated"] = datetime.date.today().isoformat()

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  [{label}] wrote {out_path}")
    return True


def main():
    print("Processing data/ copy ...")
    ok1 = process(BAK_DATA, OUT_DATA, "data")
    print()
    print("Processing public/ copy ...")
    ok2 = process(BAK_PUBLIC, OUT_PUBLIC, "public")

    print()
    if ok1 and ok2:
        print("All renumbering applied. Every reference is preserved.")
        print()
        print("Next steps:")
        print("  1. Spot-check:")
        print("     findstr /C:\"MISSING\" data\\references\\ast-t1-vol-1.json")
        print("       (should return no matches)")
        print("     findstr /C:\"Vera Rubin and What We Cannot\" data\\references\\ast-t1-vol-1.json")
        print("       (should return no matches - Ch 3 title is 'Survey Telescopes...')")
        print()
        print("  2. Optional WinMerge against the previous .bak:")
        print(f"     winmergeu {BAK_DATA} {OUT_DATA}")
        print()
        print("  3. Build and deploy:")
        print("     python build.py")
        print("     firebase deploy")
        print()
        print("  4. Commit:")
        print("     git add data\\references\\ast-t1-vol-1.json")
        print("     git add public\\data\\references\\ast-t1-vol-1.json")
        print("     git commit -m \"Vol I refs: renumber Chs 1-4, 16, 17, 19, 20 in citation order (no refs dropped)\"")
        print("     git push")
    else:
        print("ERRORS occurred - DO NOT deploy.")


if __name__ == "__main__":
    main()

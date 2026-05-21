#!/usr/bin/env python3
"""Run the renumber tool on all eight out-of-order chapters and write
new versioned MDs, an updated JSON, and an orphans MD."""
import os
import json
import shutil
import sys
import importlib.util

# Load renumber_refs module
spec = importlib.util.spec_from_file_location("rr", "renumber_refs.py")
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)

VOL_I = "/sessions/vibrant-cool-noether/mnt/Vol_I"
JSON_SRC = f"{VOL_I}/website/_pauldejong.com/data/references/ast-t1-vol-1.json"
JSON_OUT_DATA = f"{VOL_I}/website/_pauldejong.com/data/references/ast-t1-vol-1.json"
JSON_OUT_PUBLIC = f"{VOL_I}/website/_pauldejong.com/public/data/references/ast-t1-vol-1.json"
ORPHANS_MD = f"{VOL_I}/Vol_I_Orphan_References.md"

# (chapter_number, old_filename, new_filename)
TARGETS = [
    (1,  "Vol_I_Ch01_v18_claude.md", "Vol_I_Ch01_v19_claude.md"),
    (2,  "Vol_I_Ch02_v15_claude.md", "Vol_I_Ch02_v16_claude.md"),
    (3,  "Vol_I_Ch03_v10_claude.md", "Vol_I_Ch03_v11_claude.md"),
    (4,  "Vol_I_Ch04_v12_claude.md", "Vol_I_Ch04_v13_claude.md"),
    (16, "Vol_I_Ch16_v17_claude.md", "Vol_I_Ch16_v18_claude.md"),
    (17, "Vol_I_Ch17_v17_claude.md", "Vol_I_Ch17_v18_claude.md"),
    (19, "Vol_I_Ch19_v17_claude.md", "Vol_I_Ch19_v18_claude.md"),
    (20, "Vol_I_Ch20_v08_claude.md", "Vol_I_Ch20_v09_claude.md"),
]

# Load JSON once; we mutate it as we go.
with open(JSON_SRC, 'r', encoding='utf-8') as f:
    big_json = json.load(f)

# We need to mutate the loaded JSON in place per chapter, then write at the
# end. The renumber_refs library writes per-call, but we'll override by
# patching `data` in memory and supplying a temp path.

orphans_by_chapter = {}
mapping_summary = {}

for ch_num, src_name, dst_name in TARGETS:
    src = os.path.join(VOL_I, src_name)
    dst = os.path.join(VOL_I, dst_name)
    print(f"\n=== Chapter {ch_num} ===")
    # We can't pass big_json directly; use a tmp file then rebuild.
    tmp_json = f"/tmp/_json_ch{ch_num}.json"
    with open(tmp_json, 'w', encoding='utf-8') as f:
        json.dump(big_json, f, indent=2, ensure_ascii=False)
    out_json = f"/tmp/_json_ch{ch_num}_out.json"
    info = rr.renumber_chapter(src, dst, str(ch_num), tmp_json, out_json)
    # Merge updated chapter back into big_json
    with open(out_json, 'r', encoding='utf-8') as f:
        updated = json.load(f)
    for i, ch in enumerate(big_json['chapters']):
        if str(ch.get('number')) == str(ch_num):
            big_json['chapters'][i] = next(
                c for c in updated['chapters']
                if str(c.get('number')) == str(ch_num))
            break
    orphans_by_chapter[ch_num] = info['json_info']['orphans']
    mapping_summary[ch_num] = info['mapping']

# Update last_updated metadata
import datetime
big_json['last_updated'] = datetime.date.today().isoformat()

# Write final JSON (both copies)
for path in [JSON_OUT_DATA, JSON_OUT_PUBLIC]:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(big_json, f, indent=2, ensure_ascii=False)
    print(f"Wrote {path}")

# Build orphans MD
lines = []
lines.append("# Volume I — Orphan References")
lines.append("")
lines.append(f"Generated {datetime.date.today().isoformat()} during the v10 → v11 reference renumbering pass.")
lines.append("")
lines.append("These references exist in the JSON file but were not cited anywhere in the latest chapter manuscript. They are NOT included in the book or on the website. Keep this file in case any are needed later.")
lines.append("")
lines.append("Each section lists the orphans for that chapter using the ORIGINAL (pre-renumbering) reference number.")
lines.append("")
lines.append("---")
total_orphans = 0
for ch_num in sorted(orphans_by_chapter.keys()):
    orphans = orphans_by_chapter[ch_num]
    if not orphans:
        continue
    lines.append("")
    lines.append(f"## Chapter {ch_num}")
    lines.append("")
    for orph in orphans:
        lines.append(f"- **[orig {orph['original_num']}]** {orph['text']}")
        total_orphans += 1

with open(ORPHANS_MD, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines) + "\n")
print(f"\nWrote {ORPHANS_MD} ({total_orphans} orphans total)")

print("\n=== Summary ===")
for ch in sorted(mapping_summary.keys()):
    m = mapping_summary[ch]
    n_orph = len(orphans_by_chapter[ch])
    print(f"  Ch{ch:>2}: {len(m)} citations renumbered, {n_orph} orphans")

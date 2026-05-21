#!/usr/bin/env python3
"""Renumber citations in a chapter file so they appear in monotonically
increasing order, and produce an updated JSON entry for that chapter.

Usage: renumber_refs.py <chapter_md_in> <chapter_md_out> <old_ch_number>
              [--json-in PATH] [--json-out PATH]

The script:
  1. Reads the chapter Markdown.
  2. Scans the body for [N] and [N, M, ...] citations in document order.
  3. Builds an old-to-new mapping where each new number is assigned in
     order of first citation. Numbers cited multiple times reuse their
     first-assignment.
  4. Rewrites every [N] or [N, M] in the body using the new mapping.
  5. Reads the JSON for that chapter (if given) and produces:
       - a new ordered list of references for that chapter (the kept
         references, in new-order)
       - a list of orphans (references in JSON that are not cited)
  6. Returns both as Python dicts so the caller can save them.

The chapter body is everything BEFORE the "## References" section. The
references section is preserved unchanged (it just points at the
website QR code).
"""
import re
import sys
import json
import argparse


def find_cite_order(body):
    """Return list of old citation numbers in order of first appearance.

    Matches single [N] and grouped [N, M, L] citations. Skips bracketed
    things that are clearly not citations (e.g. [REF NEEDED], [N]).
    """
    cite_pat = re.compile(r'\[(\d+(?:\s*,\s*\d+)*)\]')
    seen = []
    for m in cite_pat.finditer(body):
        for token in re.split(r'\s*,\s*', m.group(1)):
            n = int(token)
            if n not in seen:
                seen.append(n)
    return seen


def renumber_body(body, mapping):
    """Rewrite [N] and [N, M] citations using mapping[old]=new."""
    cite_pat = re.compile(r'\[(\d+(?:\s*,\s*\d+)*)\]')

    def repl(m):
        nums = [int(x) for x in re.split(r'\s*,\s*', m.group(1))]
        new_nums = []
        for n in nums:
            if n in mapping:
                new_nums.append(mapping[n])
            else:
                # Unmapped (citation has no JSON entry); leave it as-is
                # but mark it for follow-up.
                new_nums.append(n)
        return "[" + ", ".join(str(n) for n in new_nums) + "]"

    return cite_pat.sub(repl, body)


def split_body_refs(text):
    """Split chapter text into (body, references_section)."""
    m = re.search(r'\n(##\s+References\s*\n.*)$', text, flags=re.DOTALL)
    if m:
        return text[:m.start()], m.group(1)
    return text, ""


def renumber_chapter(md_path, md_out_path, ch_num,
                     json_in_path=None, json_out_path=None):
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    body, refs_section = split_body_refs(text)
    cite_order = find_cite_order(body)
    # Build mapping: old -> new (1-based, sequential)
    mapping = {old: new for new, old in enumerate(cite_order, start=1)}
    print(f"  Citations: {len(cite_order)}")
    print(f"  Mapping (old -> new): " +
          ", ".join(f"{o}->{n}" for o, n in mapping.items()))

    new_body = renumber_body(body, mapping)
    # Ensure a blank line between body end and "## References" so
    # pandoc does not interpret "---" as YAML frontmatter.
    sep = "" if new_body.endswith("\n\n") else ("\n" if new_body.endswith("\n") else "\n\n")
    new_text = new_body + sep + refs_section

    with open(md_out_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print(f"  Wrote {md_out_path}")

    json_info = None
    if json_in_path:
        with open(json_in_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Find the chapter entry
        ch_entry = None
        for ch in data['chapters']:
            if str(ch.get('number')) == str(ch_num):
                ch_entry = ch
                break
        if ch_entry is None:
            print(f"  WARNING: no JSON entry for chapter {ch_num}")
            return None

        json_refs = {r['num']: r for r in ch_entry.get('references', [])}
        new_refs = []
        orphans = []

        for old_num in cite_order:
            ref = json_refs.get(old_num)
            new_num = mapping[old_num]
            if ref is None:
                # Cited but not in JSON - keep a placeholder
                new_refs.append({
                    "num": new_num,
                    "text": f"[MISSING: original reference [{old_num}] was cited but had no JSON entry]"
                })
            else:
                new_refs.append({"num": new_num, "text": ref['text']})

        # Identify orphans: JSON refs not cited
        for old_num, ref in sorted(json_refs.items()):
            if old_num not in mapping:
                orphans.append({"original_num": old_num, "text": ref['text']})

        ch_entry['references'] = new_refs
        json_info = {
            "ch_num": ch_num,
            "title": ch_entry.get('title'),
            "kept_count": len(new_refs),
            "orphan_count": len(orphans),
            "orphans": orphans,
            "data": data,
        }
        if json_out_path:
            with open(json_out_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  Wrote {json_out_path}")
        print(f"  Refs kept: {len(new_refs)}, orphans: {len(orphans)}")

    return {"mapping": mapping, "json_info": json_info}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('md_in')
    ap.add_argument('md_out')
    ap.add_argument('ch_num')
    ap.add_argument('--json-in')
    ap.add_argument('--json-out')
    args = ap.parse_args()
    renumber_chapter(args.md_in, args.md_out, args.ch_num,
                     args.json_in, args.json_out)

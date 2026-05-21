"""Build a proposed body-position -> bak-ref mapping for each chapter where the
safety check in apply_mappings.py failed.

For each citation [N] in the FINALIZED manuscript body, we extract the context
(prose before/after the citation), tokenize it, and rank the bak refs for that
chapter by keyword overlap with the bak ref text. The top candidates are
emitted to tools/proposed_mappings/Ch{N}_proposal.md for human review.

This does NOT modify the JSON. It just produces review files.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT_DIR = HERE / "proposed_mappings"
OUT_DIR.mkdir(exist_ok=True)

# Chapters that failed the safety check (every chapter except Ch 1)
FINALIZED = [
    ("2",  "Vol_I_Ch02_v17_claude.md"),
    ("3",  "Vol_I_Ch03_v11_claude.md"),
    ("4",  "Vol_I_Ch04_v13_claude.md"),
    ("16", "Vol_I_Ch16_v18_claude.md"),
    ("17", "Vol_I_Ch17_v18_claude.md"),
    ("19", "Vol_I_Ch19_v18_claude.md"),
    ("20", "Vol_I_Ch20_v09_claude.md"),
]

STOPWORDS = set("""
a about above after again against all am an and any are aren as at be because been before being below
between both but by can could did do does doing don down during each few for from further had has have
having he her here hers herself him himself his how i i'd i'll i'm i've if in into is isn it it's its itself
just let's me more most mustn my myself no nor not of off on once only or other ought our ours ourselves
out over own same shan she should shouldn so some such than that the their theirs them themselves then
there these they this those through to too under until up very was wasn we were weren what when where
which while who whom why will with won would wouldn you your yours yourself yourselves use using used
also etc see also use first new one two three figure table chapter volume vol per via due using based
""".split())


def tokenize(text):
    # split on non-alphanumeric, keep alpha tokens length >=3
    toks = re.findall(r"[A-Za-z][A-Za-z0-9'\-_]{2,}", text.lower())
    return [t for t in toks if t not in STOPWORDS]


def score(context_tokens, ref_text):
    ref_tokens = set(tokenize(ref_text))
    if not ref_tokens:
        return 0.0
    overlap = sum(1 for t in context_tokens if t in ref_tokens)
    return overlap / (len(context_tokens) + 1)


def first_cite_positions(body):
    """Return list of (n, char_pos, context) for each [N] in first-appearance order."""
    pat = re.compile(r'\[(\d+(?:\s*,\s*\d+)*)\]')
    seen = set()
    out = []
    for m in pat.finditer(body):
        for tok in re.split(r'\s*,\s*', m.group(1)):
            n = int(tok)
            if n in seen:
                continue
            seen.add(n)
            s = max(0, m.start() - 200)
            e = min(len(body), m.end() + 60)
            ctx = body[s:e].replace("\n", " ").strip()
            out.append((n, m.start(), ctx))
    out.sort(key=lambda x: x[1])
    return out


def split_body_refs(text):
    m = re.search(r'\n(##\s+References\s*\n.*)$', text, flags=re.DOTALL)
    if m:
        return text[:m.start()]
    return text


def main():
    with open(ROOT / "data" / "references" / "ast-t1-vol-1.json.pre-cowork-sync.bak",
              encoding="utf-8") as f:
        bak = json.load(f)
    bak_chs = {c["number"]: c for c in bak["chapters"]}

    for ch_num, md_name in FINALIZED:
        with open(ROOT / "book" / md_name, encoding="utf-8") as f:
            body = split_body_refs(f.read())
        ch = bak_chs[ch_num]
        bak_refs = {r["num"]: r["text"] for r in ch["references"]}

        cites = first_cite_positions(body)
        lines = []
        lines.append(f"# Ch {ch_num} mapping proposal")
        lines.append("")
        lines.append(f"Manuscript: {md_name}")
        lines.append(f"Cites in body: {len(cites)} | Bak refs available: {len(bak_refs)}")
        lines.append("")
        lines.append("For each finalized body position [N], top-3 bak ref candidates by keyword overlap. "
                     "First column **propose** is the top match; review and correct if wrong.")
        lines.append("")

        used_proposal = set()
        for n, _, ctx in cites:
            ctx_tokens = tokenize(ctx)
            scored = sorted(
                ((bak_num, score(ctx_tokens, txt), txt) for bak_num, txt in bak_refs.items()),
                key=lambda x: -x[1],
            )
            propose = scored[0][0] if scored else "?"
            used_proposal.add(propose)
            lines.append(f"## body [{n}]  →  propose bak [{propose}]")
            lines.append("")
            lines.append(f"**Context**: ...{ctx}...")
            lines.append("")
            lines.append("Top candidates:")
            for bak_num, sc, txt in scored[:4]:
                lines.append(f"- **bak [{bak_num}]** (score {sc:.2f}): {txt[:240]}")
            lines.append("")

        # Note any bak refs that DIDN'T appear as anyone's top-1
        unused = sorted(set(bak_refs) - used_proposal)
        if unused:
            lines.append("---")
            lines.append("")
            lines.append(f"### Bak refs NOT picked as anyone's top-1 ({len(unused)}):")
            for bn in unused:
                lines.append(f"- bak [{bn}]: {bak_refs[bn][:200]}")

        out_path = OUT_DIR / f"Ch{int(ch_num):02d}_proposal.md"
        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

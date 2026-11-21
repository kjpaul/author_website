"""Build the 1200 x 630 share image for /arc/ (Facebook, X, LinkedIn previews).

Run from the site root:

    python tools/make_arc_share_image.py            writes arc-share-v1.png
    python tools/make_arc_share_image.py --version 2

The cover is read from static/images/covers/orbital-ring-vol-1-cover.png, so
when the final cover replaces the provisional one under the same name, run
this again with the next version number and set ARC_SHARE_IMAGE in build.py
to the new file. Facebook caches a preview by the image's URL, so a
regenerated image needs a new file name.

Colors are the site's own, from :root in static/css/style.css. The fonts are
the site's Fraunces (headings) and Inter (text), kept in tools/fonts/ under
the SIL Open Font License; without those files the script falls back to
Georgia and Segoe UI or Arial.
"""
import argparse
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COVER = os.path.join(ROOT, "static", "images", "covers", "orbital-ring-vol-1-cover.png")
CSS = os.path.join(ROOT, "static", "css", "style.css")
FONTS = os.path.join(ROOT, "tools", "fonts")
OUT_DIR = os.path.join(ROOT, "static", "images", "social")

W, H = 1200, 630
EDGE = 60            # no text nearer than this to any edge
COVER_MARGIN = 40    # above and below the cover
GAP = 56             # between the cover and the text

LABEL = "ADVANCE READER COPIES"
HEADLINE = "Read Volume I before it is out."
LINE = ["Orbital Ring Engineering", "Paul G. de Jong"]
FOOTER = ["Free", "pauldejong.com/arc", "On sale 19 January 2027"]
SEP = " \u00b7 "

HEADLINE_PX = 64     # at least 56
SMALL_PX = 30        # the smallest text, at least 30


def css_color(name):
    """A color variable from :root in the site's stylesheet."""
    with open(CSS, encoding="utf-8") as f:
        m = re.search(r"--%s:\s*(#[0-9a-fA-F]{6})" % re.escape(name), f.read())
    if not m:
        sys.exit("color --%s not found in %s" % (name, CSS))
    h = m.group(1)
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def contrast(a, b):
    def lum(c):
        v = [x / 255 for x in c]
        v = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in v]
        return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def font(kind, px, weight):
    """kind is 'serif' or 'sans'. The site's variable fonts when present."""
    name = {"serif": "Fraunces.ttf", "sans": "Inter.ttf"}[kind]
    path = os.path.join(FONTS, name)
    if os.path.exists(path):
        f = ImageFont.truetype(path, px)
        if kind == "serif":      # axes: optical size, weight, softness, wonky
            f.set_variation_by_axes([min(px, 144), weight, 0, 0])
        else:                    # axes: optical size, weight
            f.set_variation_by_axes([min(max(px, 14), 32), weight])
        return f, name
    win = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    for fb in ({"serif": ["georgia.ttf"], "sans": ["segoeui.ttf", "arial.ttf"]}[kind]):
        p = os.path.join(win, fb)
        if os.path.exists(p):
            return ImageFont.truetype(p, px), fb
    sys.exit("no font found for " + kind)


def wrap_words(draw, text, f, width):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if cur and draw.textlength(trial, font=f) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    lines.append(cur)
    return lines


def wrap_parts(draw, parts, f, width):
    """Join parts with the middle dot; break only between parts."""
    lines, cur = [], ""
    for p in parts:
        trial = cur + SEP + p if cur else p
        if cur and draw.textlength(trial, font=f) > width:
            lines.append(cur)
            cur = p
        else:
            cur = trial
    lines.append(cur)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", type=int, default=1)
    args = ap.parse_args()

    bg = css_color("bg")
    ink = css_color("ink")
    accent = css_color("accent")
    muted = css_color("muted")
    rule = css_color("rule")
    for name, c in (("ink", ink), ("accent", accent), ("muted", muted)):
        r = contrast(c, bg)
        print("contrast %-6s on bg: %.2f : 1" % (name, r))
        if r < 4.5:
            sys.exit("contrast of %s is below 4.5 : 1" % name)

    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    # The cover, scaled without distortion to the height between the margins.
    cover = Image.open(COVER).convert("RGB")
    ch = H - 2 * COVER_MARGIN
    cw = round(cover.width * ch / cover.height)
    cover = cover.resize((cw, ch), Image.LANCZOS)
    cx, cy = EDGE, COVER_MARGIN
    d.rectangle([cx + 6, cy + 8, cx + cw + 6, cy + ch + 8], fill=rule)   # a flat shadow
    img.paste(cover, (cx, cy))
    d.rectangle([cx, cy, cx + cw - 1, cy + ch - 1], outline=rule)

    x0 = cx + cw + GAP
    x1 = W - EDGE
    width = x1 - x0

    f_label, n1 = font("sans", SMALL_PX, 600)
    f_head, n2 = font("serif", HEADLINE_PX, 500)
    f_line, _ = font("sans", 32, 500)
    f_foot, _ = font("sans", SMALL_PX, 400)
    print("fonts: %s, %s" % (n2, n1))

    head = wrap_words(d, HEADLINE, f_head, width)
    line = wrap_parts(d, LINE, f_line, width)
    foot = wrap_parts(d, FOOTER, f_foot, width)

    # (lines, font, color, line height, space after the block)
    blocks = [
        ([LABEL], f_label, accent, 38, 26),
        (head, f_head, ink, 72, 30),
        (line, f_line, ink, 42, 0),
    ]
    foot_lh = 40
    foot_h = foot_lh * len(foot)

    y = EDGE + 6
    boxes = []
    for lines, f, color, lh, after in blocks:
        for t in lines:
            d.text((x0, y), t, font=f, fill=color)
            boxes.append(d.textbbox((x0, y), t, font=f))
            y += lh
        y += after
    upper_end = y

    fy = H - EDGE - foot_h
    if fy - 34 < upper_end:
        sys.exit("the text does not fit: shorten it or reduce the sizes")
    d.line([x0, fy - 22, x1, fy - 22], fill=rule, width=2)
    for t in foot:
        d.text((x0, fy), t, font=f_foot, fill=muted)
        boxes.append(d.textbbox((x0, fy), t, font=f_foot))
        fy += foot_lh

    # Every drawn line of text stays inside the 60 px safe area.
    for l, t, r, b in boxes:
        if l < EDGE or t < EDGE or r > W - EDGE or b > H - EDGE:
            sys.exit("text outside the safe area: %s" % ((l, t, r, b),))
    print("text box: left %d, top %d, right %d, bottom %d" % (
        min(b[0] for b in boxes), min(b[1] for b in boxes),
        max(b[2] for b in boxes), max(b[3] for b in boxes)))

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "arc-share-v%d.png" % args.version)
    img.save(out, optimize=True)
    print("%s  %d x %d  %.0f KB" % (os.path.relpath(out, ROOT), img.width, img.height,
                                    os.path.getsize(out) / 1024))


if __name__ == "__main__":
    main()

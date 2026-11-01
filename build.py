#!/usr/bin/env python3
"""
Build static site from markdown content + Jinja2 templates.

Reads:
    content/**/*.md       markdown with YAML frontmatter
    templates/*.html      Jinja2 templates (base + includes + pages)
    static/               CSS, JS, images (copied verbatim)
    data/                 JSON data files (copied to public/data/)
    series.json           book catalog, exposed as `series` in templates

Writes:
    public/               ready for `firebase deploy`

Usage:
    python build.py
"""

import glob
import json
import os
import re
import shutil

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

# --- Paths ---
CONTENT_DIR = "content"
TEMPLATE_DIR = "templates"
STATIC_DIR = "static"
DATA_DIR = "data"
OUTPUT_DIR = "public"
SERIES_FILE = "series.json"

TRACK_LABELS = {"technical": "Technical Books", "fiction": "Science Fiction"}
TRACK_LEDES = {
    "technical": (
        "Engineering and physics of building space infrastructure — from orbital "
        "rings and mass drivers to propulsion, habitats, and generational ships. "
        "Rigorous enough to teach from; accessible enough to read cover-to-cover."
    ),
    "fiction": (
        "Eight hundred years of human history, constrained by known physics. "
        "Characters live normal lifespans. Propulsion is limited by available "
        "power. Materials are limited by what can reasonably be manufactured. "
        "There are no shortcuts."
    ),
}
TRACK_BOOK_LABELS = {"technical": "Technical Book", "fiction": "Hard Science Fiction Book"}


# --- Jinja2 filters ---
def truncate_excerpt(text, limit=200):
    if text and len(text) > limit:
        return text[:limit] + "..."
    return text or ""


_URL_RE = re.compile(r'(https?://[^\s<>"\')]+)')
_ITALIC_RE = re.compile(r'\*([^*\n]+?)\*')


def ref_markdown(text):
    """Render inline markdown in a reference text string.

    Converts *x* to <em>x</em> and raw URLs to clickable links. Leaves $...$
    math alone (dollar signs are not HTML-sensitive after escaping).
    """
    if not text:
        return ""
    out = str(escape(text))

    def _link(m):
        url = m.group(1)
        trail = ""
        while url and url[-1] in ".,;:!?":
            trail = url[-1] + trail
            url = url[:-1]
        return f'<a href="{url}" rel="noopener">{url}</a>{trail}'

    out = _URL_RE.sub(_link, out)
    out = _ITALIC_RE.sub(r"<em>\1</em>", out)
    return Markup(out)


def to_roman(n):
    if n is None:
        return ""
    try:
        n = int(n)
    except (TypeError, ValueError):
        return str(n)
    if n <= 0 or n >= 4000:
        return str(n)
    pairs = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
             (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
             (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = []
    for value, numeral in pairs:
        while n >= value:
            out.append(numeral)
            n -= value
    return "".join(out)


# --- Jinja2 environment ---
env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html"]),
    keep_trailing_newline=True,
)
env.filters["truncate_excerpt"] = truncate_excerpt
env.filters["roman"] = to_roman
env.filters["ref_markdown"] = ref_markdown


def load_series():
    if os.path.exists(SERIES_FILE):
        with open(SERIES_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


env.globals["series"] = load_series()
SERIES = env.globals["series"]


# --- IO helpers ---
def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# --- Markdown / frontmatter ---
def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = yaml.safe_load(parts[1]) or {}
    if "date" in meta and not isinstance(meta["date"], str):
        meta["date"] = str(meta["date"])
    return meta, parts[2].strip()


def render_markdown(text):
    return markdown.markdown(text, extensions=["tables", "fenced_code"])


def fix_old_urls(html):
    def rewrite_img(m):
        filename = m.group(1)
        filename = re.sub(r"-\d+x\d+\.", ".", filename)
        return f"/images/{filename}"

    html = re.sub(
        r"https?://www\.orbitalring\.space/wp-content/uploads/\d{4}/\d{2}/([^\"')\s]+)",
        rewrite_img,
        html,
    )
    replacements = [
        ("https://www.orbitalring.space/buy-book/", "/series/technical/orbital-rings/"),
        ("https://www.orbitalring.space/buy-book", "/series/technical/orbital-rings/"),
        ("https://www.orbitalring.space/coding-hub/", "/code/"),
        ("https://www.orbitalring.space/about-author-book/", "/about/"),
        ("https://www.orbitalring.space/blog/", "/blog/"),
        ("https://www.orbitalring.space/contact/", "/contact/"),
        ("https://www.orbitalring.space/privacy-policy/", "/privacy/"),
        ("https://www.orbitalring.space/", "/"),
    ]
    for old, new in replacements:
        html = html.replace(old, new)
    return html


def render_markdown_file(path):
    """Read a markdown file and return (meta, rendered_html)."""
    if not os.path.exists(path):
        return {}, ""
    meta, md_body = parse_frontmatter(read_file(path))
    return meta, fix_old_urls(render_markdown(md_body))


# --- Rendering ---
def render_template(template_name, output_path, **context):
    template = env.get_template(template_name)
    write_file(output_path, template.render(**context))
    print(f"  Built: {output_path}")


def build_markdown_page(md_path, output_path, template_name="pages/page.html"):
    meta, html = render_markdown_file(md_path)
    render_template(
        template_name,
        output_path,
        title=meta.get("title", "Untitled"),
        description=meta.get("excerpt", meta.get("title", "")),
        content=html,
        meta=meta,
    )


def build_blog_post(md_path):
    meta, md_body = parse_frontmatter(read_file(md_path))
    slug = meta.get("slug")
    if not slug:
        return None
    html = fix_old_urls(render_markdown(md_body))
    render_template(
        "pages/blog-post.html",
        os.path.join(OUTPUT_DIR, "blog", slug, "index.html"),
        title=meta.get("title", ""),
        description=meta.get("excerpt", meta.get("title", "")),
        content=html,
        post=meta,
    )
    return meta


def build_blog_index(posts):
    sorted_posts = sorted(posts, key=lambda p: p.get("date", ""), reverse=True)
    render_template(
        "pages/blog-index.html",
        os.path.join(OUTPUT_DIR, "blog", "index.html"),
        title="Blog",
        description="Articles on orbital rings, space engineering, and physics",
        posts=sorted_posts,
    )


def build_homepage():
    render_template(
        "pages/home.html",
        os.path.join(OUTPUT_DIR, "index.html"),
        title="Home",
        description=(
            "Paul de Jong — author of Orbital Ring Engineering, "
            "a deep dive into building humanity's highway to space."
        ),
    )


def build_chapter_excerpts():
    """Render any chapter-excerpt markdown files under content/books/.

    Each file at content/books/<book>/<slug>.md is rendered to
    public/books/<book>/<slug>/index.html using the chapter-excerpt template.
    """
    for md_path in sorted(glob.glob(os.path.join(CONTENT_DIR, "books", "*", "*.md"))):
        meta, html = render_markdown_file(md_path)
        rel = os.path.relpath(md_path, os.path.join(CONTENT_DIR, "books"))
        rel_no_ext = os.path.splitext(rel)[0]
        out_path = os.path.join(OUTPUT_DIR, "books", rel_no_ext, "index.html")
        render_template(
            "pages/chapter-excerpt.html",
            out_path,
            title=meta.get("title", "Chapter excerpt"),
            description=meta.get("description", meta.get("title", "")),
            content=html,
            meta=meta,
        )


def get_errata_books():
    """Books available for errata reporting, as an ordered list of dicts
    with `key`, `title`, and `isbn`.

    The `key` is the stable identifier stored on every Firestore errata
    document. Do NOT change an existing key or previously submitted errata
    stop matching their book. New books can be added freely.

    Driven from series.json so adding a book in one place is enough.
    """
    books = []

    # Original single-volume edition (the one currently on Amazon).
    for entry in SERIES.get("legacy", []):
        books.append({
            "key": entry.get("errata_key", entry["slug"]),
            "title": f"{entry['title']} (1st Edition)",
            "isbn": entry.get("isbn", ""),
        })

    # The volumes of the new edition (AST-T1). The key is `errata_key` when a volume carries one (the volumes were renumbered
    # on 2026-10-29 and the keys stayed with their books), else ast-t1-vol-<number>.
    _, ast_t1 = find_book_by_id("ast-t1")
    if ast_t1 and ast_t1.get("volumes"):
        for vol in ast_t1["volumes"]:
            books.append({
                "key": vol.get("errata_key") or f"ast-t1-vol-{vol['number']}",
                "title": f"Vol {to_roman(vol['number'])}: {vol['title']}",
                "isbn": (vol.get("isbns") or {}).get("paperback", ""),
            })

    # Standalone technical books that carry an errata key (Why Space, the economic case, which left the
    # AST-T1 set on 2026-10-31 and keeps its key ast-t1-vol-1).
    for book in SERIES.get("technical", []):
        if not book.get("volumes") and book.get("errata_key"):
            books.append({
                "key": book["errata_key"],
                "title": book["title"],
                "isbn": (book.get("isbns") or {}).get("paperback", ""),
            })

    return books


def build_errata_pages():
    books = get_errata_books()
    books_map = {b["key"]: {"title": b["title"], "isbn": b["isbn"]} for b in books}
    books_json = json.dumps(books_map)

    render_template(
        "pages/errata.html",
        os.path.join(OUTPUT_DIR, "errata", "index.html"),
        title="Errata",
        description="Report and search for book errata",
        errata_books=books,
        errata_books_json=books_json,
    )
    render_template(
        "admin/errata-dashboard.html",
        os.path.join(OUTPUT_DIR, "errata", "admin", "index.html"),
        title="Errata Admin",
        description="Manage book errata submissions",
        errata_books=books,
        errata_books_json=books_json,
    )


def build_404():
    render_template(
        "pages/error-404.html",
        os.path.join(OUTPUT_DIR, "404.html"),
        title="404",
        description="Page not found",
    )


# --- Series generation ---
def build_series_overview():
    intro_meta, intro_html = render_markdown_file(
        os.path.join(CONTENT_DIR, "series", "overview.md")
    )
    render_template(
        "pages/series-overview.html",
        os.path.join(OUTPUT_DIR, "series", "index.html"),
        title="Series",
        description=(
            "Astronomy's Shocking Twist — a 10-book series of technical "
            "engineering and hard science fiction."
        ),
        intro_html=intro_html,
    )


def build_series_track(track):
    intro_meta, intro_html = render_markdown_file(
        os.path.join(CONTENT_DIR, "series", f"{track}.md")
    )
    render_template(
        "pages/series-track.html",
        os.path.join(OUTPUT_DIR, "series", track, "index.html"),
        title=TRACK_LABELS[track],
        description=TRACK_LEDES[track],
        track=track,
        track_label=TRACK_LABELS[track],
        track_lede=TRACK_LEDES[track],
        books=SERIES.get(track, []),
        intro_html=intro_html,
    )


def build_book_page(book, track):
    # Content file can be content/series/{track}/{slug}.md
    # OR content/series/{track}/{slug}/index.md (for multi-volume books).
    content_candidates = [
        os.path.join(CONTENT_DIR, "series", track, f"{book['slug']}.md"),
        os.path.join(CONTENT_DIR, "series", track, book["slug"], "index.md"),
    ]
    book_content = ""
    for candidate in content_candidates:
        if os.path.exists(candidate):
            _, book_content = render_markdown_file(candidate)
            break

    render_template(
        "pages/book-detail.html",
        os.path.join(OUTPUT_DIR, "series", track, book["slug"], "index.html"),
        title=book["title"],
        description=book.get("description", ""),
        track=track,
        track_label=TRACK_LABELS[track],
        track_book_label=f"{TRACK_BOOK_LABELS[track]} {book['id'].upper()}",
        book=book,
        book_content=book_content,
    )


def build_volume_page(book, vol, track):
    out_path = os.path.join(
        OUTPUT_DIR, "series", track, book["slug"], vol["slug"], "index.html"
    )
    # If a custom hub HTML file exists, write it directly. This lets a volume
    # override the default template with a hand-built landing page.
    hub_path = os.path.join(
        CONTENT_DIR, "series", track, book["slug"], f"{vol['slug']}.hub.html"
    )
    if os.path.exists(hub_path):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        shutil.copyfile(hub_path, out_path)
        print(f"  Built: {out_path} (hub)")
        return
    content_path = os.path.join(
        CONTENT_DIR, "series", track, book["slug"], f"{vol['slug']}.md"
    )
    _, vol_content = render_markdown_file(content_path)
    render_template(
        "pages/volume-detail.html",
        out_path,
        title=vol["title"],
        description=f"{book['title']} - Volume {to_roman(vol['number'])}.",
        track=track,
        track_label=TRACK_LABELS[track],
        track_book_label=f"{TRACK_BOOK_LABELS[track]} {book['id'].upper()}",
        book=book,
        vol=vol,
        vol_content=vol_content,
    )


def find_book_by_id(book_id):
    """Return (track, book) for a given book id (case-insensitive)."""
    target = book_id.lower()
    for track in ("technical", "fiction"):
        for book in SERIES.get(track, []):
            if book["id"].lower() == target:
                return track, book
    return None, None


def build_reference_pages():
    """Render a references page for every JSON file in data/references/."""
    for json_path in sorted(glob.glob(os.path.join(DATA_DIR, "references", "*.json"))):
        with open(json_path, encoding="utf-8") as f:
            refs_data = json.load(f)

        book_id = refs_data.get("series_id", "")
        track, book = find_book_by_id(book_id)
        if not book:
            print(f"  WARN: series.json has no book matching {book_id!r}")
            continue

        vol_num = refs_data.get("volume")
        vol = None
        if vol_num is not None and book.get("volumes"):
            vol = next(
                (v for v in book["volumes"] if v["number"] == vol_num), None
            )
            if vol is None:
                print(
                    f"  WARN: {book_id} volume {vol_num} missing from series.json"
                )
                continue

        if vol:
            out_path = os.path.join(
                OUTPUT_DIR, "series", track, book["slug"],
                vol["slug"], "references", "index.html",
            )
        else:
            out_path = os.path.join(
                OUTPUT_DIR, "series", track, book["slug"],
                "references", "index.html",
            )

        render_template(
            "pages/references.html",
            out_path,
            title=refs_data.get("page_title") or f"References — {refs_data.get('volume_title') or refs_data.get('book_title')}",
            description=(
                f"Numbered references for {refs_data.get('book_title')}"
                + (f", Volume {to_roman(vol_num)}" if vol_num else "")
                + "."
            ),
            refs=refs_data,
            track=track,
            track_label=TRACK_LABELS[track],
            book=book,
            vol=vol,
        )


def build_legacy_book():
    legacy_list = SERIES.get("legacy", [])
    if not legacy_list:
        return
    for entry in legacy_list:
        content_path = os.path.join(
            CONTENT_DIR, "series", "technical", f"{entry['slug']}.md"
        )
        _, content_html = render_markdown_file(content_path)
        render_template(
            "pages/legacy-book.html",
            os.path.join(
                OUTPUT_DIR, "series", "technical", entry["slug"], "index.html"
            ),
            title=entry["title"],
            description=entry.get("description", ""),
            content=content_html,
            book=entry,
        )


def build_series():
    build_series_overview()
    for track in ("technical", "fiction"):
        build_series_track(track)
        for book in SERIES.get(track, []):
            build_book_page(book, track)
            if book.get("volumes"):
                for vol in book["volumes"]:
                    build_volume_page(book, vol, track)
    build_legacy_book()
    build_reference_pages()


# --- Review page ---
REVIEW_MD = os.path.join(CONTENT_DIR, "review.md")
REVIEW_BOOKS_MARKER = "<!-- books -->"

# Stores shown as buttons, in display order. Keys match the `review` block
# on each volume / book / legacy entry in series.json. Amazon is built from
# `amazon_asin`; the rest are full URLs pasted into series.json.
REVIEW_STORES = [
    ("goodreads", "Goodreads"),
    ("barnes_noble", "Barnes & Noble"),
    ("kobo", "Kobo"),
    ("apple_books", "Apple Books"),
]
AMAZON_REVIEW_US = "https://www.amazon.com/review/create-review?asin={asin}"
AMAZON_REVIEW_INTL = [
    ("UK", "https://www.amazon.co.uk/review/create-review?asin={asin}"),
    ("DE", "https://www.amazon.de/review/create-review?asin={asin}"),
    ("NL", "https://www.amazon.nl/review/create-review?asin={asin}"),
    ("CA", "https://www.amazon.ca/review/create-review?asin={asin}"),
    ("AU", "https://www.amazon.com.au/review/create-review?asin={asin}"),
]


def review_entry(review, anchor, label, title, cover, placeholder):
    """Turn a series.json `review` block into what the template needs.

    Returns None when no link is set, so books that are not out yet stay
    off the page until their links are added.
    """
    review = review or {}
    asin = (review.get("amazon_asin") or "").strip()
    stores = [
        {"key": key, "name": name, "url": review[key].strip()}
        for key, name in REVIEW_STORES
        if (review.get(key) or "").strip()
    ]
    if not asin and not stores:
        return None
    return {
        "anchor": review.get("anchor") or anchor,
        "label": label,
        "title": title,
        "cover": cover,
        "placeholder": placeholder,
        "amazon_url": AMAZON_REVIEW_US.format(asin=asin) if asin else "",
        "amazon_intl": [
            {"country": c, "url": u.format(asin=asin)} for c, u in AMAZON_REVIEW_INTL
        ] if asin else [],
        "stores": stores,
    }


def get_review_books():
    """Every book or volume in series.json that has at least one review link.

    Multi-volume books contribute one entry per volume (anchor = volume slug,
    e.g. #vol-1). Single books contribute one entry (anchor = book slug).
    Legacy editions come last. The anchor can be overridden with
    `review.anchor`.
    """
    entries = []
    for track in ("technical", "fiction"):
        for book in SERIES.get(track, []):
            if book.get("volumes"):
                for vol in book["volumes"]:
                    entries.append(review_entry(
                        vol.get("review"),
                        anchor=vol["slug"],
                        label=f"{book.get('short_title') or book['title']} · Volume {to_roman(vol['number'])}",
                        title=vol["title"],
                        cover=vol.get("cover_image", ""),
                        placeholder=f"Vol {to_roman(vol['number'])}",
                    ))
            else:
                entries.append(review_entry(
                    book.get("review"),
                    anchor=book["slug"],
                    label=book["id"].upper(),
                    title=book["title"],
                    cover=book.get("cover_image", ""),
                    placeholder=book["id"].upper(),
                ))
    for entry in SERIES.get("legacy", []):
        entries.append(review_entry(
            entry.get("review"),
            anchor=entry["slug"],
            label="Original single-volume edition",
            title=entry["title"],
            cover=entry.get("cover_image", ""),
            placeholder="1st Ed",
        ))
    return [e for e in entries if e]


def build_review_page():
    """Render /review from content/review.md plus the review links in
    series.json. The markdown is split at `<!-- books -->`: the part above
    is the intro, the part below closes the page (the instructors section).
    """
    if not os.path.exists(REVIEW_MD):
        return
    meta, md_body = parse_frontmatter(read_file(REVIEW_MD))
    intro_md, _, outro_md = md_body.partition(REVIEW_BOOKS_MARKER)
    render_template(
        "pages/review.html",
        os.path.join(OUTPUT_DIR, "review", "index.html"),
        title=meta.get("title", "Leave a review"),
        description=meta.get("excerpt", ""),
        intro_html=fix_old_urls(render_markdown(intro_md)),
        outro_html=fix_old_urls(render_markdown(outro_md)),
        review_books=get_review_books(),
    )


# --- Sitemap ---
SITE_URL = "https://pauldejong.com"
# Output paths (relative to public/, forward slashes) left out of the sitemap:
# error page, the errata admin dashboard, and the post-subscribe thank-you.
SITEMAP_EXCLUDE = {"404.html", "errata/admin/index.html", "thanks/index.html"}


def build_sitemap():
    """Write public/sitemap.xml listing every built HTML page.

    Runs last so it picks up everything the build wrote. URLs have no
    trailing slash because firebase.json sets cleanUrls and
    trailingSlash: false.
    """
    urls = []
    for path in sorted(glob.glob(os.path.join(OUTPUT_DIR, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(path, OUTPUT_DIR).replace(os.sep, "/")
        if rel in SITEMAP_EXCLUDE:
            continue
        if rel == "index.html":
            loc = SITE_URL + "/"
        elif rel.endswith("/index.html"):
            loc = f"{SITE_URL}/{rel[:-len('/index.html')]}"
        else:
            loc = f"{SITE_URL}/{rel[:-len('.html')]}"
        urls.append(loc)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines += [f"  <url><loc>{escape(u)}</loc></url>" for u in urls]
    lines.append("</urlset>")
    write_file(os.path.join(OUTPUT_DIR, "sitemap.xml"), "\n".join(lines) + "\n")
    print(f"  Built: {os.path.join(OUTPUT_DIR, 'sitemap.xml')} ({len(urls)} URLs)")


# --- File operations ---
def clean_output():
    """Remove the output directory contents.

    On some filesystems (notably Windows shares mounted into a Linux
    sandbox) individual files cannot be deleted. We do best-effort
    cleanup and rely on subsequent writes to overwrite stale content.
    """
    if not os.path.exists(OUTPUT_DIR):
        return
    for item in glob.glob(os.path.join(OUTPUT_DIR, "*")):
        try:
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
        except (PermissionError, OSError) as exc:
            # Skip files we cannot delete; they will be overwritten by
            # write_file on the next build pass.
            print(f"  WARN: could not remove {item}: {exc}")


def copy_tree(src, dst, label):
    if os.path.exists(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
        print(f"  Copied {label}")


PAGE_MAP = {
    "content/about.md": "about",
    "content/code.md": "code",
    "content/contact.md": "contact",
    "content/privacy.md": "privacy",
    "content/thanks.md": "thanks",
}


def build():
    clean_output()
    copy_tree(STATIC_DIR, OUTPUT_DIR, "static assets")
    copy_tree(DATA_DIR, os.path.join(OUTPUT_DIR, "data"), "data files")

    build_homepage()

    for md_path, out_dir in PAGE_MAP.items():
        if os.path.exists(md_path):
            build_markdown_page(
                md_path, os.path.join(OUTPUT_DIR, out_dir, "index.html")
            )

    posts = []
    for md_path in sorted(glob.glob(os.path.join(CONTENT_DIR, "blog", "*.md"))):
        meta = build_blog_post(md_path)
        if meta:
            posts.append(meta)

    build_blog_index(posts)
    build_series()
    build_chapter_excerpts()
    build_errata_pages()
    build_review_page()
    build_404()
    build_sitemap()

    print("\nBuild complete!")


if __name__ == "__main__":
    build()

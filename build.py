#!/usr/bin/env python3
"""
Build static site from markdown content + Jinja2 templates.

Reads:
    content/**/*.md       markdown with YAML frontmatter
    templates/*.html      Jinja2 templates (base + includes + pages)
    static/               CSS, JS, images (copied verbatim)
    data/                 JSON data files (copied to public/data/)
    data/author.json      the author record, exposed as `author` in templates
    series.json           book catalog, exposed as `series` in templates
    site.json             site settings (analytics), exposed as `site` in templates

Writes:
    public/               ready for `firebase deploy`
    METADATA.md           human-readable export of the author and book metadata
                          (generated; edit data/author.json and series.json instead)

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

try:
    from PIL import Image
except ImportError:  # image sizes on the press kit are optional
    Image = None

# --- Paths ---
CONTENT_DIR = "content"
TEMPLATE_DIR = "templates"
STATIC_DIR = "static"
DATA_DIR = "data"
OUTPUT_DIR = "public"
SERIES_FILE = "series.json"
SITE_FILE = "site.json"
AUTHOR_FILE = os.path.join(DATA_DIR, "author.json")
METADATA_MD = "METADATA.md"

SITE_URL = "https://pauldejong.com"

# Group labels are filled from series.json (its `groups` list) once the catalog is loaded; see load_series().
TRACK_LABELS = {}
TRACK_LEDES = {}
TRACK_BOOK_LABELS = {}


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


def word_count(text):
    return len((text or "").split())


def paragraphs(text):
    """Split a bio string on blank lines into a list of paragraphs."""
    return [p.strip() for p in (text or "").split("\n\n") if p.strip()]


# --- Jinja2 environment ---
env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html"]),
    keep_trailing_newline=True,
)
env.filters["truncate_excerpt"] = truncate_excerpt
env.filters["roman"] = to_roman
env.filters["ref_markdown"] = ref_markdown
env.filters["word_count"] = word_count
env.filters["paragraphs"] = paragraphs


def longdate(value, year=True):
    """2026-11-15 -> '15 November 2026' (or '15 November' with year=False).
    A month-only date, 2026-12, -> 'December 2026' (or 'December')."""
    if not value:
        return ""
    try:
        parts = str(value).split("-")
        months = ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"]
        if len(parts) == 2:
            y, m = parts
            out = months[int(m) - 1]
        else:
            y, m, d = parts
            out = f"{int(d)} {months[int(m) - 1]}"
        return f"{out} {y}" if year else out
    except (ValueError, IndexError):
        return str(value)


env.filters["longdate"] = longdate


def load_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_series():
    return load_json(SERIES_FILE)


env.globals["series"] = load_series()
SERIES = env.globals["series"]


def load_site():
    """Site-wide settings (site.json): analytics provider and ids."""
    return load_json(SITE_FILE)


env.globals["site"] = load_site()

AUTHOR = load_json(AUTHOR_FILE)
if not AUTHOR:
    raise SystemExit(f"{AUTHOR_FILE} is missing; the templates need the author record")
env.globals["author"] = AUTHOR
env.globals["site_url"] = SITE_URL

META_DEFAULTS = SERIES.get("metadata_defaults") or {
    "author": AUTHOR.get("name", ""),
    "publisher": (AUTHOR.get("publisher") or {}).get("name", ""),
    "language": "en",
}

GROUPS = SERIES.get("groups") or [
    {"key": "technical", "label": "Technical Books", "line": "", "book_label": "Technical Book"},
    {"key": "fiction", "label": "Science Fiction", "line": "", "book_label": "Hard Science Fiction Book"},
]
GROUP_KEYS = [g["key"] for g in GROUPS]
for _g in GROUPS:
    TRACK_LABELS[_g["key"]] = _g["label"]
    TRACK_LEDES[_g["key"]] = _g.get("line", "")
    TRACK_BOOK_LABELS[_g["key"]] = _g.get("book_label", "Book")
env.globals["groups"] = GROUPS


def find_group(key):
    return next((g for g in GROUPS if g["key"] == key), None)


def featured_book():
    """The book (and volume, when the book has volumes) the home page sells, from series.json `featured`."""
    f = SERIES.get("featured") or {}
    track, book = find_book_by_id(f.get("book", ""))
    if not book:
        return None, None, None
    vol = None
    if f.get("volume") is not None and book.get("volumes"):
        vol = next((v for v in book["volumes"] if v["number"] == f["volume"]), None)
    return track, book, vol


def primary_headshot():
    shots = AUTHOR.get("headshots") or []
    for shot in shots:
        if shot.get("primary"):
            return shot
    return shots[0] if shots else None


env.globals["primary_headshot"] = primary_headshot()


# --- IO helpers ---
def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def absolute_url(path):
    """'/images/x.png' -> 'https://pauldejong.com/images/x.png'. Full URLs pass through."""
    if not path:
        return ""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return SITE_URL + (path if path.startswith("/") else "/" + path)


def page_url_for(output_path):
    """The canonical URL of a built page, matching the sitemap rules
    (cleanUrls and trailingSlash: false in firebase.json; the home page
    keeps its slash)."""
    rel = os.path.relpath(output_path, OUTPUT_DIR).replace(os.sep, "/")
    if rel == "index.html":
        return SITE_URL + "/"
    if rel.endswith("/index.html"):
        return f"{SITE_URL}/{rel[:-len('/index.html')]}"
    return f"{SITE_URL}/{rel[:-len('.html')]}"


def image_size(static_path):
    """(width, height) of an image under static/, by its site path, or None."""
    if not Image or not static_path:
        return None
    path = os.path.join(STATIC_DIR, static_path.lstrip("/"))
    try:
        with Image.open(path) as im:
            return im.size
    except (OSError, ValueError):
        return None


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


# --- Publication metadata ---
FORMAT_LABELS = {
    "hardcover": "Hardcover",
    "paperback": "Paperback",
    "kindle": "Kindle",
    "epub": "E-book",
}
SCHEMA_FORMATS = {
    "hardcover": "https://schema.org/Hardcover",
    "paperback": "https://schema.org/Paperback",
    "kindle": "https://schema.org/EBook",
    "epub": "https://schema.org/EBook",
}
STATUS_LABELS = {
    "published": "Published",
    "pre_order": "Pre-order",
    "forthcoming": "Forthcoming",
    "planned": "Planned",
    "replaced": "Replaced by a later edition",
    "in_progress": "In progress",
    "coming_soon": "Coming soon",
}
_ASIN_RE = re.compile(r"/dp/([A-Z0-9]{10})")


def book_full_title(book, vol=None):
    """'Orbital Ring Engineering, Volume I: Space Mass Transit Complete Design Review'
    or 'Why Space: Apollo, the Lost Decades, ...'."""
    if vol:
        return f"{book['title']}, Volume {to_roman(vol['number'])}: {vol['title']}"
    if book.get("subtitle"):
        return f"{book['title']}: {book['subtitle']}"
    return book["title"]


def inherit(item, book, group, key, default=None):
    """A metadata field from the volume, else the book, else the group, else the catalog defaults."""
    for source in (item, book, group):
        if source and source.get(key) not in (None, "", []):
            return source[key]
    return META_DEFAULTS.get(key, default)


def asin_from(url):
    m = _ASIN_RE.search(url or "")
    return m.group(1) if m else ""


def publication_details(book, vol, track):
    """Everything the Publication details block, the Book schema and
    METADATA.md need for one book or volume, in one dict."""
    group = find_group(track) or {}
    item = vol or book
    isbns = item.get("isbns") or {}
    if not isbns and item.get("isbn"):
        isbns = {"paperback": item["isbn"]}
    purchase = item.get("purchase") or item.get("amazon") or {}
    prices = item.get("prices") or {}
    formats = item.get("formats") or [k for k in ("hardcover", "paperback", "kindle") if isbns.get(k) or purchase.get(k)]
    formats = [f for f in ("hardcover", "paperback", "kindle", "epub") if f in formats]  # the usual order

    series_parts = []
    if group.get("series"):
        series_parts.append(f"{group['series']}, {group.get('label', '').lower()}".rstrip(", "))
    if vol:
        series_parts.append(f"{book['title']}, Volume {to_roman(vol['number'])} of {len(book.get('volumes') or [])}")
    elif book.get("kind") == "first_edition":
        series_parts.append("First edition, replaced by Orbital Ring Engineering in three volumes")

    editions = []
    for fmt in ("hardcover", "paperback", "kindle", "epub"):
        isbn = isbns.get(fmt) or (isbns.get("epub") if fmt == "kindle" else "")
        url = purchase.get(fmt) or ""
        price = prices.get(fmt)
        if fmt == "epub" and ("kindle" in formats or purchase.get("kindle")):
            continue  # the e-book is listed once, under Kindle
        if fmt not in formats and not isbn and not url:
            continue
        editions.append({
            "format": fmt,
            "label": FORMAT_LABELS[fmt],
            "isbn_label": "e-book" if fmt in ("kindle", "epub") else FORMAT_LABELS[fmt].lower(),
            "schema_format": SCHEMA_FORMATS[fmt],
            "isbn": isbn,
            "url": url,
            "asin": asin_from(url) or ((item.get("review") or {}).get("amazon_asin") if fmt == "hardcover" else ""),
            "price": price,
        })

    cover = item.get("cover_image") or book.get("cover_image") or ""
    details = {
        "full_title": book_full_title(book, vol),
        "title": item["title"],
        "subtitle": item.get("subtitle", "") if not vol else "",
        "author": inherit(item, book, group, "author"),
        "publisher": inherit(item, book, group, "publisher"),
        "language": inherit(item, book, group, "language", "en"),
        "series": "; ".join(series_parts),
        "series_name": group.get("series") or "",
        "status": STATUS_LABELS.get(item.get("status") or book.get("status") or "", (item.get("status") or "").replace("_", " ").capitalize()),
        "status_key": item.get("status") or book.get("status") or "",
        "release_date": item.get("release_date") or "",
        "pages": item.get("pages"),
        "chapters": item.get("chapters"),
        "formats": [FORMAT_LABELS[f] for f in formats if f in FORMAT_LABELS],
        "editions": editions,
        "lccn": item.get("lccn", ""),
        "subjects": inherit(item, book, group, "subjects", []) or [],
        "bisac_codes": inherit(item, book, group, "bisac_codes", []) or [],
        "audience": inherit(item, book, group, "audience", ""),
        "description": item.get("description") or book.get("description") or "",
        "headline": item.get("headline", ""),
        "cover": cover,
        "cover_size": image_size(cover),
        "cover_note": item.get("cover_note") or book.get("cover_note") or "",
        "links": item.get("links") or {},
        "review": item.get("review") or {},
        "catalog_id": book.get("id", ""),
        "errata_key": item.get("errata_key", ""),
    }

    # The rows the template prints, in order. Empty values are left out.
    rows = [
        ("Title", details["full_title"]),
        ("Author", details["author"]),
        ("Series", details["series"]),
        ("Publisher", details["publisher"]),
        ("Publication date", longdate(details["release_date"]) if details["release_date"] else ""),
        ("Status", details["status"] if not details["release_date"] or details["status_key"] != "published" else ""),
        ("Language", "English" if details["language"] == "en" else details["language"]),
        ("Pages", str(details["pages"]) if details["pages"] else ""),
        ("Chapters", str(details["chapters"]) if details["chapters"] else ""),
        ("Formats", ", ".join(details["formats"])),
    ]
    for ed in editions:
        if ed["isbn"]:
            rows.append((f"ISBN-13, {ed['isbn_label']}", ed["isbn"]))
    for ed in editions:
        if ed["asin"]:
            rows.append((f"Amazon ASIN, {ed['label'].lower()}", ed["asin"]))
    rows += [
        ("Library of Congress Control Number", details["lccn"]),
        ("Subjects", "; ".join(details["subjects"])),
        ("BISAC codes", ", ".join(details["bisac_codes"])),
        ("Audience", details["audience"]),
    ]
    for ed in editions:
        if ed["price"]:
            rows.append((f"List price, {ed['label'].lower()}", f"US$ {ed['price']:.2f}"))
    details["rows"] = [(k, v) for k, v in rows if v]
    return details


# --- Structured data (JSON-LD) ---
PERSON_ID = SITE_URL + "/#person"
WEBSITE_ID = SITE_URL + "/#website"


def person_schema():
    shot = primary_headshot()
    same_as = [u for u in (AUTHOR.get("profiles") or {}).values() if u]
    same_as += [u for u in (AUTHOR.get("sites") or {}).get("alternate_domains", []) if u]
    for key in ("project",):
        u = (AUTHOR.get("sites") or {}).get(key)
        if u:
            same_as.append(u)
    person = {
        "@type": "Person",
        "@id": PERSON_ID,
        "name": AUTHOR.get("name"),
        "givenName": AUTHOR.get("given_name"),
        "additionalName": AUTHOR.get("additional_name"),
        "familyName": AUTHOR.get("family_name"),
        "jobTitle": AUTHOR.get("job_title", "Author"),
        "description": (AUTHOR.get("bios") or {}).get("one_line", ""),
        "url": SITE_URL + "/",
        "mainEntityOfPage": SITE_URL + "/about",
        "sameAs": same_as,
    }
    if shot:
        person["image"] = absolute_url(shot["file"])
    if (AUTHOR.get("contact") or {}).get("general"):
        person["email"] = "mailto:" + AUTHOR["contact"]["general"]
    return {k: v for k, v in person.items() if v}


def website_schema():
    return {
        "@type": "WebSite",
        "@id": WEBSITE_ID,
        "url": SITE_URL + "/",
        "name": AUTHOR.get("name"),
        "description": (AUTHOR.get("seo") or {}).get("home_description", ""),
        "publisher": {"@id": PERSON_ID},
        "inLanguage": "en",
    }


def book_schema(details, url):
    work_examples = []
    for ed in details["editions"]:
        ex = {
            "@type": "Book",
            "bookFormat": ed["schema_format"],
            "name": details["full_title"],
        }
        if ed["isbn"]:
            ex["isbn"] = ed["isbn"]
        if ed["url"]:
            offer = {"@type": "Offer", "url": ed["url"], "availability": "https://schema.org/InStock"
                     if details["status_key"] == "published" else "https://schema.org/PreOrder"}
            if ed["price"]:
                offer["price"] = f"{ed['price']:.2f}"
                offer["priceCurrency"] = "USD"
            ex["offers"] = offer
        work_examples.append(ex)
    is_part_of = []
    if details["series_name"]:
        is_part_of.append({"@type": "BookSeries", "name": details["series_name"]})
    schema = {
        "@type": "Book",
        "@id": url + "#book",
        "url": url,
        "name": details["full_title"],
        "author": {"@id": PERSON_ID},
        "publisher": {"@type": "Organization", "name": details["publisher"]},
        "inLanguage": details["language"],
        "description": details["description"],
        "image": absolute_url(details["cover"]) if details["cover"] else "",
        "datePublished": details["release_date"],
        "numberOfPages": details["pages"],
        "about": details["subjects"],
        "audience": {"@type": "Audience", "audienceType": details["audience"]} if details["audience"] else None,
        "isPartOf": is_part_of,
        "workExample": work_examples,
    }
    return {k: v for k, v in schema.items() if v}


def profile_page_schema(url):
    return {"@type": "ProfilePage", "@id": url, "url": url, "mainEntity": {"@id": PERSON_ID}}


def blog_posting_schema(post, url):
    schema = {
        "@type": "BlogPosting",
        "@id": url,
        "url": url,
        "headline": post.get("title", ""),
        "description": post.get("excerpt", ""),
        "datePublished": post.get("date", ""),
        "author": {"@id": PERSON_ID},
        "publisher": {"@id": PERSON_ID},
        "mainEntityOfPage": url,
    }
    return {k: v for k, v in schema.items() if v}


def schema_json(extra):
    """The JSON-LD graph for a page: the site, the author and the page's own entities."""
    graph = [website_schema(), person_schema()] + [s for s in (extra or []) if s]
    text = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)
    return Markup(text.replace("</", "<\\/"))


# --- Rendering ---
def render_template(template_name, output_path, **context):
    """Render a template. Every page gets its canonical URL, an Open Graph
    type and image, and a JSON-LD graph; a builder can pass og_type,
    og_image (a site path) and schema (a list of extra entities)."""
    template = env.get_template(template_name)
    url = page_url_for(output_path)
    context.setdefault("page_url", url)
    context.setdefault("og_type", "website")
    context["og_image"] = absolute_url(context.get("og_image") or AUTHOR.get("default_share_image", ""))
    context["schema_json"] = schema_json(context.pop("schema", None))
    write_file(output_path, template.render(**context))
    print(f"  Built: {output_path}")


def build_markdown_page(md_path, output_path, template_name="pages/page.html", **extra):
    meta, html = render_markdown_file(md_path)
    render_template(
        template_name,
        output_path,
        title=meta.get("title", "Untitled"),
        description=meta.get("excerpt", meta.get("title", "")),
        content=html,
        meta=meta,
        **extra,
    )


def build_about_page():
    """The About page: third-person copy from content/about.md, the primary
    headshot, and a ProfilePage schema so search engines treat it as the
    author's profile."""
    md_path = "content/about.md"
    if not os.path.exists(md_path):
        return
    out = os.path.join(OUTPUT_DIR, "about", "index.html")
    shot = primary_headshot()
    build_markdown_page(
        md_path, out, "pages/about.html",
        og_type="profile",
        og_image=shot["file"] if shot else None,
        schema=[profile_page_schema(page_url_for(out))],
    )


def build_blog_post(md_path):
    meta, md_body = parse_frontmatter(read_file(md_path))
    slug = meta.get("slug")
    if not slug:
        return None
    html = fix_old_urls(render_markdown(md_body))
    out = os.path.join(OUTPUT_DIR, "blog", slug, "index.html")
    render_template(
        "pages/blog-post.html",
        out,
        title=meta.get("title", ""),
        description=meta.get("excerpt", meta.get("title", "")),
        content=html,
        post=meta,
        og_type="article",
        schema=[blog_posting_schema(meta, page_url_for(out))],
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
    track, book, vol = featured_book()
    item = vol or book
    seo = AUTHOR.get("seo") or {}
    schema = []
    if book:
        details = publication_details(book, vol, track)
        schema.append(book_schema(details, absolute_url(item.get("links", {}).get("overview", "/"))))
    render_template(
        "pages/home.html",
        os.path.join(OUTPUT_DIR, "index.html"),
        title=seo.get("home_title") or AUTHOR.get("name", "Home"),
        description=seo.get("home_description") or (item or {}).get("headline") or "",
        featured_track=track,
        featured=book,
        featured_vol=vol,
        og_image=(item or {}).get("cover_image"),
        schema=schema,
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
            og_type="article",
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

    # The 2025 first edition (the `related` group, kind first_edition; `legacy` in older catalogs).
    first_editions = [b for b in SERIES.get("related", []) if b.get("kind") == "first_edition"]
    first_editions += SERIES.get("legacy", [])
    for entry in first_editions:
        books.append({
            "key": entry.get("errata_key", entry["slug"]),
            "slug": entry.get("errata_slug"),
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
                "slug": vol.get("errata_slug"),
                "title": f"Vol {to_roman(vol['number'])}: {vol['title']}",
                "isbn": (vol.get("isbns") or {}).get("paperback", ""),
            })

    # Every other standalone book that carries an errata key, in any group (Why Space keeps ast-t1-vol-1).
    seen = {bk["key"] for bk in books}
    for key in GROUP_KEYS:
        for book in SERIES.get(key, []):
            ek = book.get("errata_key")
            if ek and not book.get("volumes") and ek not in seen:
                books.append({
                    "key": ek,
                    "slug": book.get("errata_slug"),
                    "title": book["title"],
                    "isbn": (book.get("isbns") or {}).get("paperback", ""),
                })
                seen.add(ek)

    return books


def get_errata_aliases(books):
    """The alias table: the slug shown in every /errata/?book= link to the
    Firestore key it stands for. Read from series.json `errata_aliases`,
    checked against each book's `errata_slug`; the page's JavaScript resolves
    the slug to the key, so nothing stored in Firestore changes.
    """
    aliases = dict(SERIES.get("errata_aliases") or {})
    keys = {b["key"] for b in books}
    for slug, key in aliases.items():
        if key not in keys:
            raise SystemExit(f"errata_aliases: {slug} points at unknown errata key {key}")
    # Every book's own errata_slug must be in the table and point at its own key.
    for b in books:
        slug = b.get("slug")
        if slug and aliases.get(slug) != b["key"]:
            raise SystemExit(f"errata_slug {slug} of {b['title']} is not aliased to its key {b['key']}")
    return aliases


def build_errata_pages():
    books = get_errata_books()
    books_map = {b["key"]: {"title": b["title"], "isbn": b["isbn"]} for b in books}
    books_json = json.dumps(books_map)
    aliases_json = json.dumps(get_errata_aliases(books))

    render_template(
        "pages/errata.html",
        os.path.join(OUTPUT_DIR, "errata", "index.html"),
        title="Errata",
        description="Report and search for book errata",
        errata_books=books,
        errata_books_json=books_json,
        errata_aliases_json=aliases_json,
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
    """The Books page: every group of the catalog, in catalog order."""
    intro_meta, intro_html = render_markdown_file(
        os.path.join(CONTENT_DIR, "series", "overview.md")
    )
    render_template(
        "pages/series-overview.html",
        os.path.join(OUTPUT_DIR, "series", "index.html"),
        title="Books",
        description=(
            "The books of Paul G. de Jong: the Astronomy's Shocking Twist series, "
            "five technical works and five hard science fiction novels, and the related books."
        ),
        intro_html=intro_html,
        group_list=[(g, SERIES.get(g["key"], [])) for g in GROUPS],
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
        group=find_group(track),
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

    out_path = os.path.join(OUTPUT_DIR, "series", track, book["slug"], "index.html")
    pub = publication_details(book, None, track)
    # The 2025 first edition keeps its own page layout.
    template = "pages/legacy-book.html" if book.get("kind") == "first_edition" else "pages/book-detail.html"
    render_template(
        template,
        out_path,
        title=book["title"],
        description=book.get("description", ""),
        track=track,
        track_label=TRACK_LABELS[track],
        track_book_label=f"{TRACK_BOOK_LABELS[track]} {book['id'].upper()}",
        book=book,
        book_content=book_content,
        content=book_content,
        group=find_group(track),
        pub=pub,
        og_type="book",
        og_image=book.get("cover_image"),
        schema=[book_schema(pub, page_url_for(out_path))],
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
    # An optional table of contents beside the page copy: <slug>.toc.md
    _, vol_toc = render_markdown_file(
        os.path.join(CONTENT_DIR, "series", track, book["slug"], f"{vol['slug']}.toc.md")
    )
    pub = publication_details(book, vol, track)
    render_template(
        "pages/volume-detail.html",
        out_path,
        title=pub["full_title"],
        description=vol.get("headline") or f"{book['title']} - Volume {to_roman(vol['number'])}.",
        track=track,
        track_label=TRACK_LABELS[track],
        track_book_label=f"{TRACK_BOOK_LABELS[track]} {book['id'].upper()}",
        book=book,
        vol=vol,
        vol_content=vol_content,
        vol_toc=vol_toc,
        group=find_group(track),
        pub=pub,
        og_type="book",
        og_image=vol.get("cover_image") or book.get("cover_image"),
        schema=[book_schema(pub, page_url_for(out_path))],
    )


def find_book_by_id(book_id):
    """Return (group key, book) for a given book id (case-insensitive), searching every group."""
    target = (book_id or "").lower()
    for track in GROUP_KEYS:
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


def build_series():
    build_series_overview()
    for track in GROUP_KEYS:
        build_series_track(track)
        for book in SERIES.get(track, []):
            # A planned series with no entries yet (the children's books) has no page.
            if book.get("kind") == "children" and not (book.get("series") or {}).get("entries"):
                continue
            build_book_page(book, track)
            if book.get("volumes"):
                for vol in book["volumes"]:
                    build_volume_page(book, vol, track)
    build_reference_pages()


# --- Press kit ---
def all_publication_details():
    """(group, book, vol, details) for every book and volume with a page, in catalog order."""
    out = []
    for track in GROUP_KEYS:
        group = find_group(track)
        for book in SERIES.get(track, []):
            if book.get("kind") == "children" and not (book.get("series") or {}).get("entries"):
                continue
            if book.get("volumes"):
                for vol in book["volumes"]:
                    out.append((group, book, vol, publication_details(book, vol, track)))
            else:
                out.append((group, book, None, publication_details(book, None, track)))
    return out


def build_press_page():
    """The press kit at /press/: bios, headshots, covers, book facts and
    talking points, all from data/author.json and series.json. The intro
    text, if any, comes from content/press.md."""
    intro_meta, intro_html = render_markdown_file(os.path.join(CONTENT_DIR, "press.md"))
    headshots = []
    for shot in AUTHOR.get("headshots") or []:
        shot = dict(shot)
        size = image_size(shot["file"])
        if size and not shot.get("width"):
            shot["width"], shot["height"] = size
        headshots.append(shot)
    # Covers: every book or volume with a real cover file, once each.
    covers, seen = [], set()
    for group, book, vol, details in all_publication_details():
        cover = details["cover"]
        if not cover or cover in seen or details.get("cover_note") == "mock cover":
            continue
        seen.add(cover)
        covers.append({
            "title": details["full_title"],
            "file": cover,
            "size": details["cover_size"],
            "status": details["status"],
            "page": details["links"].get("overview", ""),
        })
    # Books with release data (ISBNs) get a facts block on the press page.
    books = [d for g, b, v, d in all_publication_details() if d["editions"] and any(e["isbn"] for e in d["editions"])]
    out = os.path.join(OUTPUT_DIR, "press", "index.html")
    seo = AUTHOR.get("seo") or {}
    render_template(
        "pages/press.html",
        out,
        title=seo.get("press_title", "Press kit"),
        description=intro_meta.get("excerpt") or f"Press kit for {AUTHOR.get('name')}: bios, headshots, cover art, book data and talking points.",
        intro_html=intro_html,
        headshots=headshots,
        covers=covers,
        press_books=books,
        og_type="profile",
        og_image=(primary_headshot() or {}).get("file"),
        schema=[profile_page_schema(page_url_for(out))],
    )


# --- METADATA.md ---
def write_metadata_md():
    """A human-readable export of everything in data/author.json and
    series.json that a store listing, a catalog or a back cover needs.
    Generated on every build; do not edit by hand."""
    L = []
    w = L.append
    name = AUTHOR.get("name", "")
    w(f"# Metadata: {name}")
    w("")
    w("Generated by `build.py` from `data/author.json` and `series.json`. Edit those files, not this one. "
      "Everything here is also rendered on the site (page heads, the Publication details blocks, the About page and the press kit at /press/).")
    w("")
    w("## Author")
    w("")
    rows = [
        ("Name", name),
        ("Sort name", AUTHOR.get("sort_name", "")),
        ("Initials / mark", AUTHOR.get("initials", "")),
        ("Handle", AUTHOR.get("handle", "")),
        ("Tagline", AUTHOR.get("tagline", "")),
        ("Website", (AUTHOR.get("sites") or {}).get("primary", "")),
        ("Alternate domains", ", ".join((AUTHOR.get("sites") or {}).get("alternate_domains", []))),
        ("Series domains", ", ".join((AUTHOR.get("sites") or {}).get("series_domains", []))),
        ("Project site", (AUTHOR.get("sites") or {}).get("project", "")),
        ("Publisher / imprint", (AUTHOR.get("publisher") or {}).get("name", "")),
        ("ISBN prefix", (AUTHOR.get("publisher") or {}).get("isbn_prefix", "")),
        ("Distribution", (AUTHOR.get("publisher") or {}).get("distribution", "")),
    ]
    for k, v in (AUTHOR.get("contact") or {}).items():
        rows.append((f"Contact, {k}", v))
    for k, v in (AUTHOR.get("profiles") or {}).items():
        rows.append((f"Profile, {k.replace('_', ' ')}", v or "(empty)"))
    w("| Field | Value |")
    w("|---|---|")
    for k, v in rows:
        w(f"| {k} | {v} |")
    w("")
    w("### Headshots")
    w("")
    shots = AUTHOR.get("headshots") or []
    if not shots:
        w("None yet.")
    for s in shots:
        size = f"{s.get('width')} x {s.get('height')} px" if s.get("width") else ""
        w(f"- `{s['file']}` {size} {'(primary)' if s.get('primary') else ''} {s.get('label', '')}. Alt: {s.get('alt', '')}. Credit: {s.get('credit') or '(none)'}")
    w("")
    for key, label in (("one_line", "One-line bio"), ("short", "Short bio"), ("medium", "Medium bio"), ("long", "Long bio")):
        text = (AUTHOR.get("bios") or {}).get(key, "")
        w(f"### {label} ({word_count(text)} words)")
        w("")
        w(text)
        w("")
    w("### Talking points")
    w("")
    for tp in AUTHOR.get("talking_points") or []:
        w(f"- {tp}")
    w("")
    w("### SEO")
    w("")
    for k, v in (AUTHOR.get("seo") or {}).items():
        w(f"- {k}: {v}")
    w("")
    w("## Books")
    w("")
    empties = []
    for group, book, vol, d in all_publication_details():
        w(f"### {d['full_title']}")
        w("")
        w(f"Catalog id `{d['catalog_id']}`" + (f", volume {vol['number']}" if vol else "") + f". Group: {group['label']}. Page: {absolute_url(d['links'].get('overview', ''))}")
        w("")
        w("| Field | Value |")
        w("|---|---|")
        for k, v in d["rows"]:
            w(f"| {k} | {v} |")
        for ed in d["editions"]:
            if ed["url"]:
                w(f"| Buy link, {ed['label'].lower()} | {ed['url']} |")
        for k in ("excerpt", "references", "errata", "review"):
            if d["links"].get(k):
                w(f"| Link, {k} | {absolute_url(d['links'][k])} |")
        for k, v in (d["review"] or {}).items():
            if v and k != "anchor":
                w(f"| Review link, {k.replace('_', ' ')} | {v} |")
        if d["cover"]:
            size = f" ({d['cover_size'][0]} x {d['cover_size'][1]} px)" if d["cover_size"] else ""
            w(f"| Cover file | `static{d['cover']}`{size}{' (mock cover)' if d['cover_note'] == 'mock cover' else ''} |")
        w("")
        if d["headline"]:
            w(f"**Headline.** {d['headline']}")
            w("")
        if d["description"]:
            w(f"**Description.** {d['description']}")
            w("")
        # What is still missing for a book that has release data.
        if d["editions"]:
            for ed in d["editions"]:
                if not ed["isbn"]:
                    empties.append(f"{d['full_title']}: ISBN, {ed['isbn_label']}")
                if not ed["url"]:
                    empties.append(f"{d['full_title']}: buy link, {ed['label'].lower()}")
            if not d["release_date"]:
                empties.append(f"{d['full_title']}: release date")
            if not d["pages"]:
                empties.append(f"{d['full_title']}: page count")
            if not d["bisac_codes"]:
                empties.append(f"{d['full_title']}: BISAC codes")
            if not (d["review"] or {}).get("amazon_asin"):
                empties.append(f"{d['full_title']}: review ASIN")
    w("## Still empty")
    w("")
    w("Fields a store listing or the site will need that are not filled in yet, for the books that have release data.")
    w("")
    for k, v in (AUTHOR.get("profiles") or {}).items():
        if not v:
            empties.insert(0, f"Author profile: {k.replace('_', ' ')}")
    for e in empties:
        w(f"- [ ] {e}")
    w("")
    write_file(METADATA_MD, "\n".join(L))
    print(f"  Built: {METADATA_MD}")


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
    for track in GROUP_KEYS:
        for book in SERIES.get(track, []):
            if book.get("kind") == "first_edition":
                entries.append(review_entry(
                    book.get("review"),
                    anchor=book["slug"],
                    label="Original single-volume edition",
                    title=book["title"],
                    cover=book.get("cover_image", ""),
                    placeholder="1st Ed",
                ))
            elif book.get("volumes"):
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
        urls.append(page_url_for(path))
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


# Plain markdown pages. The About page has its own builder (build_about_page).
PAGE_MAP = {
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
    build_about_page()

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
    build_press_page()
    build_404()
    build_sitemap()
    write_metadata_md()

    print("\nBuild complete!")


if __name__ == "__main__":
    build()

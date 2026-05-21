#!/usr/bin/env python3
"""
Export WordPress WXR XML to clean markdown files + image list.

Usage:
    python wp_export.py orbitalring.WordPress.2026-04-11.xml

Creates:
    site_export/
        pages/       - published pages as markdown
        posts/       - published posts as markdown
        drafts/      - draft posts as markdown
        images.txt   - list of image URLs to download
"""

import sys
import os
import re
import html
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

NS = {
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'wp': 'http://wordpress.org/export/1.2/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
}

OUTPUT_DIR = "site_export"


def get_text(item, tag, default=""):
    """Get text content of a child element, supporting namespaced tags."""
    el = item.find(tag, NS)
    return el.text if el is not None and el.text else default


def strip_divi_shortcodes(text):
    """Remove Divi Builder shortcodes like [et_pb_section ...][/et_pb_section].

    These are WordPress shortcodes used by the Divi theme's page builder.
    They wrap the actual content in layout markup we don't need.
    """
    # Convert Divi image shortcodes to markdown images BEFORE stripping
    def divi_image_to_md(m):
        attrs = m.group(1)
        src = re.search(r'src="([^"]+)"', attrs)
        alt = re.search(r'alt="([^"]*)"', attrs)
        if src:
            alt_text = alt.group(1) if alt else ''
            return f'\n\n![{alt_text}]({src.group(1)})\n\n'
        return ''
    text = re.sub(r'\[et_pb_image\s+([^\]]*)\]', divi_image_to_md, text)

    # Remove remaining opening shortcodes: [et_pb_xxx attr="val" ...]
    text = re.sub(r'\[et_pb_\w+[^\]]*\]', '', text)
    # Remove closing shortcodes: [/et_pb_xxx]
    text = re.sub(r'\[/et_pb_\w+\]', '', text)
    # Remove other common shortcodes
    text = re.sub(r'\[/?(?:vc_|fusion_|gallery|caption|embed)\w*[^\]]*\]', '', text)
    return text


def html_to_markdown(content):
    """Convert simple HTML to markdown.

    Handles the common tags found in WordPress posts.  Not a full HTML
    parser -- just enough to get clean readable markdown.
    """
    if not content:
        return ""

    text = content

    # Strip Divi shortcodes first
    text = strip_divi_shortcodes(text)

    # Normalize line endings
    text = text.replace('\r\n', '\n')

    # --- Block-level elements ---

    # Headings
    for level in range(6, 0, -1):
        tag = f'h{level}'
        prefix = '#' * level
        text = re.sub(
            rf'<{tag}[^>]*>(.*?)</{tag}>',
            lambda m: f'\n\n{prefix} {m.group(1).strip()}\n\n',
            text, flags=re.DOTALL | re.IGNORECASE
        )

    # Paragraphs
    text = re.sub(r'<p[^>]*>(.*?)</p>', lambda m: f'\n\n{m.group(1).strip()}\n\n',
                  text, flags=re.DOTALL | re.IGNORECASE)

    # Line breaks
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)

    # Blockquotes
    text = re.sub(
        r'<blockquote[^>]*>(.*?)</blockquote>',
        lambda m: '\n\n' + '\n'.join(
            '> ' + line for line in m.group(1).strip().split('\n')
        ) + '\n\n',
        text, flags=re.DOTALL | re.IGNORECASE
    )

    # Lists
    text = re.sub(r'<ul[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</ul>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<ol[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</ol>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<li[^>]*>(.*?)</li>',
                  lambda m: f'- {m.group(1).strip()}\n',
                  text, flags=re.DOTALL | re.IGNORECASE)

    # --- Inline elements ---

    # Images -> markdown
    text = re.sub(
        r'<img[^>]*src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']*)["\'][^>]*/?>',
        lambda m: f'![{m.group(2)}]({m.group(1)})',
        text, flags=re.IGNORECASE
    )
    text = re.sub(
        r'<img[^>]*src=["\']([^"\']+)["\'][^>]*/?>',
        lambda m: f'![]({m.group(1)})',
        text, flags=re.IGNORECASE
    )

    # Links
    text = re.sub(
        r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        lambda m: f'[{m.group(2).strip()}]({m.group(1)})',
        text, flags=re.DOTALL | re.IGNORECASE
    )

    # Bold / italic
    text = re.sub(r'<(?:strong|b)[^>]*>(.*?)</(?:strong|b)>',
                  r'**\1**', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<(?:em|i)[^>]*>(.*?)</(?:em|i)>',
                  r'*\1*', text, flags=re.DOTALL | re.IGNORECASE)

    # Code
    text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`',
                  text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<pre[^>]*>(.*?)</pre>',
                  lambda m: f'\n\n```\n{m.group(1).strip()}\n```\n\n',
                  text, flags=re.DOTALL | re.IGNORECASE)

    # Horizontal rules
    text = re.sub(r'<hr[^>]*/?>',  '\n\n---\n\n', text, flags=re.IGNORECASE)

    # --- Cleanup ---

    # Strip remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities
    text = html.unescape(text)

    # Collapse excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Strip leading/trailing whitespace per line, but preserve blank lines
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)

    # Final trim
    text = text.strip()

    return text


def extract_image_urls(content):
    """Find all image URLs in HTML content."""
    if not content:
        return []
    urls = re.findall(r'<img[^>]*src=["\']([^"\']+)["\']', content, re.IGNORECASE)
    return urls


def safe_filename(name):
    """Convert a string to a safe filename."""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = name.strip('. ')
    return name[:80] if name else 'untitled'


def process_export(xml_path):
    """Parse WXR XML and write markdown files."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Create output directories
    for subdir in ['pages', 'posts', 'drafts']:
        os.makedirs(os.path.join(OUTPUT_DIR, subdir), exist_ok=True)

    all_image_urls = set()
    items = root.findall('.//item')

    # Collect attachment URLs (media library)
    for item in items:
        post_type = get_text(item, 'wp:post_type')
        if post_type == 'attachment':
            url = get_text(item, 'wp:attachment_url')
            if url:
                all_image_urls.add(url)

    pages_written = 0
    posts_written = 0
    drafts_written = 0

    for item in items:
        post_type = get_text(item, 'wp:post_type')
        status = get_text(item, 'wp:status')

        if post_type not in ('post', 'page'):
            continue

        title = get_text(item, 'title', 'Untitled')
        slug = get_text(item, 'wp:post_name', safe_filename(title))
        date = get_text(item, 'wp:post_date')[:10]
        author = get_text(item, 'dc:creator')
        raw_content = get_text(item, 'content:encoded')
        excerpt = get_text(item, 'excerpt:encoded')

        # Get categories and tags
        categories = []
        tags = []
        for cat in item.findall('category'):
            domain = cat.get('domain', '')
            if domain == 'category':
                categories.append(cat.text or '')
            elif domain == 'post_tag':
                tags.append(cat.text or '')

        # Extract image URLs from content
        content_images = extract_image_urls(raw_content)
        all_image_urls.update(content_images)

        # Convert content to markdown
        md_content = html_to_markdown(raw_content)
        md_excerpt = html_to_markdown(excerpt)

        # Build frontmatter
        frontmatter = f"""---
title: "{html.unescape(title)}"
slug: "{slug}"
date: {date}
author: "{author}"
type: {post_type}
status: {status}"""

        if categories:
            frontmatter += f'\ncategories: [{", ".join(categories)}]'
        if tags:
            frontmatter += f'\ntags: [{", ".join(tags)}]'
        if md_excerpt:
            # Escape for YAML
            exc = md_excerpt.replace('"', '\\"').replace('\n', ' ')
            frontmatter += f'\nexcerpt: "{exc[:200]}"'

        frontmatter += "\n---\n\n"

        # Determine output path
        if post_type == 'page':
            filename = f"{slug}.md"
            subdir = 'pages'
            pages_written += 1
        elif status == 'draft':
            filename = f"{date}-{slug}.md"
            subdir = 'drafts'
            drafts_written += 1
        else:
            filename = f"{date}-{slug}.md"
            subdir = 'posts'
            posts_written += 1

        filepath = os.path.join(OUTPUT_DIR, subdir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
            f.write(md_content)
            f.write('\n')

        print(f"  {post_type:>5} [{status:>7}]  {filepath}")

    # Write image URL list
    image_urls = sorted(all_image_urls)
    img_path = os.path.join(OUTPUT_DIR, "images.txt")
    with open(img_path, 'w', encoding='utf-8') as f:
        for url in image_urls:
            f.write(url + '\n')

    print(f"\n  Summary:")
    print(f"    Pages:       {pages_written}")
    print(f"    Posts:       {posts_written}")
    print(f"    Drafts:      {drafts_written}")
    print(f"    Image URLs:  {len(image_urls)}")
    print(f"    Output:      {OUTPUT_DIR}/")
    print(f"    Image list:  {img_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <wordpress-export.xml>")
        sys.exit(1)
    process_export(sys.argv[1])
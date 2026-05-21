# WordPress migration artifacts

This folder holds the source data and tooling from the original WordPress → static-site migration. It's history, not active code.

- `orbitalring.WordPress.2026-04-11.xml` — the full WordPress export dump from 2026-04-11. This is the canonical record of what the WordPress site contained at the moment it was retired. Keep it as the audit source if you ever need to confirm "what did the old site say about X?" or re-extract content.
- `wp_export.py` — the parser that consumed the XML to generate the initial static site (currently still at the project root at [../wp_export.py](../wp_export.py); kept there because it's where it was originally run from).

Neither file is needed to build or serve the live site. They exist only to preserve migration provenance.

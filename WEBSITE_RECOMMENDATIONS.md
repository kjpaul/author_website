# Website Recommendations for Claude Code

**Date:** April 18, 2026
**Context:** Review of Phase 2 build. These recommendations cover visual design changes, layout fixes, content fixes, and Phase 3 reference system implementation.

---

## 1. Switch to Light Theme

The current dark theme (GitHub-style `#0d1117` background) should be replaced with a light theme. This is an author website for technical books, not a developer tool. Light backgrounds are easier to read for long-form content and feel more like a bookshelf.

**Replace the `:root` CSS variables with:**

```css
:root {
  --bg: #ffffff;
  --bg-card: #f8f9fb;
  --bg-hover: #eef1f6;
  --text: #1a1a2e;
  --text-muted: #4a4a6a;
  --accent: #2266aa;
  --accent-hover: #1a5090;
  --border: #d8dce6;
  --max-width: 860px;
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  --font-mono: "SF Mono", "Fira Code", monospace;
}
```

**Other CSS changes needed for light theme:**

- `nav` background: change `rgba(13, 17, 23, 0.95)` to `rgba(255, 255, 255, 0.95)` (or a very light off-white)
- `.nav-dropdown-menu` background: use `#ffffff` with a subtle shadow
- `.nav-dropdown-menu` box-shadow: change `rgba(0, 0, 0, 0.5)` to `rgba(0, 0, 0, 0.12)` (much lighter shadow for light theme)
- `.home-hero h1` gradient: change from `var(--text) to var(--accent)` to something visible on white. Suggestion: `linear-gradient(135deg, #1a1a2e 0%, #2266aa 100%)`
- `.cover-placeholder` background: change from dark gradient to light gradient, e.g., `linear-gradient(135deg, #eef1f6 0%, #d8dce6 100%)`, and use a darker text color for the AST ID
- Badge colors: `.badge-confirmed` and `.badge-published` green (`#1a7f37`) works on both themes. `.badge-in-progress` border/text should use `--accent` (already does). Check that all badge text is readable on the lighter card backgrounds.
- Form inputs: change `background: var(--bg-card)` which is now light, and make sure `border` is visible. Inputs on a light card on a white page need a slightly darker border.
- `blockquote` left border and background should still be visible. The accent border works; the card background (`#f8f9fb`) is subtle but fine.
- `code` background: `var(--bg-card)` becomes very light. May need a slightly darker background like `#eef1f6` for inline code to remain visible.

**Track accent colors (keep, but adjust fiction accent):**

```css
.track-technical { --track-accent: #2266aa; --track-accent-soft: rgba(34, 102, 170, 0.08); }
.track-fiction { --track-accent: #884422; --track-accent-soft: rgba(136, 68, 34, 0.08); }
```

The fiction accent changes from `#d9846e` (salmon/terracotta) to `#884422` (warm brown). This is darker and more distinct from the technical blue, and will read better on a white background.

---

## 2. Fix Volume Cards Below the Fold

**Problem:** On the AST-T1 book hub page (`/series/technical/orbital-rings/`), the volume cards are buried below the book description, which is several paragraphs long. The most important thing on this page is the three volumes, and a visitor has to scroll past a cover placeholder, book metadata, and 4 paragraphs of description before seeing them.

**Fix:** Restructure the `book-detail.html` template so the volume cards appear immediately after the book header, before the description. The layout should be:

1. Breadcrumb
2. Book header (cover + title + series line + status badge)
3. **Volume cards (immediately visible)**
4. Book description (below the volumes)
5. Links section

In the template, move the `{% if book.volumes %}` block to appear before `<div class="book-description">`.

Additionally, the cover placeholder takes up a lot of vertical space on this page. For a multi-volume book that does not yet have a cover image, consider either making the placeholder smaller or removing it entirely and putting the AST-T1 identifier next to the title instead.

---

## 3. Fix Duplicate Description on Placeholder Pages

**Problem:** On placeholder book pages (e.g., MIA Drive), the description from `series.json` appears twice: once as `book.description` in the tagline area of the header, and again as the first paragraph of the fallback content ("This book is in the early stages of planning...") followed by the same description text.

**Fix:** In `book-detail.html`, when there is no content markdown file (i.e., `book_content` is empty), the template should show the tagline from `book.description` in the header and a single "Coming soon" message below, without repeating the description. If `book_content` exists (from a markdown file), show that instead, and the tagline still appears in the header.

---

## 4. Fix Copyright Year

**Fix:** In `templates/includes/footer.html` (or wherever the footer is defined), change:

```html
<p>&copy; 2025 Paul de Jong. All rights reserved.</p>
```

to:

```html
<p>&copy; 2026 Paul de Jong. All rights reserved.</p>
```

---

## 5. Build the References System (Phase 3)

Volume III has 25 references in two reference sections (after the catastrophic failure chapters and at the end of the book). These should be extracted into a JSON file and rendered on the references page.

### 5.1 Extract Vol III References to JSON

The references are in `/Vol_III/250_km/Vol_III_Design_Review_v35_claude.md`. There are two `## References` sections:

**First section (line 2392):** 10 references, covering chapters on catastrophic failure and radiation (Chapters 12-13). These are numbered [1] through [10].

**Second section (line 2765):** 15 references, covering the general design review content (Chapters 1-11). These are numbered [1] through [15].

Because Vol III is structured as a single document (not per-chapter files), and the references are currently in two blocks rather than per-chapter, the JSON should organize them into two groups. For now, label them by the chapter ranges they cover:

```json
{
  "series_id": "AST-T1",
  "book_title": "Engineering Orbital Rings, Mass Drivers and Space Elevators",
  "volume": 3,
  "volume_title": "Space Mass Transit Systems, Complete Design Review",
  "last_updated": "2026-04-18",
  "chapters": [
    {
      "number": "12-13",
      "title": "Catastrophic Failure Analysis and Design Altitude",
      "references": [
        {
          "num": 1,
          "type": "journal",
          "authors": "Robock, A., Oman, L., and Stenchikov, G.L.",
          "title": "Nuclear winter revisited with a modern climate model and current nuclear arsenals: Still catastrophic consequences",
          "journal": "Journal of Geophysical Research",
          "volume": "112",
          "pages": "D13107",
          "year": 2007,
          "doi": "10.1029/2006JD008235"
        },
        {
          "num": 2,
          "type": "journal",
          "authors": "Toon, O.B., Robock, A., and Turco, R.P.",
          "title": "Environmental consequences of nuclear war",
          "journal": "Physics Today",
          "volume": "61",
          "issue": "12",
          "pages": "37-42",
          "year": 2008,
          "doi": "10.1063/1.3047679"
        },
        {
          "num": 3,
          "type": "journal",
          "authors": "Housen, K.R. and Holsapple, K.A.",
          "title": "Ejecta from impact craters",
          "journal": "Icarus",
          "volume": "211",
          "issue": "1",
          "pages": "856-875",
          "year": 2011
        },
        {
          "num": 4,
          "type": "book",
          "authors": "Melosh, H.J.",
          "title": "Impact Cratering: A Geologic Process",
          "publisher": "Oxford University Press",
          "year": 1989,
          "note": "Chapter 7: Ejecta scaling laws."
        },
        {
          "num": 5,
          "type": "report",
          "authors": "Sawyer, D.M. and Vette, J.I.",
          "title": "AP-8 Trapped Proton Environment for Solar Maximum and Solar Minimum",
          "publisher": "NASA/WDC-A-R&S",
          "report_number": "Report 76-06",
          "year": 1976
        },
        {
          "num": 6,
          "type": "journal",
          "authors": "Li, W. and Hudson, M.K.",
          "title": "Earth's Van Allen Radiation Belts: From Discovery to the Van Allen Probes Era",
          "journal": "Journal of Geophysical Research: Space Physics",
          "volume": "124",
          "pages": "8319-8351",
          "year": 2019
        },
        {
          "num": 7,
          "type": "journal",
          "authors": "Fischer, D.X. et al.",
          "title": "The effect of fast neutron irradiation on the superconducting properties of REBCO coated conductors with and without artificial pinning centers",
          "journal": "Superconductor Science and Technology",
          "volume": "31",
          "pages": "044006",
          "year": 2018
        },
        {
          "num": 8,
          "type": "report",
          "authors": "Seltzer, S.M.",
          "title": "Updated Calculations for Routine Space-Shielding Radiation Dose Estimates: SHIELDOSE-2",
          "publisher": "NIST",
          "report_number": "NISTIR 5477",
          "year": 1994
        },
        {
          "num": 9,
          "type": "journal",
          "authors": "Summers, G.P. et al.",
          "title": "Damage Correlations in Semiconductors Exposed to Gamma, Electron and Proton Radiations",
          "journal": "IEEE Transactions on Nuclear Science",
          "volume": "40",
          "issue": "6",
          "pages": "1372-1379",
          "year": 1993
        },
        {
          "num": 10,
          "type": "journal",
          "authors": "Messenger, S.R. et al.",
          "title": "Nonionizing Energy Loss (NIEL) for Heavy Ions",
          "journal": "IEEE Transactions on Nuclear Science",
          "volume": "46",
          "issue": "6",
          "pages": "1595-1602",
          "year": 1999
        }
      ]
    },
    {
      "number": "1-11",
      "title": "Design Review: Structure, Subsystems, and Performance",
      "references": [
        {
          "num": 1,
          "type": "journal",
          "authors": "Zhang, Y., et al.",
          "title": "Carbon nanotube fibers with dynamic strength up to 14 GPa",
          "journal": "Science",
          "year": 2024,
          "doi": "10.1126/science.adj1082",
          "note": "CNT yarn tensile strength, laboratory state of the art as of 2024."
        },
        {
          "num": 2,
          "type": "journal",
          "authors": "Bai, Y., et al.",
          "title": "Carbon nanotube bundles with tensile strength over 80 GPa",
          "journal": "Nature Nanotechnology",
          "volume": "13",
          "pages": "589-595",
          "year": 2018,
          "doi": "10.1038/s41565-018-0141-z"
        },
        {
          "num": 3,
          "type": "journal",
          "authors": "Xu, L., et al.",
          "title": "Ultrahigh strength, modulus, and conductivity of graphitic fibers by macromolecular coalescence",
          "journal": "Science Advances",
          "volume": "8",
          "issue": "17",
          "year": 2022,
          "doi": "10.1126/sciadv.abn0939",
          "note": "Bulk CNT/graphitic fiber conductivity of 2.2 MS/m."
        },
        {
          "num": 4,
          "type": "journal",
          "authors": "De Luna, R., et al.",
          "title": "Environmentally stable macroscopic graphene films with specific electrical conductivity exceeding metals",
          "journal": "Carbon",
          "volume": "158",
          "pages": "311-319",
          "year": 2020,
          "doi": "10.1016/j.carbon.2019.10.073"
        },
        {
          "num": 5,
          "type": "report",
          "authors": "NASA",
          "title": "Low Earth Orbit Spacecraft Charging Design Standard",
          "report_number": "NASA-STD-4005A",
          "year": 2017
        },
        {
          "num": 6,
          "type": "book",
          "authors": "Laithwaite, E.R.",
          "title": "A History of Linear Electric Motors",
          "publisher": "Macmillan",
          "year": 1987,
          "note": "Goodness factor model for linear induction motor performance."
        },
        {
          "num": 7,
          "type": "journal",
          "authors": "Kim, K.S., et al.",
          "title": "Large-scale pattern growth of graphene films for stretchable transparent electrodes",
          "journal": "Nature",
          "volume": "457",
          "pages": "706-710",
          "year": 2009,
          "doi": "10.1038/nature07719"
        },
        {
          "num": 8,
          "type": "journal",
          "authors": "Chopra, N.G. and Zettl, A.",
          "title": "Measurement of the elastic modulus of a multi-wall boron nitride nanotube",
          "journal": "Solid State Communications",
          "volume": "105",
          "issue": "5",
          "pages": "297-300",
          "year": 1998,
          "doi": "10.1016/S0038-1098(97)10125-9"
        },
        {
          "num": 9,
          "type": "report",
          "authors": "Smith, F.W., et al.",
          "title": "Boron Nitride Nanotube: Synthesis and Applications",
          "report_number": "NASA/TM-2014-218062",
          "year": 2014
        },
        {
          "num": 10,
          "type": "journal",
          "authors": "Sanchez-Valencia, J.R., et al.",
          "title": "Theory of the electrodynamic tether",
          "journal": "Advances in Space Research",
          "volume": "7",
          "issue": "1",
          "pages": "21-33",
          "year": 1987,
          "doi": "10.1016/0273-1177(87)90364-X"
        },
        {
          "num": 11,
          "type": "report",
          "authors": "SpaceX",
          "title": "Starship Users Guide, Revision 1.0",
          "publisher": "Space Exploration Technologies Corp.",
          "year": 2020
        },
        {
          "num": 12,
          "type": "website",
          "authors": "de Jong, Paul G.",
          "title": "Orbital Ring Simulation Source Code and Interactive Database",
          "url": "https://www.orbitalring.space/coding-hub/",
          "note": "LIM deployment simulator, mass driver simulation, J2 perturbation analysis."
        },
        {
          "num": 13,
          "type": "journal",
          "authors": "Grün, E., Zook, H.A., Fechtig, H., and Giese, R.H.",
          "title": "Collisional balance of the meteoritic complex",
          "journal": "Icarus",
          "volume": "62",
          "issue": "2",
          "pages": "244-272",
          "year": 1985,
          "doi": "10.1016/0019-1035(85)90121-6"
        },
        {
          "num": 14,
          "type": "journal",
          "authors": "Robock, A., Oman, L., and Stenchikov, G.L.",
          "title": "Nuclear winter revisited with a modern climate model and current nuclear arsenals: Still catastrophic consequences",
          "journal": "Journal of Geophysical Research: Atmospheres",
          "volume": "112",
          "pages": "D13107",
          "year": 2007,
          "doi": "10.1029/2006JD008235"
        },
        {
          "num": 15,
          "type": "journal",
          "authors": "Toon, O.B., Robock, A., and Turco, R.P.",
          "title": "Environmental consequences of nuclear war",
          "journal": "Physics Today",
          "volume": "61",
          "issue": "12",
          "pages": "37-42",
          "year": 2008,
          "doi": "10.1063/1.3047679"
        }
      ]
    }
  ]
}
```

Save this file to `data/references/ast-t1-vol-3.json`.

### 5.2 Build the References Page

Create a references page template (`templates/pages/references.html`) and the JavaScript renderer (`static/js/references.js`).

**The page should:**
1. Load the JSON file based on the URL (e.g., `/series/technical/orbital-rings/vol-3/references/` loads `ast-t1-vol-3.json`)
2. Display chapter/section navigation as clickable buttons at the top
3. Render each reference section with its references formatted in academic citation style
4. Support anchor links (`#chapters-12-13` or similar) so the printed book can point readers to a specific section
5. DOIs should be clickable links to `https://doi.org/[DOI]`
6. URLs should be clickable
7. Style should match the rest of the site (use the new light theme variables)

**Reference rendering format:**

```
[1] Robock, A., Oman, L., and Stenchikov, G.L. "Nuclear winter revisited 
    with a modern climate model and current nuclear arsenals: Still 
    catastrophic consequences." Journal of Geophysical Research, Vol. 112, 
    D13107, 2007. DOI: 10.1029/2006JD008235
```

Journal names in italics, article titles in quotes, DOI as a link.

### 5.3 Generate Reference Pages in build.py

Add a `build_reference_pages()` function to `build.py` that:
1. Scans `data/references/` for JSON files
2. For each file, generates the reference page at the correct URL path
3. The template receives the JSON data and renders it server-side (no need for client-side JS if Jinja2 can handle it at build time)

Actually, since the JSON is available at build time, it is simpler and better for SEO to render references as static HTML via Jinja2 rather than loading JSON with JavaScript. The Jinja2 template can loop over the chapters and references directly. The JSON file still serves as the data source, but `build.py` reads it and passes it to the template.

### 5.4 Wire Up Existing Links

The volume detail pages already link to references pages (e.g., Vol I links to `/series/technical/orbital-rings/vol-1/references/`). Vol III references should work once the JSON and template are in place. Vol I and Vol II reference JSON files can be empty placeholders for now:

```json
{
  "series_id": "AST-T1",
  "book_title": "Engineering Orbital Rings, Mass Drivers and Space Elevators",
  "volume": 1,
  "volume_title": "The Economic Case for Space Mass Transit Systems",
  "last_updated": "2026-04-18",
  "chapters": []
}
```

With a message on the page: "References for this volume will be published here when the volume is in print."

---

## 6. Additional Fixes

### 6.1 Legacy Book Images

The legacy book page references images at `/images/orbital-ring-engineering-cover-final1000.jpg` and `/images/author-icon-12.png`. Verify these exist in `static/images/` (or `public/images/`). If they were carried over from the old WordPress site, they may be in `_baseline_public/` or `site_export/`. Copy them to `static/images/` if missing.

### 6.2 URL in Legacy Book

The legacy book page text says "keep exploring this website" and links to `https://www.orbitalring.space/`. The `fix_old_urls()` function in `build.py` should catch most of these, but verify the legacy page renders with correct internal URLs, not old orbitalring.space links.

### 6.3 Update the code page URL

The homepage GitHub link goes to `https://github.com/kjpaul/orbitalring`. Verify this is the correct current repo URL.

---

## 7. Implementation Order

1. Switch CSS to light theme (Section 1)
2. Fix volume cards position on book hub page (Section 2)
3. Fix duplicate description on placeholders (Section 3)
4. Fix copyright year (Section 4)
5. Create Vol III reference JSON file (Section 5.1) — the JSON is provided above, just save it
6. Build reference page template and integrate into build.py (Section 5.2, 5.3)
7. Create placeholder JSON for Vol I and Vol II (Section 5.4)
8. Verify legacy book images and URLs (Section 6)
9. Rebuild and test

After these changes, the site should be ready for a visual review pass on typography, spacing, and the homepage hero before deploying.

---

## 8. Phase 4 Updates (April 18, 2026 — continued)

### 8.1 Vol I References Now Complete

The file `data/references/ast-t1-vol-1.json` now contains all 358 references across all 21 chapters of Volume I. The schema matches the Vol III file at the top level (`series_id`, `book_title`, `volume`, `volume_title`, `last_updated`, `chapters`), but references use a simpler text format:

```json
{
  "num": 1,
  "text": "Full citation text including See also notes..."
}
```

This is different from Vol III which uses structured fields (`type`, `authors`, `title`, `journal`, `doi`, etc.).

### 8.2 Updated Reference Template

The template `templates/includes/reference.html` has been updated to handle BOTH formats:
- If a reference has a `text` field, it renders the text directly in a `<span class="ref-text">`.
- If it has structured fields (`authors`, `title`, etc.), it uses the existing structured rendering.
- The `num` field is resolved via `r.num or r.number` for backward compatibility.

**No changes needed to the template — it's already updated.**

### 8.3 build.py Is Truncated

**IMPORTANT:** The `build.py` file is truncated at line 396. The `build_legacy_book()` function is cut off mid-string, and the `main()` function with its call sequence is missing entirely. This needs to be restored. The function `build_reference_pages()` (lines 339-388) is intact and works correctly with both Vol I and Vol III JSON formats.

The missing code needs to be reconstructed. At minimum, `build_legacy_book()` needs to be completed and a `main()` function needs to call all the build functions in order.

### 8.4 Markdown Formatting in Vol I Reference Text

Vol I references contain markdown-style formatting (e.g., `*Science*` for italics, `$10^{24}$` for math). For the website, these should ideally be:
- `*text*` → `<em>text</em>` 
- `$...$` → rendered as HTML (or left as-is for now)
- URLs in text → auto-linked with `<a>` tags

This could be done as a Jinja2 filter or a post-processing step in the build script. Low priority — the references are readable as-is.

### 8.5 Vol III References Status

The Vol III JSON (`data/references/ast-t1-vol-3.json`) has 25 references in two grouped sections:
- Chapters 12-13: 10 references (catastrophic failure and radiation)
- Chapters 1-11: 15 references (design review subsystems)

This matches the manuscript (v35), which only has two `## References` sections. Chapters 14-16 do not have separate reference sections in the current manuscript. The Vol III JSON is complete for what exists.

### 8.6 Updated Implementation Order

1. ~~Switch CSS to light theme~~ ✓ Done
2. ~~Fix volume cards position~~ ✓ Done
3. ~~Fix duplicate description~~ ✓ Done
4. ~~Fix copyright year~~ ✓ Done
5. ~~Create Vol III reference JSON~~ ✓ Done
6. ~~Build reference page template~~ ✓ Done
7. **Fix build.py truncation** — restore `build_legacy_book()` and `main()`
8. **Rebuild site** — the Vol I references page should now appear at `/series/technical/orbital-rings/vol-1/references/`
9. **Optional:** Add markdown-to-HTML processing for Vol I reference text (italics, URLs)
10. Verify all reference pages render correctly
11. Deploy to Firebase

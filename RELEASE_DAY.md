# Release day for Volume I: 19 January 2027

Three data changes, no code. Rebuild with `python build.py`, deploy with `firebase deploy --only hosting`.

The release date is 19 January 2027, filed at Bowker on 2026-11-10 as the publication and on-sale date for all three ISBNs. `release_date` on Volume I in `series.json` holds `2027-01-19` and renders as "19 January 2027" on the hero, the volume cards, the buy button and the Publication details block. If the date moves, change it there and at Bowker on the same day.

1. **Status.** In `series.json`, the first volume of `technical[0]` (Volume I): change `"status": "pre_order"` to `"status": "published"`. The badge on every card and page follows, and the Volume I page says "Released 19 January 2027".

2. **Buy links.** In the same volume's `purchase` block, fill in the links as they go live:
   - `kindle`: the Amazon Kindle listing (the ASIN appears when the Kindle pre-order or the listing goes live). This turns the "Coming December 2026" button into the Amazon link.
   - `paperback` and `hardcover`: the Amazon print listings. Each format gets its own button with the price from `prices`.
   - `bookstore`: the IngramSpark listing for bookstores and libraries. The line under the buttons becomes a link.
   Until `kindle`, `paperback` or `hardcover` is set, the button reads "Coming 19 January 2027" and the notify-me form is the call to action.

3. **Cover.** Replace `static/images/covers/orbital-ring-vol-1-cover.png` with the professional cover under the same name (800 x 1200, PNG). Nothing else references the file by another name.

Also on release day, when the listings exist: the Amazon ASIN in the same volume's `review.amazon_asin` puts Volume I on the review page (`/review/`), and the other store links in that block add their buttons.

The catalog's `_notes` carry the same instructions.

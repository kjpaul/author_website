// Errata tracker — public page
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.7.1/firebase-app.js";
import { getFirestore, collection, query, where, orderBy, getDocs }
  from "https://www.gstatic.com/firebasejs/11.7.1/firebase-firestore.js";

const app  = initializeApp(firebaseConfig);   // firebaseConfig loaded from firebase-config.js
const db   = getFirestore(app);
const coll = collection(db, "errata");

// --- Books registry (injected by build.py from series.json) ---
const BOOKS = window.ERRATA_BOOKS || {};

// --- Alias table (injected by build.py from series.json `errata_aliases`) ---
// Maps the slug in a /errata/?book= link to the key stored on the Firestore
// records. A link that already carries a key still works.
const ALIASES = window.ERRATA_ALIASES || {};
function resolveBookKey(param) {
  if (!param) return null;
  if (Object.prototype.hasOwnProperty.call(ALIASES, param)) return ALIASES[param];
  return BOOKS[param] ? param : null;
}

// --- DOM refs ---
const listEl     = document.getElementById("errata-list");
const searchEl   = document.getElementById("errata-search");
const bookFilter = document.getElementById("book-filter");
const formEl     = document.getElementById("errata-form");
const statusEl   = document.getElementById("form-status");
const countEl    = document.getElementById("errata-count");

// --- Load the confirmed errata once; search, book filter and paging work on that list ---
const PAGE_SIZE = 10;
const recentWrap = document.getElementById("recent-wrap");
const recentBtn  = document.getElementById("recent-btn");
const pagerEl    = document.getElementById("errata-pager");
const prevBtn    = document.getElementById("errata-prev");
const nextBtn    = document.getElementById("errata-next");
const pageInfo   = document.getElementById("errata-page-info");

let allItems = null;   // every confirmed or fixed erratum, newest first; null until loaded
let shown    = [];     // the ones that match the search box and the book filter
let page     = 0;
let listOpen = false;  // the list opens on "Show recent errata", a search, or a choice of book

async function fetchErrata() {
  if (allItems) return allItems;
  const q = query(coll,
    where("status", "in", ["confirmed", "fixed"]),
    orderBy("created_at", "desc"));
  const snap = await getDocs(q);
  const items = [];
  snap.forEach(doc => items.push(doc.data()));
  allItems = items;
  return items;
}

async function loadErrata() {
  try {
    if (!allItems) countEl.textContent = "Loading…";
    const items = await fetchErrata();
    const search = searchEl.value.trim().toLowerCase();
    const bookKey = bookFilter.value;
    shown = items.filter(d => {
      if (bookKey !== "all" && d.book !== bookKey) return false;
      if (search && ![d.page, d.quote, d.description, d.admin_note || ""]
          .some(f => (f || "").toLowerCase().includes(search))) {
        return false;
      }
      return true;
    });
    page = 0;
    render();
  } catch (err) {
    console.error(err);
    countEl.textContent = "";
    listEl.innerHTML = '<p class="error">Could not load errata. Please try again later.</p>';
  }
}

function itemHtml(d) {
  const book = BOOKS[d.book]?.title || d.book;
  const statusBadge = d.status === "fixed"
    ? '<span class="badge badge-fixed">Fixed</span>'
    : '<span class="badge badge-confirmed">Confirmed</span>';
  const adminNote = d.admin_note
    ? `<div class="admin-note"><strong>Author note:</strong> ${escHtml(d.admin_note)}</div>`
    : "";
  return `<div class="errata-item">
        <div class="errata-header">
          <span class="errata-page">${escHtml(fmtWhere(d.page))}</span>
          ${statusBadge}
        </div>
        <div class="errata-quote">"${escHtml(d.quote)}"</div>
        <div class="errata-desc">${escHtml(d.description)}</div>
        ${adminNote}
        <div class="errata-meta">${escHtml(book)} &middot; ${fmtDate(d.created_at)}</div>
      </div>`;
}

function render() {
  if (!allItems) return;
  if (allItems.length === 0) {
    countEl.textContent = "No errata have been confirmed yet.";
    listEl.innerHTML = "";
    recentWrap.hidden = true;
    pagerEl.hidden = true;
    return;
  }
  countEl.textContent = shown.length === 1 ? "1 erratum found" : `${shown.length} errata found`;
  if (!listOpen) {
    listEl.innerHTML = "";
    recentWrap.hidden = false;
    pagerEl.hidden = true;
    return;
  }
  recentWrap.hidden = true;
  if (shown.length === 0) {
    listEl.innerHTML = '<p class="empty">No errata match.</p>';
    pagerEl.hidden = true;
    return;
  }
  const pages = Math.ceil(shown.length / PAGE_SIZE);
  page = Math.min(Math.max(page, 0), pages - 1);
  const start = page * PAGE_SIZE;
  const slice = shown.slice(start, start + PAGE_SIZE);
  listEl.innerHTML = slice.map(itemHtml).join("\n");
  pagerEl.hidden = pages <= 1;
  prevBtn.disabled = page === 0;
  nextBtn.disabled = page >= pages - 1;
  pageInfo.textContent = `${start + 1} to ${start + slice.length} of ${shown.length}`;
}

// --- Recent errata, ten at a time ---
recentBtn.addEventListener("click", () => { listOpen = true; page = 0; render(); });
function turnPage(step) {
  page += step;
  render();
  countEl.scrollIntoView({ behavior: "smooth", block: "center" });
}
prevBtn.addEventListener("click", () => turnPage(-1));
nextBtn.addEventListener("click", () => turnPage(1));

// --- Submit form ---
formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = formEl.querySelector("button[type=submit]");
  btn.disabled = true;
  btn.textContent = "Submitting…";
  statusEl.textContent = "";
  let sent = false;

  const payload = {
    book:        formEl.book.value,
    page:        formEl.page.value.trim(),
    quote:       formEl.quote.value.trim(),
    description: formEl.description.value.trim(),
    name:        (document.getElementById("f-name")?.value || "").trim(),
    email:       formEl.email.value.trim(),
    website:     formEl.website.value,                         // honeypot
    turnstileToken: formEl["cf-turnstile-response"]?.value || "",
  };

  try {
    const resp = await fetch("/api/submit-errata", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const json = await resp.json().catch(() => ({}));

    if (resp.ok && json.ok) {
      statusEl.innerHTML = '<span class="success">Thank you! Your submission will be reviewed.</span>';
      sent = true;
      formEl.reset();
      applyBookParam();  // restore any deep-linked book selection after reset
    } else {
      const msg = (json.error === "captcha_failed" || json.error === "captcha_missing")
        ? "Please complete the verification box and try again."
        : "Submission failed. Please try again.";
      statusEl.innerHTML = `<span class="error">${msg}</span>`;
    }
  } catch (err) {
    console.error(err);
    statusEl.innerHTML = '<span class="error">Submission failed. Please try again.</span>';
  } finally {
    btn.disabled = false;
    // After a report has gone through, the button must not look as if it still needs pressing.
    btn.textContent = sent ? "Report another error" : "Submit";
    if (window.turnstile) window.turnstile.reset();
  }
});

// --- Search ---
let searchTimeout;
searchEl.addEventListener("input", () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => { listOpen = true; loadErrata(); }, 300);
});

// --- Book filter ---
bookFilter.addEventListener("change", () => { listOpen = true; loadErrata(); });

// --- Deep link: /errata/?book=<key> preselects the book in filter + form ---
function applyBookParam() {
  const key = resolveBookKey(new URLSearchParams(location.search).get("book"));
  if (key && BOOKS[key]) {
    if ([...bookFilter.options].some(o => o.value === key)) bookFilter.value = key;
    if (formEl && [...formEl.book.options].some(o => o.value === key)) formEl.book.value = key;
  }
}

// --- Helpers ---
function escHtml(s) {
  const el = document.createElement("span");
  el.textContent = s || "";
  return el.innerHTML;
}

// Where the error is. New reports give a chapter and section; older ones
// gave a page number, shown as "Page 142".
function fmtWhere(v) {
  const s = (v || "").trim();
  if (!s) return "?";
  return /^\d+$/.test(s) ? `Page ${s}` : s;
}

function fmtDate(ts) {
  if (!ts) return "";
  const d = ts.toDate ? ts.toDate() : new Date(ts);
  return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

// --- Init ---
applyBookParam();
if (bookFilter.value !== "all") listOpen = true;   // a link to one book opens its list
loadErrata();

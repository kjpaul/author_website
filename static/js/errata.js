// Errata tracker — public page
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.7.1/firebase-app.js";
import { getFirestore, collection, query, where, orderBy, getDocs, addDoc, Timestamp }
  from "https://www.gstatic.com/firebasejs/11.7.1/firebase-firestore.js";

const app  = initializeApp(firebaseConfig);   // firebaseConfig loaded from firebase-config.js
const db   = getFirestore(app);
const coll = collection(db, "errata");

// --- Books registry ---
const BOOKS = {
  "orbital-ring-engineering": {
    title: "Orbital Ring, Mass Driver, Space Elevator Engineering",
    isbn:  "979-8-9938893-0-2",
  },
};

// --- DOM refs ---
const listEl     = document.getElementById("errata-list");
const searchEl   = document.getElementById("errata-search");
const bookFilter = document.getElementById("book-filter");
const formEl     = document.getElementById("errata-form");
const statusEl   = document.getElementById("form-status");
const countEl    = document.getElementById("errata-count");

// --- Load & render confirmed errata ---
async function loadErrata(searchText = "") {
  listEl.innerHTML = '<p class="loading">Loading...</p>';

  try {
    const q = query(coll,
      where("status", "in", ["confirmed", "fixed"]),
      orderBy("created_at", "desc"));
    const snap = await getDocs(q);

    const items = [];
    snap.forEach(doc => {
      const d = doc.data();
      const search = searchText.toLowerCase();
      if (search && ![d.page, d.quote, d.description, d.admin_note || ""]
          .some(f => (f || "").toLowerCase().includes(search))) {
        return;
      }
      items.push(d);
    });

    countEl.textContent = `${items.length} errata found`;

    if (items.length === 0) {
      listEl.innerHTML = '<p class="empty">No errata found.</p>';
      return;
    }

    listEl.innerHTML = items.map(d => {
      const book = BOOKS[d.book]?.title || d.book;
      const statusBadge = d.status === "fixed"
        ? '<span class="badge badge-fixed">Fixed</span>'
        : '<span class="badge badge-confirmed">Confirmed</span>';
      const adminNote = d.admin_note
        ? `<div class="admin-note"><strong>Author note:</strong> ${escHtml(d.admin_note)}</div>`
        : "";
      return `<div class="errata-item">
        <div class="errata-header">
          <span class="errata-page">Page ${escHtml(d.page || "?")}</span>
          ${statusBadge}
        </div>
        <div class="errata-quote">"${escHtml(d.quote)}"</div>
        <div class="errata-desc">${escHtml(d.description)}</div>
        ${adminNote}
        <div class="errata-meta">${book} &middot; ${fmtDate(d.created_at)}</div>
      </div>`;
    }).join("\n");

  } catch (err) {
    console.error(err);
    listEl.innerHTML = '<p class="error">Could not load errata. Please try again later.</p>';
  }
}

// --- Submit form ---
formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = formEl.querySelector("button[type=submit]");
  btn.disabled = true;
  btn.textContent = "Submitting...";
  statusEl.textContent = "";

  const data = {
    book:        formEl.book.value,
    isbn:        BOOKS[formEl.book.value]?.isbn || "",
    page:        formEl.page.value.trim(),
    quote:       formEl.quote.value.trim(),
    description: formEl.description.value.trim(),
    submitted_by: formEl.email.value.trim() || "anonymous",
    status:      "pending",
    admin_note:  "",
    created_at:  Timestamp.now(),
  };

  try {
    await addDoc(coll, data);
    statusEl.innerHTML = '<span class="success">Thank you! Your submission will be reviewed.</span>';
    formEl.reset();
  } catch (err) {
    console.error(err);
    statusEl.innerHTML = '<span class="error">Submission failed. Please try again.</span>';
  } finally {
    btn.disabled = false;
    btn.textContent = "Submit";
  }
});

// --- Search ---
let searchTimeout;
searchEl.addEventListener("input", () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => loadErrata(searchEl.value), 300);
});

// --- Helpers ---
function escHtml(s) {
  const el = document.createElement("span");
  el.textContent = s || "";
  return el.innerHTML;
}

function fmtDate(ts) {
  if (!ts) return "";
  const d = ts.toDate ? ts.toDate() : new Date(ts);
  return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

// --- Init ---
loadErrata();

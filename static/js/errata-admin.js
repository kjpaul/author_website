// Errata tracker — admin page
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.7.1/firebase-app.js";
import { getFirestore, collection, query, orderBy, getDocs, doc, updateDoc, deleteDoc, Timestamp }
  from "https://www.gstatic.com/firebasejs/11.7.1/firebase-firestore.js";
import { getAuth, signInWithPopup, GoogleAuthProvider, onAuthStateChanged, signOut }
  from "https://www.gstatic.com/firebasejs/11.7.1/firebase-auth.js";

const ADMIN_EMAIL = "paul@orbitalring.space";

const app  = initializeApp(firebaseConfig);
const db   = getFirestore(app);
const auth = getAuth(app);
const coll = collection(db, "errata");

// --- DOM refs ---
const authSection  = document.getElementById("auth-section");
const adminSection = document.getElementById("admin-section");
const loginBtn     = document.getElementById("login-btn");
const logoutBtn    = document.getElementById("logout-btn");
const userInfo     = document.getElementById("user-info");
const listEl       = document.getElementById("admin-list");
const filterEl     = document.getElementById("status-filter");

// --- Auth ---
onAuthStateChanged(auth, (user) => {
  if (user && user.email === ADMIN_EMAIL) {
    authSection.style.display = "none";
    adminSection.style.display = "block";
    userInfo.textContent = `Signed in as ${user.email}`;
    loadAll();
  } else if (user) {
    authSection.innerHTML = `<p class="error">Access denied for ${user.email}. Only the site admin can access this page.</p>`;
    signOut(auth);
  } else {
    authSection.style.display = "block";
    adminSection.style.display = "none";
  }
});

loginBtn.addEventListener("click", () => {
  signInWithPopup(auth, new GoogleAuthProvider());
});

logoutBtn.addEventListener("click", () => {
  signOut(auth);
});

// --- Load all errata ---
async function loadAll(statusFilter = "all") {
  listEl.innerHTML = '<p class="loading">Loading...</p>';

  try {
    const q = query(coll, orderBy("created_at", "desc"));
    const snap = await getDocs(q);

    const items = [];
    snap.forEach(d => {
      const data = d.data();
      data._id = d.id;
      if (statusFilter !== "all" && data.status !== statusFilter) return;
      items.push(data);
    });

    if (items.length === 0) {
      listEl.innerHTML = '<p class="empty">No errata found.</p>';
      return;
    }

    listEl.innerHTML = items.map(d => `
      <div class="errata-item admin-item" data-id="${d._id}">
        <div class="errata-header">
          <span class="errata-page">Page ${escHtml(d.page || "?")}</span>
          <span class="badge badge-${d.status}">${d.status}</span>
          <span class="errata-meta">${fmtDate(d.created_at)} &middot; ${escHtml(d.submitted_by)}</span>
        </div>
        <div class="errata-quote">"${escHtml(d.quote)}"</div>
        <div class="errata-desc">${escHtml(d.description)}</div>
        <div class="admin-controls">
          <label>Status:
            <select class="status-select" data-id="${d._id}">
              <option value="pending" ${d.status === "pending" ? "selected" : ""}>Pending</option>
              <option value="confirmed" ${d.status === "confirmed" ? "selected" : ""}>Confirmed</option>
              <option value="fixed" ${d.status === "fixed" ? "selected" : ""}>Fixed</option>
              <option value="rejected" ${d.status === "rejected" ? "selected" : ""}>Rejected</option>
            </select>
          </label>
          <label>Note:
            <input type="text" class="note-input" data-id="${d._id}"
                   value="${escHtml(d.admin_note || "")}" placeholder="Author note...">
          </label>
          <button class="save-btn" data-id="${d._id}">Save</button>
          <button class="delete-btn" data-id="${d._id}">Delete</button>
        </div>
      </div>
    `).join("\n");

    // Wire up buttons
    listEl.querySelectorAll(".save-btn").forEach(btn => {
      btn.addEventListener("click", () => saveItem(btn.dataset.id));
    });
    listEl.querySelectorAll(".delete-btn").forEach(btn => {
      btn.addEventListener("click", () => deleteItem(btn.dataset.id));
    });

  } catch (err) {
    console.error(err);
    listEl.innerHTML = '<p class="error">Failed to load. Check console.</p>';
  }
}

async function saveItem(id) {
  const status = listEl.querySelector(`.status-select[data-id="${id}"]`).value;
  const note   = listEl.querySelector(`.note-input[data-id="${id}"]`).value;
  try {
    await updateDoc(doc(db, "errata", id), { status, admin_note: note });
    loadAll(filterEl.value);
  } catch (err) {
    console.error(err);
    alert("Save failed: " + err.message);
  }
}

async function deleteItem(id) {
  if (!confirm("Delete this errata entry?")) return;
  try {
    await deleteDoc(doc(db, "errata", id));
    loadAll(filterEl.value);
  } catch (err) {
    console.error(err);
    alert("Delete failed: " + err.message);
  }
}

// --- Filter ---
filterEl.addEventListener("change", () => loadAll(filterEl.value));

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

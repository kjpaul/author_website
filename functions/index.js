// Cloud Functions for pauldejong.com.
//
// subscribe: receives a POST from the notify-me form on the Volume I hub page
// and adds the reader to one or more MailerLite groups. MailerLite is configured
// for account-level double opt-in, so creating the subscriber triggers the
// confirmation email; on confirm the reader lands on the URL configured in the
// MailerLite double opt-in settings (https://pauldejong.com/thanks/).
//
// Secrets (configure once, then redeploy):
//   firebase functions:secrets:set MAILERLITE_API_KEY
//
// Environment parameters (configure in .env or via
// `firebase functions:config:set` style; here we read from process.env):
//   MAILERLITE_GROUP_VOL1      - group ID for "Volume I release" checkbox
//   MAILERLITE_GROUP_VOL23     - group ID for "Volumes II and III release"
//   MAILERLITE_GROUP_PROGRESS  - group ID for "Occasional progress notes"
//
// Deploy:
//   firebase deploy --only functions:subscribe
//
// Local test:
//   firebase emulators:start --only functions,hosting
//   curl -X POST http://127.0.0.1:5001/<project>/us-central1/subscribe \
//     -H 'Content-Type: application/json' \
//     -d '{"email":"test@example.com","groups":["vol1"]}'

// Runtime is pinned to Node.js 22 in firebase.json ("runtime") and package.json
// ("engines"); keep them in sync — firebase.json wins if they differ.
const { onRequest } = require("firebase-functions/v2/https");
const { onDocumentCreated } = require("firebase-functions/v2/firestore");
const { defineSecret } = require("firebase-functions/params");
const { logger } = require("firebase-functions");
const nodemailer = require("nodemailer");
const admin = require("firebase-admin");

admin.initializeApp();

const MAILERLITE_API_KEY = defineSecret("MAILERLITE_API_KEY");
const TURNSTILE_SECRET_KEY = defineSecret("TURNSTILE_SECRET_KEY");

const CHECKBOX_TO_GROUP_ENV = {
  vol1: "MAILERLITE_GROUP_VOL1",
  vol23: "MAILERLITE_GROUP_VOL23",
  progress: "MAILERLITE_GROUP_PROGRESS",
};

const ALLOWED_ORIGINS = [
  "https://pauldejong.com",
  "https://www.pauldejong.com",
  "http://127.0.0.1:8000",
  "http://localhost:8000",
  "http://127.0.0.1:5000",
  "http://localhost:5000",
];

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function resolveGroupIds(keys) {
  const out = [];
  for (const key of keys) {
    const envName = CHECKBOX_TO_GROUP_ENV[key];
    if (!envName) continue;
    const groupId = process.env[envName];
    if (groupId) out.push(groupId);
  }
  return out;
}

function setCors(req, res) {
  const origin = req.headers.origin;
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    res.set("Access-Control-Allow-Origin", origin);
    res.set("Vary", "Origin");
  }
  res.set("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.set("Access-Control-Allow-Headers", "Content-Type");
  res.set("Access-Control-Max-Age", "3600");
}

exports.subscribe = onRequest(
  {
    region: "us-central1",
    secrets: [MAILERLITE_API_KEY, TURNSTILE_SECRET_KEY],
    maxInstances: 5,
  },
  async (req, res) => {
    setCors(req, res);

    if (req.method === "OPTIONS") {
      res.status(204).send("");
      return;
    }
    if (req.method !== "POST") {
      res.status(405).json({ error: "method_not_allowed" });
      return;
    }

    // This grandfathered-public function also serves errata submissions
    // (POST /api/submit-errata). A new function can't be made public because of
    // the org's Domain Restricted Sharing policy, so errata rides on this one.
    // Dispatch by payload shape: errata carries `book`/`turnstileToken`.
    if (req.body && (req.body.book !== undefined || req.body.turnstileToken !== undefined)) {
      await handleErrataSubmit(req, res);
      return;
    }

    const body = req.body || {};
    const email = typeof body.email === "string" ? body.email.trim().toLowerCase() : "";
    const selected = Array.isArray(body.groups) ? body.groups : [];

    if (!EMAIL_RE.test(email) || email.length > 254) {
      res.status(400).json({ error: "invalid_email" });
      return;
    }

    const groupIds = resolveGroupIds(selected);
    if (groupIds.length === 0) {
      res.status(400).json({ error: "no_groups_selected" });
      return;
    }

    try {
      const upstream = await fetch(
        "https://connect.mailerlite.com/api/subscribers",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: `Bearer ${MAILERLITE_API_KEY.value()}`,
          },
          body: JSON.stringify({
            email,
            groups: groupIds,
            status: "unconfirmed",
          }),
        }
      );

      if (!upstream.ok) {
        const text = await upstream.text();
        logger.error("mailerlite_subscribe_failed", {
          status: upstream.status,
          body: text.slice(0, 500),
        });
        res.status(502).json({ error: "upstream_failed" });
        return;
      }

      logger.info("subscribe_ok", { email_hash: hashEmail(email), groups: groupIds.length });
      res.status(200).json({ ok: true });
    } catch (err) {
      logger.error("subscribe_exception", { message: err && err.message });
      res.status(500).json({ error: "internal" });
    }
  }
);

function hashEmail(email) {
  // Tiny non-cryptographic hash used only for log correlation;
  // we do not want to log PII in cleartext.
  let h = 0;
  for (let i = 0; i < email.length; i++) {
    h = (h * 31 + email.charCodeAt(i)) | 0;
  }
  return (h >>> 0).toString(16);
}

// --- Errata submission ------------------------------------------------------
// Errata come in through the public `subscribe` function above, which routes
// POST /api/submit-errata here. We can't make a dedicated function public: the
// org's Domain Restricted Sharing policy blocks granting allUsers to new
// services, and `subscribe` is grandfathered-public, so errata rides on it.
// This handler verifies a Cloudflare Turnstile token and a honeypot field, then
// writes the doc with the Admin SDK. Firestore rules forbid direct client
// writes, so this is the only way in, which keeps the spam bots out.
//
// Setup: create a Turnstile widget at dash.cloudflare.com (site key goes in
// templates/pages/errata.html), then
// `firebase functions:secrets:set TURNSTILE_SECRET_KEY`.

const ERRATA_MAX = { book: 100, page: 200, quote: 4000, description: 4000, email: 254 };

// Called by `subscribe` when the payload looks like an erratum. CORS, OPTIONS,
// and the POST check are already handled by the caller.
async function handleErrataSubmit(req, res) {
  const body = req.body || {};

  // Honeypot: a hidden field real users never fill. If it has content it's a
  // bot; return a fake success so it doesn't learn to adapt.
  if (typeof body.website === "string" && body.website.trim() !== "") {
    res.status(200).json({ ok: true });
    return;
  }

  // Verify the Cloudflare Turnstile token.
  const token = typeof body.turnstileToken === "string" ? body.turnstileToken : "";
  if (!token) {
    res.status(400).json({ error: "captcha_missing" });
    return;
  }
  const ip = req.headers["cf-connecting-ip"] || "";
  const human = await verifyTurnstile(token, TURNSTILE_SECRET_KEY.value(), ip);
  if (!human) {
    res.status(403).json({ error: "captcha_failed" });
    return;
  }

  // Validate the fields.
  const book = trimStr(body.book);
  const page = trimStr(body.page);
  const quote = trimStr(body.quote);
  const description = trimStr(body.description);
  const email = trimStr(body.email);

  if (!book || !page || !quote || !description) {
    res.status(400).json({ error: "missing_fields" });
    return;
  }
  if (book.length > ERRATA_MAX.book || page.length > ERRATA_MAX.page ||
      quote.length > ERRATA_MAX.quote || description.length > ERRATA_MAX.description ||
      email.length > ERRATA_MAX.email) {
    res.status(400).json({ error: "too_long" });
    return;
  }
  if (email && !EMAIL_RE.test(email)) {
    res.status(400).json({ error: "invalid_email" });
    return;
  }

  try {
    await admin.firestore().collection("errata").add({
      book,
      page,
      quote,
      description,
      submitted_by: email || "anonymous",
      status: "pending",
      admin_note: "",
      created_at: admin.firestore.Timestamp.now(),
    });
    res.status(200).json({ ok: true });
  } catch (err) {
    logger.error(`errata_write_failed: ${err && err.message}`, { code: err && err.code });
    res.status(500).json({ error: "internal" });
  }
}

async function verifyTurnstile(token, secret, ip) {
  try {
    const form = new URLSearchParams();
    form.append("secret", secret || "");
    form.append("response", token);
    if (ip) form.append("remoteip", ip);
    const resp = await fetch(
      "https://challenges.cloudflare.com/turnstile/v0/siteverify",
      { method: "POST", body: form }
    );
    const data = await resp.json();
    return !!data.success;
  } catch (err) {
    logger.error("turnstile_verify_exception", { message: err && err.message });
    return false;
  }
}

function trimStr(v) {
  return typeof v === "string" ? v.trim() : "";
}

// --- Errata notification ----------------------------------------------------
// When a reader submits an erratum (a new doc in the `errata` collection),
// email the author so it can be reviewed in the admin dashboard.
//
// Sent through the author's Google Workspace over Gmail SMTP, so no extra
// email service is needed. One-time setup:
//   1. On the Google account named in GMAIL_USER, turn on 2-Step Verification,
//      then create an App Password (Google Account > Security > App passwords).
//   2. firebase functions:secrets:set GMAIL_APP_PASSWORD   (paste the 16-char
//      app password; the spaces Google shows are stripped automatically)
//   3. firebase deploy --only functions:onErrataCreated
//
// Environment parameters (see functions/.env.example):
//   GMAIL_USER           - Workspace account that sends and authenticates;
//                          must match the account the App Password belongs to.
//   MAIL_FROM            - From header (default: GMAIL_USER)
//   ERRATA_NOTIFY_TO     - destination address (default author@pauldejong.com)
//   ADMIN_DASHBOARD_URL  - admin link included in the email body

const GMAIL_APP_PASSWORD = defineSecret("GMAIL_APP_PASSWORD");

exports.onErrataCreated = onDocumentCreated(
  {
    document: "errata/{errataId}",
    region: "us-central1",
    secrets: [GMAIL_APP_PASSWORD],
    maxInstances: 5,
  },
  async (event) => {
    const snap = event.data;
    if (!snap) return;
    const d = snap.data() || {};

    // App passwords are displayed with spaces ("abcd efgh ijkl mnop");
    // Gmail accepts them without, so strip whitespace.
    const appPassword = (GMAIL_APP_PASSWORD.value() || "").replace(/\s+/g, "");
    const gmailUser = process.env.GMAIL_USER || "";
    if (!appPassword || !gmailUser) {
      // Not configured yet: skip quietly rather than failing (and retrying).
      logger.warn("gmail_not_configured", {
        msg: "GMAIL_APP_PASSWORD or GMAIL_USER not set; skipping errata email",
      });
      return;
    }

    const to = process.env.ERRATA_NOTIFY_TO || "author@pauldejong.com";
    const from = process.env.MAIL_FROM || gmailUser;
    const dashUrl = process.env.ADMIN_DASHBOARD_URL || "https://pauldejong.com/errata/admin/";

    const book = d.book || "unknown";
    const page = d.page || "?";
    const subject = `New errata: ${book} (page ${page})`;

    const text = [
      "A new erratum was submitted on pauldejong.com.",
      "",
      `Book:         ${book}`,
      `ISBN:         ${d.isbn || "n/a"}`,
      `Page/Section: ${page}`,
      `Submitted by: ${d.submitted_by || "anonymous"}`,
      `Status:       ${d.status || "pending"}`,
      "",
      "Quote:",
      d.quote || "(none)",
      "",
      "Description:",
      d.description || "(none)",
      "",
      `Review and approve it here: ${dashUrl}`,
      `Document ID: ${event.params.errataId}`,
    ].join("\n");

    try {
      const transporter = nodemailer.createTransport({
        host: "smtp.gmail.com",
        port: 465,
        secure: true,
        auth: { user: gmailUser, pass: appPassword },
      });

      await transporter.sendMail({ from, to, subject, text });
      logger.info("errata_email_sent", { errataId: event.params.errataId, book });
    } catch (err) {
      logger.error("gmail_send_failed", { message: err && err.message });
    }
  }
);

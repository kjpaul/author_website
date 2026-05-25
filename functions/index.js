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

const { onRequest } = require("firebase-functions/v2/https");
const { onDocumentCreated } = require("firebase-functions/v2/firestore");
const { defineSecret } = require("firebase-functions/params");
const { logger } = require("firebase-functions");

const MAILERLITE_API_KEY = defineSecret("MAILERLITE_API_KEY");

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
    secrets: [MAILERLITE_API_KEY],
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

// --- Errata notification ----------------------------------------------------
// When a reader submits an erratum (a new doc in the `errata` collection),
// email the author so it can be reviewed in the admin dashboard.
//
// Email goes out via Resend (https://resend.com), a simple transactional
// email API. One-time setup:
//   1. Create a free Resend account and generate an API key.
//   2. firebase functions:secrets:set RESEND_API_KEY      (paste the key)
//   3. (Recommended) Verify pauldejong.com in Resend, then set RESEND_FROM
//      to an address on that domain. Until a domain is verified, Resend's
//      default onboarding sender delivers to the account owner's inbox.
//   4. firebase deploy --only functions:onErrataCreated
//
// Optional environment parameters (see functions/.env.example):
//   ERRATA_NOTIFY_TO     - destination address (default author@pauldejong.com)
//   RESEND_FROM          - From header (default onboarding@resend.dev)
//   ADMIN_DASHBOARD_URL  - admin link included in the email body

const RESEND_API_KEY = defineSecret("RESEND_API_KEY");

exports.onErrataCreated = onDocumentCreated(
  {
    document: "errata/{errataId}",
    region: "us-central1",
    secrets: [RESEND_API_KEY],
    maxInstances: 5,
  },
  async (event) => {
    const snap = event.data;
    if (!snap) return;
    const d = snap.data() || {};

    const apiKey = RESEND_API_KEY.value();
    if (!apiKey) {
      // Not configured yet: skip quietly rather than failing (and retrying).
      logger.warn("resend_key_missing", {
        msg: "RESEND_API_KEY not set; skipping errata email",
      });
      return;
    }

    const to = process.env.ERRATA_NOTIFY_TO || "author@pauldejong.com";
    const from = process.env.RESEND_FROM || "Orbital Ring Errata <onboarding@resend.dev>";
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
      const resp = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({ from, to, subject, text }),
      });

      if (!resp.ok) {
        const body = await resp.text();
        logger.error("resend_send_failed", {
          status: resp.status,
          body: body.slice(0, 500),
        });
        return;
      }
      logger.info("errata_email_sent", { errataId: event.params.errataId, book });
    } catch (err) {
      logger.error("resend_exception", { message: err && err.message });
    }
  }
);

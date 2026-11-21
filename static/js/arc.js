// The advance-reader-copy application form on /arc/.
// Posts to /api/arc (the `subscribe` Cloud Function, dispatched on kind: "arc").
(function () {
  const formEl = document.getElementById("arc-form");
  if (!formEl) return;
  const statusEl = document.getElementById("form-status");
  const btn = formEl.querySelector("button[type=submit]");
  const btnHtml = btn.innerHTML;

  // "example.com" becomes "https://example.com"; an empty field stays empty.
  function normalizeLink(v) {
    const t = (v || "").trim();
    if (!t) return "";
    return /^https?:\/\//i.test(t) ? t : "https://" + t;
  }

  function show(kind, text) {
    statusEl.innerHTML = "";
    const span = document.createElement("span");
    span.className = kind;
    span.textContent = text;
    statusEl.appendChild(span);
  }

  formEl.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!formEl.checkValidity()) {
      formEl.reportValidity();
      return;
    }

    const platforms = Array.from(formEl.querySelectorAll('input[name="platforms"]:checked')).map((el) => el.value);
    const payload = {
      kind: "arc",
      name: formEl.name.value.trim(),
      email: formEl.email.value.trim(),
      background: formEl.background.value,
      platforms,
      format: formEl.format.value,
      link: normalizeLink(formEl.link.value),
      why: formEl.why.value.trim(),
      newsletter: formEl.newsletter.checked, // also join the release news list
      website: formEl.website.value, // honeypot
      turnstileToken: formEl["cf-turnstile-response"]?.value || "",
    };

    btn.disabled = true;
    btn.textContent = "Sending…";
    statusEl.textContent = "";

    try {
      const resp = await fetch("/api/arc", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const json = await resp.json().catch(() => ({}));
      if (resp.ok && json.ok) {
        show("success", "Thanks. Please check your email and click the confirmation button.");
        formEl.reset();
      } else if (json.error === "captcha_failed" || json.error === "captcha_missing") {
        show("error", "Please complete the verification box and try again.");
      } else if (json.error === "invalid_email") {
        show("error", "That email address does not look right.");
      } else if (json.error === "invalid_link") {
        show("error", "The link should start with http:// or https://.");
      } else {
        show("error", "Something went wrong. Please try again, or use the contact page.");
      }
    } catch (_err) {
      show("error", "Network error. Please try again.");
    } finally {
      btn.disabled = false;
      btn.innerHTML = btnHtml;
      if (window.turnstile) window.turnstile.reset();
    }
  });
})();

/**
 * MONARCH® Portfolio v37 -> 24/7 Cloud Lead Intake & Client Portal Bridge
 * Drop into adil-chandio/portfolio index.html before </body>:
 * <script src="https://monarch-workspace-beryl.vercel.app/portfolio-intake.js" defer></script>
 */
(function () {
  const INTAKE_ENDPOINT = "https://oeqeqlgatdlqbuywktnu.supabase.co/functions/v1/public-intake";
  const STUDIO_PORTAL_URL = "https://monarch-workspace-beryl.vercel.app/";

  function mountPortalBadge() {
    if (document.getElementById("monarch-portal-pill")) return;
    const link = document.createElement("a");
    link.id = "monarch-portal-pill";
    link.href = STUDIO_PORTAL_URL;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "CLIENT PORTAL & SERVICES ↗";
    Object.assign(link.style, {
      position: "fixed",
      right: "18px",
      bottom: "18px",
      zIndex: "9999",
      padding: "11px 16px",
      borderRadius: "999px",
      background: "#0a0a0b",
      color: "#ece9e2",
      border: "1px solid rgba(210,31,43,0.65)",
      boxShadow: "0 12px 30px rgba(0,0,0,0.45)",
      fontFamily: "Manrope, sans-serif",
      fontSize: "11px",
      fontWeight: "700",
      letterSpacing: "0.12em",
      textDecoration: "none",
    });
    document.body.appendChild(link);
  }

  function wireContactForm() {
    const form = document.getElementById("contactForm") || document.querySelector("form");
    if (!form || form.dataset.monarchWired === "1") return;
    form.dataset.monarchWired = "1";

    form.addEventListener(
      "submit",
      async function (event) {
        event.preventDefault();
        event.stopImmediatePropagation();

        const fd = new FormData(form);
        const inputs = Array.from(form.querySelectorAll("input, textarea, select"));
        const getVal = (keys, fallbackIdx) => {
          for (const k of keys) {
            const v = fd.get(k);
            if (v && String(v).trim()) return String(v).trim();
          }
          return inputs[fallbackIdx]?.value?.trim() || "";
        };

        const payload = {
          client_name: getVal(["name", "client_name", "fullName"], 0),
          client_email: getVal(["email", "client_email"], 1),
          service_slug: getVal(["service", "project_type"], 2) || "signature-websites",
          project_brief:
            getVal(["message", "brief", "project_brief", "details"], inputs.length - 1) ||
            "Portfolio inquiry submitted.",
          source: "portfolio_v37",
        };

        const btn = form.querySelector('button[type="submit"], input[type="submit"]');
        const prevText = btn ? btn.textContent : "";
        if (btn) {
          btn.disabled = true;
          btn.textContent = "SENDING TO MONARCH CLOUD…";
        }

        try {
          const res = await fetch(INTAKE_ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          const data = await res.json();
          if (!res.ok || !data.ok) throw new Error(data.error || "Submission error");
          form.reset();
          if (btn) btn.textContent = "BRIEF RECEIVED ✓ — WE'LL REPLY SHORTLY";
        } catch (_err) {
          if (btn) btn.textContent = "SAVED FALLBACK — OPENING EMAIL…";
          window.location.href =
            "mailto:workadilchandio@gmail.com?subject=" +
            encodeURIComponent("MONARCH Project Inquiry — " + payload.client_name) +
            "&body=" +
            encodeURIComponent(payload.project_brief + "\n\nReply to: " + payload.client_email);
        } finally {
          if (btn) {
            setTimeout(() => {
              btn.disabled = false;
              btn.textContent = prevText || "SEND MESSAGE";
            }, 4200);
          }
        }
      },
      true
    );
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      mountPortalBadge();
      wireContactForm();
    });
  } else {
    mountPortalBadge();
    wireContactForm();
  }
})();

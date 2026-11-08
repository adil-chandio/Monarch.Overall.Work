# MONARCH® — $0 Launch Playbook

**Goal:** first paying client without spending any money. Domain bought later, from client money.

> Rule: a domain is *perception*. A payment rail is *revenue*. Get revenue first.

---

## Step 1 — Clean address, $0 (15 min)

Current link is a deployment URL: `monarch-workspace-beryl.vercel.app` (the `-beryl` part is random and looks temporary).

### Option A — Cloudflare Pages (recommended: commercial use allowed on free plan)
1. Sign up at `dash.cloudflare.com` (no card needed).
2. Workers & Pages → Create → Pages → Connect to Git → pick `Monarch.Overall.Work`.
3. Build settings:
   - Framework preset: `Vite`
   - Build command: `npm run build`
   - Output directory: `dist`
4. Deploy → you get `monarch-workspace.pages.dev`.
5. Project → Settings → rename project if needed so the address reads better, e.g. `monarchstudio.pages.dev`.
6. Later, when you own a domain: Custom domains → add `monarchstudio.com` → Cloudflare gives you the CNAME/A records. **No rebuild required.**

### Option B — Keep Vercel, fix the address
Vercel project domain is `<project-name>.vercel.app` — free and clean. The random suffix only appears on individual deployment URLs.

- Vercel → Project → Settings → Domains → add `monarch-studio.vercel.app`.
- Use that as your public link everywhere.
- Note: Vercel Hobby is officially non-commercial only. Fine while the site is a portfolio; move to Cloudflare Pages (free) or Pro ($20/mo) before you start taking card payments on it.

**Pick one. Never share the `-beryl` URL again.**

---

## Step 2 — Get paid, $0 (20 min)

### Foreign clients (USD)
1. `payoneer.com` → sign up as an individual/ freelancer (free).
2. Complete verification (CNIC + bank account).
3. Dashboard → **Get Paid** → **Request a Payment**.
4. Fill: client email, amount, description, due date → attach invoice PDF → send.
5. Client pays by **credit card (~3%)** or bank transfer (~1%).
6. Funds land in Payoneer → withdraw to Pakistani bank.

### Local clients (PKR)
- **Raast / bank transfer / SadaPay** — instant, 0% fee. Send a clean PDF invoice.
- Later, if volume grows: Safepay merchant account → hosted payment links (PKR only, max Rs 250,000/txn, approval is strict).

### Do not attempt
- **Stripe** — Pakistan-registered businesses are not supported.
- **Wise Business** — Pakistan residents cannot sign up (foreign entity required).

---

## Step 3 — Invoice that looks like a studio made it

Every invoice must contain:

- Your name / studio name, city (`Hyderabad, Pakistan`)
- Client name + company
- Invoice number (`MON-2026-001`) and date
- Line items with fixed scope (deliverable, revision count, timeline)
- Total, currency, and **payment terms: 50% advance / 50% on delivery**
- Payment link or account details
- A footer line: `Delivery: 1080p60 master + source files on final settlement`

Free invoice generators: Payoneer's built-in invoice, or `freeinvoicebuilder.com`.

---

## Step 4 — Make Gmail look intentional (5 min)

No domain yet = no `adil@monarchstudio.com`. So make the Gmail itself deliberate:

- **Display name:** `Adil Chandio · MONARCH® Studio` (not just "adil")
- **Signature:**
  ```
  Adil Chandio
  MONARCH® Studio — Design & Film
  Hyderabad, PK
  [showreel link]  [portfolio link]
  1080p60 · fixed scope · fixed price
  ```
- **Never** write `adilchandio@gmail.com` in a bio. Write **"Email"** and hyperlink the word.
- Reply within 12 hours. Speed is a trust signal that costs nothing.

---

## Step 5 — Proof block (already done, just point at it)

Put these three numbers in every pitch, gig description and invoice footer:

- **583,290** real views
- **92.5%** peak retention
- **80.5%** viewed-vs-swiped

Link: showreel page + `MON-DEMO26` client portal (it proves you run a real delivery pipeline).

---

## Step 6 — First money in

Order of operations, cheapest first:

1. **Fiverr** — 2 gigs only:
   - `Website + Brand Audit — 48hr, 12-point report` — **$79**
   - `Cinematic 3-Second Teaser` — **$120**
   - Both descriptions end with: *"Full build available as an order upgrade."*
   - Fiverr takes 20%; buyer pays +5.5%. Payout clears in 14 days.
   - Goal for 90 days: **12–15 five-star reviews**. Profit is secondary.
2. **Direct outreach** — 10 messages/day to local businesses (restaurants, clinics, gyms, real estate). 100 messages → 2–3 conversations → 1 job.
3. **Upwork / Contra** — for $450+ scope. Contra is 0% commission; Upwork is 10%.

---

## Step 7 — Now buy the domain (from client money)

When the first payment lands:

- `.com` at Cloudflare Registrar or Namecheap: **~$10–12/year**
- Attach to the Cloudflare Pages project (Custom domains → add)
- **Zoho Mail Free** → `adil@monarchstudio.com` (5 users, 5 GB each, $0)
  - DNS: MX → `mx.zoho.com` / `mx2.zoho.com` / `mx3.zoho.com`
  - SPF: `v=spf1 include:zoho.com ~all`
  - DKIM + DMARC: get values from Zoho admin panel
- Nothing else changes. Same site, same Supabase portal, just a real address.

### If you are a student — do this instead, it is $0
**GitHub Student Developer Pack** → free domain for 1 year, registered in your own name:
- Namecheap: free **`.me`** + free SSL
- Name.com: 25+ extensions incl. `.dev`, `.app`, `.studio`
- `.TECH`: one standard `.tech` free for 1 year
- Needs: dated proof of enrollment or school email.

Claim order: GitHub Education verification → the domain offer in the pack page → check out at $0.

---

## Tech stack summary

| Layer | $0 choice | Paid upgrade (later) |
|---|---|---|
| Hosting | Cloudflare Pages (`*.pages.dev`) | — free forever, commercial OK |
| Address | `pages.dev` subdomain | `.com` ~$12/yr |
| Email | Gmail w/ deliberate signature | Zoho Mail Free on own domain ($0) |
| Payments USD | Payoneer request-a-payment | — |
| Payments PKR | Raast / bank / SadaPay | Safepay merchant account |
| Client portal | Supabase (existing) | — |
| Video delivery | GitHub + Google Drive (existing) | R2 / S3 if volume grows |

---

## Hard rules

- Never share `*.vercel.app` random deployment URLs.
- Never share email as raw text — hyperlink it.
- Never quote a price without scope + revision count + timeline.
- Never deliver the clean master before settlement — watermarked review copy first (already built into the portal).
- Never put a business site on **GitHub Pages** — commercial use is prohibited by their usage policy.
- Never attempt Stripe or Wise Business from Pakistan.

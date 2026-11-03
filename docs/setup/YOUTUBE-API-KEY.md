# YouTube Data API v3 — key lo, 5 minute, $0, koi card nahi

> Ye sirf **public data** ke liye key hai (search, video stats, channel info, comments).
> Upload ya private analytics ke liye OAuth chahiye — uske liye alag setup hai.

**Kya milega:** exact view/like/comment counts, 50-item search pages, `commentThreads`
(comment mining), aur throttle ka koi masla nahi.

**Kya nahi milega:** search volume (wo kisi API mein nahi hai), aur quota ka upgrade
(10,000 units/day fixed — paid tier maujood nahi hai).

---

## Step 1 — Google Cloud Console kholo

👉 https://console.cloud.google.com/

Usi Google account se login karo jo tumhare channel ke saath hai (`workadilchandio@gmail.com`).
Naya account banane ki zaroorat nahi. Agar pehli baar aaye ho to terms accept kar lo.

## Step 2 — Project banao

Top bar mein project dropdown → **New project** → naam: `monarch-yt-intel` → **Create**.
~10 second. **Project select karna na bhoolo** — galat project par key ban gayi to 403 aata hai.

> Quota **project** par hota hai, key par nahi. Ek project = 10,000 units/day.

## Step 3 — API enable karo

Left menu → **APIs & Services → Library** → search: `YouTube Data API v3`
→ usko kholo → **Enable**.

**Ye step skip kar diya to** key bilkul theek hogi lekin har call `403 accessNotConfigured`
degi. Yehi sabse aam ghalti hai.

## Step 4 — Key banao

**APIs & Services → Credentials → + Create credentials → API key**.
Key turant screen par aa jayegi, `AIza…` se shuru hoti hai, 39 characters.

**Copy kar lo — dobara poori key nahi dikhegi.**

## Step 5 — Key ko lock karo (ye important hai)

Key par click → **Edit**:

| Section | Set karo |
|---|---|
| Application restrictions | **None** (local CLI/CI ke liye) ya **IP addresses** — agar Vercel par hai to server IP |
| API restrictions | **Restrict key** → sirf `YouTube Data API v3` |

Agar key leak ho jaye to sirf ek API use ho sakti hai, aur tumhare 10k quota par
koi aur nahi chadh sakta. **Kabhi bhi key ko browser code (React) mein na daalo** —
frontend bundles public hote hain.

## Step 6 — Key lagao (teen jagah, jo tumhe chahiye)

**A) Local machine (sabse pehle ye):**

```bash
export YOUTUBE_API_KEY="AIza..."      # isi terminal session ke liye
```

Har naye terminal mein dobara chahiye. Permanent chahiye to `~/.bashrc` ya `~/.zshrc`
mein wahi line daal do.

Ya `.env.local` (repo already gitignore karta hai):

```bash
YOUTUBE_API_KEY=AIza...
```

Aur phir: `set -a; source .env.local; set +a`

**B) GitHub Actions (weekly research run):**

Repo → **Settings → Secrets and variables → Actions → New repository secret**
Name: `YOUTUBE_API_KEY` · Secret: `AIza...`

Workflow already `${{ secrets.YOUTUBE_API_KEY }}` padh raha hai — kuch aur nahi karna.

**C) Vercel:**

Filen **nahi** chahiye. Key sirf server-side tool chala raha hai; UI `public/yt-intel/index.json`
padhta hai jo CI commit karta hai. Key ko frontend env mein daalna **mana** hai.

---

## Step 7 — Verify (guess mat karo)

```bash
python -m yt_intel doctor
```

Expected output jab sab theek ho:

```
  PASS  key present — AIzaAb…9xYz (39 chars)
  PASS  key shape looks right — starts with AIza…
  PASS  channels.list — 1 channel returned (1 quota unit)
  PASS  search.list — lane=api status=ok items=1 (100 quota units)

  quota used today : 101 / 10000 units
  searches left    : 98
```

Har failure ka matlab:

| Output | Matlab | Fix |
|---|---|---|
| `no YOUTUBE_API_KEY` | env var set nahi | Step 6A |
| `API not enabled on this project` | Step 3 chhoot gaya | Library → Enable |
| `key rejected` | galat/incomplete key, ya delete ho gayi | nayi key banao |
| `quotaExceeded` | aaj ki 10,000 khatam | midnight Pacific tak wait (Pakistan ~1:00 PM) |
| `TLS/SSL connection has been closed` | **network block**, key ka masla nahi | doosra network/VPN, ya CI par chalao |

---

## Quota maths (kya kitna khaata hai)

| Call | Units | 10,000 mein kitne |
|---|---|---|
| `videos.list` (50 videos ek saath) | 1 | 10,000 |
| `channels.list` | 1 | 10,000 |
| `commentThreads.list` (100 comments) | 1 | 10,000 |
| **`search.list`** | **100** | **100** |
| `videos.insert` (upload) | 1600 | 6 |

Isliye `yt_intel` search par quota bachata hai: ek `topic` run = **1 search (100) + 1 videos (1)**
≈ 101 units → din mein **~99 topic research**. Cache on hone se dobara same query 0 units.

Budget state yahan rehta hai: `.cache/yt-intel/budget.json` (gitignored).
`python -m yt_intel lanes` se kabhi bhi dekho.

---

## Key kabhi share na karo

- ❌ React/JSX/HTML mein — bundle public hota hai
- ❌ commit mein — `.env*` gitignored hai, wahi use karo
- ❌ screenshot/chat mein
- ✅ GitHub Secrets, ya local env var
- ✅ agar leak ho jaye: Cloud console → Credentials → key → **Delete** → nayi banao (30 second)

---

# GitHub Secrets — exactly kaunsi secret, kahan, kyun

Repo: `adil-chandio/Monarch.Overall.Work` → **Settings → Secrets and variables → Actions**

## Teen secrets (sirf pehli zaroori hai)

| # | Name | Value | Kyun chahiye | Na ho to kya hota hai |
|---|---|---|---|---|
| 1 | `YOUTUBE_API_KEY` | `AIza...` | exact stats + comment mining + koi throttle nahi | keyless mode chal jata hai; datacenter IP se YouTube block karta hai → har run `RETRY` (aaj yahi ho raha hai) |
| 2 | `YT_COMMIT_KEY` | ek SSH **deploy key** (private half) | bot ko `public/yt-intel/index.json` commit karne de | report ban jaati hai lekin commit nahi hoti; run artifact se download karni padegi |
| 3 | *(optional)* `SUPABASE_*` | — | cloud workspace | abhi zaroorat nahi |

**Sirf local par test karna hai?** Koi secret nahi chahiye — `export YOUTUBE_API_KEY=...` kafi hai.

## Deploy key kaise banayein (secret #2)

Local terminal par:

```bash
ssh-keygen -t ed25519 -C "monarch-yt-intel" -f ~/.ssh/monarch_yt -N ""
cat ~/.ssh/monarch_yt.pub          # PUBLIC half -> GitHub
cat ~/.ssh/monarch_yt             # PRIVATE half -> secret YT_COMMIT_KEY
```

1. **Public half** → repo → **Settings → Deploy keys → Add deploy key** → paste → **✅ Allow write access** tick → Add key
2. **Private half** → **Settings → Secrets and variables → Actions → New repository secret** → name `YT_COMMIT_KEY` → paste (poora block, `-----BEGIN...` se `-----END...` tak) → Add secret

Phir workflow khud `git remote set-url` karke `git@github.com:` par push karega.

> **Kyoon deploy key aur `GITHUB_TOKEN` nahi?** Repo ka `GITHUB_TOKEN` is branch par push
> mein pehle hi fail ho chuka hai (render run `41595732667`), aur protected branch / fork
> se aane wale run par wo kabhi push nahi kar sakta. Deploy key durable hai.

## Verify karo ke secrets lag gaye

```bash
gh secret list -R adil-chandio/Monarch.Overall.Work
```
Expected:
```
YOUTUBE_API_KEY   2026-11-03T…
YT_COMMIT_KEY     2026-11-03T…
```
(Values kabhi print nahi hoti — sirf naam aur date.)

Manual run chalao (secret par password/token kabhi chat mein na bhejo, sirf repo settings mein):

```bash
gh workflow run "YT Intel — topic research" -R adil-chandio/Monarch.Overall.Work -f topic="ai video editing"
gh run watch $(gh run list --workflow="YT Intel — topic research" -L 1 --json databaseId -q '.[0].databaseId')
```

## Schedules (do, aur wo bhi free)

| workflow | kab | kya |
|---|---|---|
| `yt-intel.yml` | har **Somwar 04:00 UTC** (PK 09:00) | `config/topic-queue.json` ke top 4 topics, quota dekh kar |
| `render-showreel-60fps.yml` | push par | showreel render + audio gates |

CI minutes public repo par **unlimited aur free** hain — koi card nahi.

## Ek zaroori baat

GitHub Actions ka runner bhi ek **datacenter IP** hai. Iska matlab: agar `YOUTUBE_API_KEY`
set **nahi** hai to CI bhi wahi `RETRY` dega jo is sandbox ne diya. Key lagne ke baad hi
CI se asli numbers aayenge — ye workflow ka issue nahi, network ki asliyat hai.

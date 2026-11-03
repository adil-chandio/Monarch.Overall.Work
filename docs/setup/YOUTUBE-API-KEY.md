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

## Ek topic abhi chalana ho (bina key ke bhi chalega)

Key na ho to bhi `yt-intel` keyless lane se chalta hai — bas `search.list` jaisi
precision nahi milti, aur datacenter IP par YouTube throttle kar deta hai (`RETRY`).
Do tareeqe hain:

**1. Marker file (recommended — key chahiye nahi, sirf edit + push):**

`yt-intel-trigger.txt` ki pehli line = topic, doosri line = filter (optional):

```
ai b roll generation
thisMonth
```

Khali file = poora queue (`config/topic-queue.json`) chalega.

Filter ke allowed values (keyless lane aur API lane dono samajhte hain):

| value | matlab | kab |
|---|---|---|
| `relevance` (default) | YouTube ka apna order | "is topic ko kaun hold karta hai" |
| `date` | newest first | naya kya aa raha hai |
| `viewCount` | sabse zyada views | all-time ceiling |
| `thisMonth` | pichhle 30 din | fast-moving topic par **yehi** — warna sample museum ban jata hai |
| `thisWeek` | pichhle 7 din | trend break dekhne ke liye |

**2. Terminal (local machine par, key ke saath):**

```bash
python -m yt_intel topic "ai b roll generation" --limit 30 --order thisMonth \
  --json public/yt-intel/ai-b-roll-generation.json
node scripts/yt-index.mjs
```

> **Kyun `thisMonth` likha hai:** pehla `shorts retention hook` run relevance order par
> chala aur sample **poora 1–3 saal purana** nikla — us par `NO` aaya jo asal mein
> "market" ka nahi, "archive" ka faisla tha. Filter lagane ke baad `ai b roll generation`
> ka sample 1–28 din purana aaya, median 9 views (naya topic), aur verdict badal gaya.

---

## Key lagne ke baad: pehla asli run (8 commands, ~3 minute)

Ye order mein chalao. Har step ke saamne likha hai "acha" kya dikhna chahiye — agar kuch
aur dikhe to usi jagah ruk jao, aage mat barho.

```bash
# 1. key environment mein hai?
export YOUTUBE_API_KEY="AIza…"
python -m yt_intel lanes
#    good: lane api · quota 10000 remaining
#    bura:  lane web  -> key load nahi hui (shell restart / .env.local check)

# 2. key asal mein kaam karti hai?
python -m yt_intel doctor
#    good: PASS key present / key shape / channels.list / search.list,
#          phir "quota used today : 101 / 10000 units" aur "searches left : 98"
#    bura: "API not enabled on this project" -> Step 3 (API enable) chhoot gaya
#          "key rejected"                   -> key galat paste hui (space / delete ho gayi)
#          timeout / SSL                    -> network, key ka masla nahi

# 3. pehla topic (1 search = 100 units)
python -m yt_intel topic "ai video editing" --limit 30 \
  --json public/yt-intel/ai-video-editing.json
#    good: TOP VIDEOS mein asli views, phir DECISION (GO / SHARPEN / NO)
#    bura: RETRY -> lane web par gir gaya, step 1 dobara

# 4. comment mining (1 unit — sabse sasta asli signal)
python -m yt_intel comments <WO_VIDEO_ID> --limit 100
#    good: n=NN · asks / objections / wants ke saath shares
#    bura: error 403 commentsDisabled -> us video par comments band hain, doosri chuno

# 5. channel (RSS lane, 0 units)
python -m yt_intel channel @mkbhd

# 6. UI ka index
node scripts/yt-index.mjs
#    good: index: 6 reports -> public/yt-intel/index.json

# 7. browser: workspace -> YouTube Automation -> Research desk
#    har card par verdict + conf + median views + views/hour dikhna chahiye

# 8. CI ko bhi de do (secret pehle lag chuka hona chahiye)
printf 'ai b roll generation\nthisMonth\n' > yt-intel-trigger.txt
git add yt-intel-trigger.txt && git commit -m "ci: first keyed topic run" && git push
#    gh run watch  -> "Key doctor" step PASS hona chahiye, skip nahi
```

> **Quota ka hisaab:** step 3 ≈ 101 units (1 search + 1 videos.list), step 4 = 1 unit.
> 10,000 units/day ka matlab ≈ 99 topics/day. Queue `max_per_run: 4` par capped hai, aur
> cache (`.cache/yt-intel/`) same query dobara chalane par 0 units leta hai.

### Ab tak kya kya unproven hai (honest list)

| cheez | status |
|---|---|
| keyless web lane (search, ages, views/hour) | **live** — CI par 6 topics measure ho chuke |
| `doctor` / quota accounting | likha hua, **kabhi key ke saath chala nahi** |
| Data API lane ke parsers (`videos.list` shape) | likha hua, key ke baghair test nahi ho sakta |
| comment mining ke phrase lists | synthetic comments par 8 assertions pass; asli comments par nahi |
| `style.py` ka cut threshold (0.22) | ek 36s film par tuned — doosri reference chahiye |

---

## Agar secret add karne ke baad bhi lane `web` rahe (jo ab hua)

Ye is repo par **asal mein hua**: screenshot mein `YTAP1` secret maujood tha, magar har run
keyless chala. Guess mat karo — repo khud jawab likh deta hai:

```bash
git pull
cat public/yt-intel/lanes.json
```

```json
{
  "lane": "web",
  "key_present": false,
  "key_secret_name": "missing",
  "secrets_seen": { "YOUTUBE_API_KEY": false, "YTAP1": false, "YT_KEY": false }
}
```

| `secrets_seen` | matlab | fix |
|---|---|---|
| sab `false` | koi secret run tak **pahuncha hi nahi** | neeche checklist |
| koi ek `true`, phir bhi `lane: web` | naam resolve nahi hua | `YOUTUBE_API_KEY` naam se dobara banao |
| `key_present: true`, `lane: api` | ho gaya — `doctor` chalao | — |

**Checklist (jahan hum atke hain):**

1. **Sahi repo?** Secret usi repo par hona chahiye jahan workflow chalta hai:
   `adil-chandio/Monarch.Overall.Work`. Fork/organisation par ban gaya to run ko nahi milega.
2. **Sahi tab?** Settings → Secrets and variables → **Actions** → *Repository secrets*.
   *Environment secrets* aur *Dependabot* alag hote hain aur `research` job ko nahi milte.
3. **Value khali to nahi?** Secret add karte waqt box khali chhod diya ho to GitHub bhi khali
   value rakhta hai — UI phir bhi "secret added" dikhata hai.
4. **Naam:** `YOUTUBE_API_KEY` (workflow `YTAP1` / `YTAPI1` / `YT_KEY` / `YT_API_KEY` bhi
   maanta hai, magar standard naam hi rakho).
5. **Public repo par bhi secrets kaam karte hain** — fork se aane wale PR par nahi, lekin
   apne branch ke push par hamesha.
6. Phir bhi na chale to: secret delete karke **dobara** banao, aur ek naya commit push karo
   (`yt-intel-trigger.txt` ki teesri line badal do — wahi run trigger karti hai).

> `lanes.json` sirf **presence** likhta hai (`true`/`false`), value kabhi nahi — wo file public
> hai aur site par serve hoti hai. Key ka sirf pehla 4 characters (`AIza`) check hota hai.

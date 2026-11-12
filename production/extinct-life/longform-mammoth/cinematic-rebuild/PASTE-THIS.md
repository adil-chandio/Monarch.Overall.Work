# PASTE THIS — The Last Mammoths (13:16 review reel)

Upload-ready copy for YouTube. Nothing to edit except the contact address.

Chapter timestamps were pulled from the reel's own caption track and machine-checked by
`edit/validate_metadata.py`. If the cut changes, re-run the validator before uploading.

---

## THE THREE PACKAGES (Test & Compare takes exactly three)

YouTube's native test accepts **three variants** — and the useful unit is a **title +
thumbnail pair**, not a thumbnail alone. Ship these three, in this order. **Slot 1 first**,
because an inconclusive test falls back to variant 1.

| slot | title | thumbnail | the argument it makes |
|---|---|---|---|
| **1** | `Who Killed The Last Mammoths?` | `A-they-were-still-here.jpg` | crime + animal |
| **2** | `Four Witnesses. No Verdict.` | `D-no-verdict.jpg` | this is a case file, not a nature doc |
| **3** | `They Were Still Here 4,000 Years Ago` | `B-what-killed-them.jpg` | the fact first, the mystery second |

Round 2 swaps the losing slot for `C-one-genome.jpg` (map). See §8 of
`METADATA-RESEARCH.md` for the full four-round sequence.

**Upload from `public/thumbnails/upload-1920/`** — 1920×1080 copies. A single variant under
1280×720 makes YouTube downscale *every* variant in the test to 854×480.

---

## TITLE

Primary (slot 1):

    Who Killed The Last Mammoths?

Alternates: `Four Witnesses. No Verdict.` · `They Were Still Here 4,000 Years Ago`

Spares, in launch order, with character counts:

| title | chars | mechanism |
|---|---|---|
| Who Killed The Last Mammoths? | 29 | case file + specificity |
| They Were Still Here 4,000 Years Ago | 36 | scale shock |
| Four Witnesses. No Verdict. | 27 | the film's structure |
| The Last Mammoths Didn't Die Out. They Were Trapped. | 52 | belief reversal |
| Why The Last Mammoths Went Extinct (Nobody Agrees) | 50 | conceded uncertainty |
| Ten Generations. No Witnesses. | 30 | absence as the object |
| One Island. One Herd. 4,000 Years. | 34 | scale ladder |
| The Mammoth's Last 10 Generations Are Missing | 45 | missing-data mystery |
| What Killed The Wrangel Island Mammoths? | 40 | case file + place |
| A Possibility Is Not A Verdict | 30 | brand title, not a launch title |

---

## DESCRIPTION

    Who killed the last mammoths? For thousands of years a single herd survived on Wrangel
    Island in the Arctic Ocean — long after the mainland herds were gone. Then, 4,000 years
    ago, they vanished. No written record. No witnesses. Only bones, isotopes and DNA.

    This is a cold case with four witnesses.

    A 2017 genome comparison found the genetic damage of isolation — and predicted a satin
    coat nobody ever saw. A 2019 isotope study found their diet stable right up to the end,
    and something in the water beginning to change. The archaeology says people reached the
    island, but several centuries too late to explain it. And in 2024, twenty-one genomes
    gave the case its strangest turn: a population that crashed to eight or fewer, then
    recovered to hundreds, and stayed small for thousands of years without collapsing.

    What the film refuses to do is pick the most dramatic clue and call it solved. Each
    witness is asked what it can actually support, what remains plausible, and what is
    still missing. The last ten generations — roughly three centuries — are absent from the
    genome record. That gap is the real subject of this film.

    CHAPTERS
    00:00 A mammoth with a mystery in its DNA
    00:58 Four witnesses
    01:26 The island nobody left
    02:52 Witness one: the genome
    05:05 Witness two: chemistry
    06:31 Witness three: humans
    07:38 Witness four: the larger genome study
    10:29 The missing witness
    11:29 The verdict
    12:40 What the evidence still cannot say

    SOURCES AND LIMITS
    Every claim is drawn from published genome, isotope and archaeological work on the
    Wrangel Island population — the 2017 genome comparison, the 2019 isotope study, the
    archaeological record, and the 2024 twenty-one-genome study, plus 2025 work on ancient
    microbial DNA. The animals you see are reconstructions, not recovered footage, and each
    shot is labelled on screen. Where the science is still arguing, the film says so out
    loud. Where it is not, the film shows its working.

    Corrections welcome: <address>

    CREDITS
    Mammoth 3D model: "3D High-poly Baby Woolly Mammoth" by SDPM Esare, licensed CC BY 4.0
    (https://creativecommons.org/licenses/by/4.0/). Modified for this film: rigged, re-skinned
    and re-animated; the original model has no armature. The model's title says "Baby", but its
    tusks and proportions do not reliably establish an age, and it is not presented as a
    documented calf or an actual Wrangel specimen.


---

## TAGS

    woolly mammoth, last mammoths, wrangel island, mammoth extinction, what killed the
    mammoths, mammoth dna, ancient dna, pleistocene, ice age animals, extinct animals,
    mammoth documentary, wrangel island mammoths, mammoth genome, prehistoric animals,
    megafauna extinction, holocene extinction, arctic history, mammoth 2024, mammoth
    genetics, cold case science, last ice age

---

## HASHTAGS

Three, above the fold. More than three and YouTube ignores all but the first three shown.

    #mammoth #wrangelisland #ancientDNA

---

## PINNED COMMENT

    Eight. That is the modelled effective population size the 2024 study lands on at the
    bottleneck — and then it recovers to a couple of hundred within about twenty
    generations. Effective size is a genetic estimate, not a head count, and the film is
    careful about that distinction. But sit with the shape of it: a herd that small, that
    isolated, holding on for thousands of years.

    So what actually ends it — the last bad season, or the six thousand quiet ones before
    it? Our answer is at 11:29, and it is not the answer the thumbnail promises. Tell us
    yours.

---

## CAPTIONS

`full-script-v2/English-reel-v2.srt` — 287 cues, covers 00:00–13:11.

Machine-aligned draft (PocketSphinx), **not human-verified**. The repo's
`longform-mammoth/full-film/English.srt` is for the older narration and does **not** match
this cut — do not upload it.

---

## BEFORE YOU PUBLISH

- [ ] Advanced Features enabled and account verified — otherwise Test & Compare is not offered
- [ ] Test configured **on desktop**, not the mobile Studio app
- [ ] All three thumbnails uploaded from `upload-1920/` (a 720p variant silently degrades the whole test)
- [ ] Slot 1 is the package you would be happy to keep, because inconclusive is the likely outcome
- [ ] Captions reviewed by a human, not just force-aligned
- [ ] `<address>` replaced with a real contact
- [ ] Confirm the cut is still 13:16 / four witnesses; if not, re-run `edit/validate_metadata.py`
- [ ] Rig rights resolved — nothing here authorises distribution
- [ ] After the test: write the result, including *Inconclusive*, into `../youtube-v14/EXPERIMENT-LOG.csv`

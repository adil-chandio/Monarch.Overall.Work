# V12 - ONE-PAGE HUMAN REVIEWER CHECKLIST

> **Ye ek hi page aapko bharna hai.** Iske baad recording/edit shuru ho sakta hai. Agent ye fields khud **nahi** bhar sakta — inme se har ek ko insaan ne verify karna hai. **Ye legal advice nahi** (`not_a_legal_opinion=true`).

**Video:** `MC-01 THE REPLAY CODE: 8 Moments, One Hidden Rule` · 10:00 · 8 DIFFERENT clips · source share <=13.3% · V10/Short asset `art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman` **EXCLUDED**

**Reviewer:** ____________________  **Date:** __________  **Overall decision:** ☐ APPROVE  ☐ REJECT  ☐ REVISE

---

## A. Har clip ke liye 18 fields (har row me tick + value)

| # | Field | Kya likhna hai |
| --- | --- | --- |
| 1 | official_source_url | ☐ verified  →  value: ____________________________________ |
| 2 | nasa_or_agency_asset_id | ☐ verified  →  value: ____________________________________ |
| 3 | licence_basis | ☐ verified  →  value: ____________________________________ |
| 4 | third_party_copyrighted_material_check | ☐ verified  →  value: ____________________________________ |
| 5 | identifiable_persons_check | ☐ verified  →  value: ____________________________________ |
| 6 | current_astronaut_or_employee_check | ☐ verified  →  value: ____________________________________ |
| 7 | promotional_or_cover_art_use | ☐ verified  →  value: ____________________________________ |
| 8 | native_audio_rights | ☐ verified  →  value: ____________________________________ |
| 9 | attribution_string | ☐ verified  →  value: ____________________________________ |
| 10 | no_endorsement_implied_wording | ☐ verified  →  value: ____________________________________ |
| 11 | no_insignia_confirmed | ☐ verified  →  value: ____________________________________ |
| 12 | sha256_after_download | ☐ verified  →  value: ____________________________________ |
| 13 | duration_seconds | ☐ verified  →  value: ____________________________________ |
| 14 | scout_score_out_of_100 | ☐ verified  →  value: ____________________________________ |
| 15 | scout_min_pass_78 | ☐ verified  →  value: ____________________________________ |
| 16 | clearance_status | ☐ verified  →  value: ____________________________________ |
| 17 | human_legal_review | ☐ verified  →  value: ____________________________________ |
| 18 | not_a_legal_opinion | ☐ verified  →  value: ____________________________________ |

## B. 8 slots - ek line har clip

| Slot | Analytic job | Official source URL / asset ID | Licence basis | SHA-256 | Duration | Score >=78 | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | expectation violation | ________________ | ____________ | ____________ | ____s | ☐ | ☐ OK / ☐ NO |
| 2 | physics / optics surprise | ________________ | ____________ | ____________ | ____s | ☐ | ☐ OK / ☐ NO |
| 3 | timing / slow-motion frame | ________________ | ____________ | ____________ | ____s | ☐ | ☐ OK / ☐ NO |
| 4 | scale / size illusion | ________________ | ____________ | ____________ | ____s | ☐ | ☐ OK / ☐ NO |
| 5 | native sound vs silence | ________________ | ____________ | ____________ | ____s | ☐ | ☐ OK / ☐ NO |
| 6 | human reaction beat | ________________ | ____________ | ____________ | ____s | ☐ | ☐ OK / ☐ NO |
| 7 | near-miss / coincidence | ________________ | ____________ | ____________ | ____s | ☐ | ☐ OK / ☐ NO |
| 8 | prediction test / callback | ________________ | ____________ | ____________ | ____s | ☐ | ☐ OK / ☐ NO |

## C. Kill conditions - koi ek bhi mila to slot REJECT

- ☐ checked / ☐ not applicable — Current named crew / employee in promotional framing or an official mission broadcast used as a source clip.
- ☐ checked / ☐ not applicable — Agency insignia, mission patch, or logo visible in the selected frames.
- ☐ checked / ☐ not applicable — Native audio or music retained without its own documented rights basis.
- ☐ checked / ☐ not applicable — Asset obtained from a social repost, mirror, aggregator or embed instead of the rights holder.
- ☐ checked / ☐ not applicable — Licence cannot be read for this exact file, or excludes commercial use while monetization is intended.
- ☐ checked / ☐ not applicable — The V10/Short NASA water-bubble asset (any hero, callback, montage or whole-video use).
- ☐ checked / ☐ not applicable — Any clip that would make the 8-source aggregate exceed 80s / 600s (13.3%).
- ☐ checked / ☐ not applicable — Clips strung together with little or no narrative, or a mostly non-verbal reaction.

## D. Sign-off

```text
reviewer_name : ____________________________
review_date   : ____________________________
decision      : APPROVE | REJECT | REVISE
notes         : ____________________________
not_a_legal_opinion : true
```

> **Rule:** `clearance_status='cleared'` sirf tab jab **sab 18 fields verified**, `human_legal_review=true`, aur upar sign-off me naam + tareekh + decision ho. `render_pipeline_v12.py` ye khud check karta hai aur warna **BLOCKED** deta hai.

---

**Yaad:** Public upload + monetization ON par likhit clearance, identifiable-person permission aur human legal review chahiye. Uploaded V10 Short ka monetization OFF karna abhi bhi pending hai. Koi guaranteed views / retention / virality / perfection ka dawa nahi.


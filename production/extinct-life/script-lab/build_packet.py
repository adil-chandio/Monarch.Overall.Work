"""Build original review documents and honest machine-checkable scope metrics."""
import hashlib,json,re
from pathlib import Path
ROOT=Path.cwd();LAB=ROOT/'production/extinct-life/script-lab';F=ROOT/'docs/research/extinct-script-forensics'
s=json.loads((LAB/'master-v2.json').read_text());chap=s['chapters'];wc=lambda t:len(t.split())
ALIGN=[
('B01','Mastodon trace, northern Greenland, 2022 and roughly two million years; not a skeleton; both opening questions; earlier plant clues.','بیس لاکھ = two million; DNA trace remains the discovery, not a body.'),
('B02','Shedding/decay/transport; mixed environmental DNA; shredded-guide analogy; no inferred neighbours; DNA breakdown.','Natural sentence shapes differ; no extra encounter or single-animal archive is introduced.'),
('B03','Information loss; long cold conditions; binding may protect; binding can hinder extraction; illustrative close-up; surviving fraction.','Can/may remain qualified; no immortal mineral vault.'),
('B04','Extraction/read/reference comparison; short-read ambiguity; uneven references; contamination; illustrative display; characteristic damage helps test age.','The English distinction between an authentication aid and proof is preserved.'),
('B05','Same animal groups/plants; no simple modern habitat copy; earlier plant evidence; no exact colour/size/behaviour.','Mastodon lineage remains a lineage; it does not become a mammoth.'),
('B06','Same imagined giant/tree/goose action; transport/time mixing; missing DNA not proof of absence; preservation/sample/reference filters.','The scene is imagined, not an event claimed from the sample.'),
('B07','Multiple evidence routes; DNA-only plant detections; method blind spots; approximate geological age; not a total inventory.','The approximate two-million-year scale is not turned into an exact date.'),
('B08','No waiting frozen body or complete genome; partly readable community; reconstruction/evidence distinction; nonliteral memory; same identity ending.','No resurrection promise or added call to action.')]
assert len(chap)==8 and [c['id'] for c in chap]==[f'B{i:02}' for i in range(1,9)]
assert all(c['en'] and c['ur'] and c['claim_ids'] and c['visual_action'] and c['visual_boundary'] for c in chap)
claims=set(re.findall(r'\| (C\d\d) \|',(LAB/'SCIENCE-LEDGER.md').read_text()))
assert all(set(c['claim_ids'])<=claims for c in chap)
assert sum('mastodon' in c['en'].lower() for c in chap)>0
assert chap[0]['en'].split()[1].lower()=='mastodon'
assert '2022' in chap[0]['en'] and '2022' in chap[0]['ur']
assert 'بیس لاکھ' in chap[0]['ur'] and 'بیس لاکھ' in chap[6]['ur']
# Human editorial review record, not automatic certification of translation quality.
header=f'# {s["title"]}\n\n## English master v2\n\n**Original narration:** {sum(wc(c["en"]) for c in chap):,} whitespace-token words. Block titles are not spoken. This is a complete script draft, not a finished film. Eight IDs are production handles, not eight hard cuts or equal-duration scenes.\n'
(LAB/'ENGLISH-MASTER-v2.md').write_text(header+'\n\n'.join(f'### {c["id"]} — {c["title"]}\n\n{c["en"]}' for c in chap)+'\n')
review=['# Owner review — the same English master in easy Urdu-English','\n**Version:** '+s['version'],'\nEnglish is canonical. Each Urdu-English passage translates the same narrative in the same order; it is not a second script. Urdu appears in Urdu script with familiar English technical terms. Headings/production notes are not narration.','\n**Timing:** fresh v2 English and Urdu audio have not been generated or measured. Old clips do not match this rewrite. Do not use old durations, stretch narration or claim a measured 6–8-minute translated version.','\n**Review status:** author semantic pass completed using the alignment table below; no independent bilingual reviewer or cold-listener test yet. Automated checks only verify structural/numerical anchors.']
for c in chap:
 review.extend([f'\n## {c["id"]} — {c["title"]}',f'\n### English\n\n{c["en"]}',f'\n### Same passage — easy Urdu-English\n\n{c["ur"]}',f'\n**Visible action required:** {c["visual_action"]}',f'\n**Do not imply:** {c["visual_boundary"]}'])
review.extend(['\n## Translation alignment audit','\nThis is a manual author review, not a claim that a computer certified semantic equivalence.','\n| Pair | Preserved content | Important translation boundary |','|---|---|---|'])
review.extend('| '+' | '.join(row)+' |' for row in ALIGN)
review.extend(['\n## What to judge in the cold read','\n1. Can you explain what was actually found after the opening?\n2. Does each explanation answer the question you were asking?\n3. Do B04 and B06–B07 become too technical or repetitive?\n4. Do the Urdu qualifiers sound natural without changing the English science?\n5. Does the ending feel like the answer to the beginning, rather than another introduction?','\nNo claim of guaranteed engagement or completed audiovisual quality is made. Approved 3D style remains locked; the existing render hold prevents an unreviewed old script from continuing.'])
(LAB/'OWNER-REVIEW-v2.md').write_text('\n'.join(review)+'\n')
first_three=' '.join(re.split(r'(?<=[.!?])\s+',chap[0]['en'])[:3]);total=sum(wc(c['en']) for c in chap)
validation={'version':s['version'],'english_words_whitespace':total,'chapters':[{'id':c['id'],'english_words':wc(c['en']),'urdu_whitespace_tokens_not_comparable_to_english_words':wc(c['ur']),'claim_ids':c['claim_ids']} for c in chap],'first_three_sentences_words':wc(first_three),'first_mastodon_english_word_position':2,'english_speech_only_estimate_seconds_at_160wpm':round(total/160*60,2),'english_speech_only_estimate_seconds_at_140wpm':round(total/140*60,2),'measured_v2_english_audio_seconds':None,'measured_v2_urdu_audio_seconds':None,'independent_translation_review':False,'finished_film_review':False,'automated_checks':['8 paired blocks with stable IDs','nonempty bilingual text and visual contracts','every claim ID in source ledger','mastodon at English word 2','2022 preserved in opening pair','two-million-year equivalent preserved in B01/B07'],'master_sha256':hashlib.sha256((LAB/'master-v2.json').read_bytes()).hexdigest()}
(LAB/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(validation,ensure_ascii=False,indent=2))

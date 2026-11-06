"""Generate v3 reading copies from the canonical paired master; never touch v2/audio."""
import hashlib
import json
from pathlib import Path

LAB = Path(__file__).resolve().parent

def build():
    path = LAB / 'master-v3.json'
    data = json.loads(path.read_text())
    count = sum(len(c['en'].split()) for c in data['chapters'])
    intro = (f"# {data['title']}\n\n"
             f"**Original script v3 · English master · {count:,} spoken words**\n\n"
             "For a 6–8-minute English flagship. At 140–160 words/minute, the reading-rate estimate is "
             f"{count / 160:.2f}–{count / 140:.2f} minutes, before pauses. This is not measured narration. "
             "Section headings and notes are not spoken. No competitor wording is used as source narration.\n\n")
    english = intro
    review = (f"# {data['title']} — owner review v3\n\n"
              "**English is the master.** Har section ke neeche usi narration ka easy Urdu-English version hai; "
              "yeh alag kahani ya shorter summary nahi hai. Headings VO ka hissa nahi.\n\n"
              "English timing is a reading-rate estimate only. Urdu-English duration has not been measured; "
              "neither track will be stretched to fit an old timeline.\n\n")
    for c in data['chapters']:
        english += f"## {c['id']} — {c['title']}\n\n{c['en']}\n\n"
        review += f"## {c['id']} — {c['title']}\n\n### English master\n\n{c['en']}\n\n### Easy Urdu-English\n\n{c['ur']}\n\n"
    (LAB / 'ENGLISH-MASTER-v3.md').write_text(english)
    (LAB / 'OWNER-REVIEW-v3.md').write_text(review)
    validation = {
        'master_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'version': data['version'], 'english_words': count,
        'paired_blocks': len(data['chapters']),
        'planning_seconds_at_160_wpm': round(count / 160 * 60, 2),
        'planning_seconds_at_140_wpm': round(count / 140 * 60, 2),
        'measured_v3_english_audio_seconds': None,
        'measured_v3_urdu_audio_seconds': None,
        'translation_status': 'author-paired; not independently bilingual listener-tested',
        'cold_listener_tested': False, 'retention_effect_verified': False,
        'finished_film_review': False,
        'science_ledger': 'SCIENCE-LEDGER-v3.md; C01–C13 retain their source definitions in SCIENCE-LEDGER.md',
        'render_hold': True,
    }
    (LAB / 'validation-v3.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n')
    return validation

if __name__ == '__main__':
    print(json.dumps(build(), indent=2))

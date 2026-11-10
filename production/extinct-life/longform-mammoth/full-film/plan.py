"""Build the long-film timeline from the selected unsped voice takes.

Uses known-transcript forced alignment. The illustrations are generated assets
and procedural 3D, never documentary photographs or samples. Times are derived
from the audio itself rather than estimated word counts.
"""
import json, re, subprocess, wave
from pathlib import Path
import imageio_ffmpeg
from pocketsphinx import Decoder

B = Path(__file__).resolve().parent
R = B.parents[3]
CACHE = R / '.cache/longform-mammoth-full'
CACHE.mkdir(parents=True, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
DATA = json.loads((B.parent / 'FILM-VO.json').read_text())

# (cue phrase, visual treatment, background image, headline, detail)
# Cue phrases are matched to transcript word boundaries, not guessed durations.
VISUALS = {
 '01-island': [
  ('around ten thousand years ago', 'globe', 'arctic-island', 'WRANGEL ISLAND', 'Isolation begins · ~10,000 years ago'),
  ('other populations disappeared earlier', 'timeline', 'tundra', 'OTHER LAST POPULATIONS', 'East European plains · St. Paul Island'),
  ('on wrangel the story looked different', 'isotopes', 'bone-isotope', 'A DIFFERENT SIGNAL', 'Carbon + nitrogen · isotope evidence'),
  ('a population survived isolation', 'island', 'arctic-island', 'ISOLATED FOR MILLENNIA', 'The ending is still unresolved')],
 '02-genome-a': [
  ('our first witness is dna', 'dna', 'laboratory', 'WITNESS 01', 'THE 2017 GENOME STUDY'),
  ('one from mainland siberia', 'compare', 'fossil', 'TWO GENOMES', 'Mainland Siberia  ·  Wrangel Island'),
  ('the researchers interpreted the pattern', 'variants', 'laboratory', 'GENOMIC MELTDOWN?', 'A hypothesis from genetic patterns'),
  ('effective population size is a genetic estimate', 'population', 'arctic-island', 'EFFECTIVE POPULATION SIZE', 'A genetic estimate, not a headcount'),
  ('this was a striking warning sign', 'evidence', 'fossil', 'ONE GENOME', 'A powerful clue — not a final verdict')],
 '03-genome-b': [
  ('the wrangel genome had two independent', 'dna', 'laboratory', 'FOXQ1', 'Two predicted loss-of-function changes'),
  ('based on comparisons with other animals', 'coat', 'tundra', 'SATIN-LIKE COAT', 'Predicted phenotype · not directly observed'),
  ('think about the difference', 'evidence', 'fossil', 'MOLECULAR TRACE', 'A prediction is not a photograph'),
  ('in 2017 the genome offered', 'compare', 'laboratory', 'ONE GENOME → MANY', 'The question becomes more complex')],
 '04-environment': [
  ('the second witness is chemistry', 'isotopes', 'bone-isotope', 'WITNESS 02', 'CHEMISTRY IN BONE AND TEETH'),
  ('the wrangel carbon and nitrogen values', 'chart', 'bone-isotope', 'BROADLY STABLE', 'Dietary isotope signals in sampled remains'),
  ('the team also found sulfur', 'water', 'tundra', 'ROCK → WATER?', 'Possible water-quality change'),
  ('then there is a possible sudden threat', 'ice', 'ice-storm', 'RAIN ON SNOW', 'An icing event is a hypothesis'),
  ('ice water and genetic strain', 'evidence', 'ice-storm', 'A PLAUSIBLE SCENARIO', 'Not an observed fatal winter')],
 '05-humans': [
  ('the third witness is us', 'archaeology', 'archaeology', 'WITNESS 03', 'THE HUMAN TIMELINE'),
  ('the earliest known archaeological evidence', 'timeline', 'archaeology', 'EARLIEST KNOWN EVIDENCE', 'Humans · ~3,600 calibrated years BP'),
  ('that is the earliest evidence we have', 'evidence', 'archaeology', 'EVIDENCE IS NOT ARRIVAL', 'An earlier visit cannot be ruled out'),
  ('so the distinction is important', 'compare', 'arctic-island', 'POSSIBLE ≠ PROVEN', 'A suspect is not a verdict')],
 '06-genomes-a': [
  ('in 2024 the fourth witness arrived', 'dna', 'laboratory', 'WITNESS 04', '21 GENOMES · 2024'),
  ('the bottleneck was real', 'bars', 'laboratory', 'DIVERSITY FELL', 'Heterozygosity · more than 40% lower'),
  ('long runs of homozygosity', 'bars', 'bone-isotope', 'HOMOZYGOSITY ROSE', 'Approximately 10% → 42%'),
  ('diversity in the major histocompatibility complex', 'cells', 'microbes', 'IMMUNE GENE DIVERSITY', 'Greater reduction than genome-wide'),
  ('modelling suggested that effective population', 'population', 'arctic-island', 'BOTTLENECK → RECOVERY', 'Modelled effective population size'),
  ('again that is an effective genetic', 'evidence', 'tundra', 'A GENETIC ESTIMATE', 'Not a count of individual animals')],
 '07-genomes-b': [
  ('recovery did not erase', 'dna', 'laboratory', 'RECOVERY ≠ RESET', 'Long-lasting genetic strain'),
  ('imagine comparing damage', 'windows', 'laboratory', 'TWO WINDOWS', 'Coverage affects what can be measured'),
  ('after accounting for coverage', 'variants', 'laboratory', 'HIGH-IMPACT VARIANTS', 'Evidence consistent with purging'),
  ('meanwhile moderately harmful variants', 'variants', 'laboratory', 'MODERATE-IMPACT VARIANTS', 'Accumulation consistent with drift'),
  ('across the sampled history', 'chart', 'arctic-island', 'STABLE IN THE SAMPLES', 'The final generations are not represented')],
 '08-missing': [
  ('here is the missing witness', 'missing', 'fossil', 'THE MISSING WITNESS', 'No genomes from the final ten generations'),
  ('we can study the long setup', 'timeline', 'arctic-island', 'A GAP IN THE GENOMES', 'Not an absence of all other evidence'),
  ('there is also a newer kind of lead', 'cells', 'microbes', 'THE MICROBIAL RECORD', '483 specimens · research published 2025'),
  ('some bacteria were related to known pathogens', 'microbe', 'microbes', 'RELATED ≠ RESPONSIBLE', 'No identified Wrangel extinction cause'),
  ('the value of this research', 'dna', 'laboratory', 'A NEW WAY TO ASK', 'Authentication · contamination control')],
 '09-verdict': [
  ('so what can we actually say', 'verdict', 'laboratory', 'THE VERDICT', 'Separate evidence from inference'),
  ('supported the wrangel population', 'verdict', 'arctic-island', 'SUPPORTED', 'Bottleneck · recovery · genetic strain'),
  ('plausible not proven', 'ice', 'ice-storm', 'PLAUSIBLE · NOT PROVEN', 'Icing · disease · water · humans'),
  ('not established a single named killer', 'missing', 'fossil', 'NOT ESTABLISHED', 'No identified single cause'),
  ('these categories are not rivals', 'compare', 'tundra', 'COMPOUNDING RISKS', 'A hypothesis, not a proven ending')],
 '10-ending': [
  ('each witness tells us something different', 'evidence', 'fossil', 'FOUR WITNESSES', 'Different evidence · one open case'),
  ('the mistake would be to pick', 'compare', 'laboratory', 'A CLUE IS NOT A CAUSE', 'Plausibility is not proof'),
  ('the same distinction matters', 'population', 'tundra', 'A LESSON FOR TODAY', 'Recovery does not erase every risk'),
  ('for the last wrangel mammoths', 'island', 'arctic-island', 'THE LAST MAMMOTHS', 'The final chapter remains uncertain')],
}

PRON = {
 'wrangel':'R AE NG G AH L', 'genomes':'JH IY N OW M Z', 'genomic':'JH IY N AA M IH K',
 "mammoth's":"M AE M AH TH S", "population's":"P AA P Y AH L EY SH AH N Z",
 'heterozygosity':'HH EH T ER OW Z AY G AA S AH T IY',
 'homozygosity':'HH OW M OW Z AY G AA S AH T IY',
 'histocompatibility':'HH IH S T OW K AH M P AE T AH B IH L AH T IY',
 'modelled':'M AA D AH L D',
}
def tokens(text):
 return re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower())

def align(seg):
 path=B/'source'/f"{seg['id']}.mp3"
 raw=subprocess.run([FF,'-v','error','-i',str(path),'-ar','16000','-ac','1','-f','s16le','-'],capture_output=True,check=True).stdout
 words=tokens(seg['text']); d=Decoder(samprate=16000,loglevel='ERROR')
 for w,p in PRON.items():
  if not d.lookup_word(w): d.add_word(w,p,False)
 missing=sorted({w for w in words if not d.lookup_word(w)})
 if missing: raise ValueError(f"{seg['id']} missing pronunciations: {missing}")
 d.set_align_text(' '.join(words));d.start_utt();d.process_raw(raw,False,True);d.end_utt()
 segments=[x for x in d.seg() if not x.word.startswith('<')]
 got=[re.sub(r'\(\d+\)$','',x.word).lower() for x in segments]
 if got != words: raise ValueError(f"Alignment mismatch in {seg['id']}: {len(got)} != {len(words)}")
 aligned=[{'word': w,'start': x.start_frame/100,'end': (x.end_frame+1)/100} for w,x in zip(words,segments)]
 return len(raw)/2/16000, aligned

def find(words, phrase):
 want=tokens(phrase); ws=[w['word'] for w in words]
 for i in range(len(ws)-len(want)+1):
  if ws[i:i+len(want)] == want: return words[i]['start']
 raise ValueError(f'Cue not found: {phrase}')

def make_cues(seg, words, offset):
 # Preserve punctuation and casing from the actual script while grouping by phrase.
 matches=list(re.finditer(r"[A-Za-z]+(?:'[A-Za-z]+)?",seg['text']))
 assert len(matches)==len(words)
 cues=[]; i=0
 while i<len(words):
  j=min(i+7,len(words))
  for k in range(i+3,j):
   tail=seg['text'][matches[k].end():matches[k+1].start()] if k+1<len(matches) else '.'
   if any(c in tail for c in '.!?;:\n'): j=k+1; break
  start,end=matches[i].start(), matches[j-1].end()
  punct=seg['text'][end:matches[j].start() if j<len(matches) else len(seg['text'])]
  m=re.match(r"[.,!?;:]",punct)
  if m: end+=1
  text=seg['text'][start:end].replace('\n',' ').strip()
  cues.append({'start':round(offset+words[i]['start'],3), 'end':round(offset+words[j-1]['end'],3), 'text':text})
  i=j
 return cues

def main():
 t=60.35; shots=[]; captions=[]; chapters=[]
 for segment in DATA['segments']:
  dur,words=align(segment)
  cues=make_cues(segment,words,t); captions.extend(cues)
  definitions=VISUALS[segment['id']]
  starts=[t+find(words, x[0]) for x in definitions]
  starts[0]=t
  if starts!=sorted(starts): raise ValueError('Cue order error '+segment['id'])
  for i,(phrase,kind,bg,title,detail) in enumerate(definitions):
   end=starts[i+1] if i+1<len(starts) else t+dur+0.8
   shots.append({'id':f"{segment['id']}-{i}",'start':round(starts[i],3),'end':round(end,3),'kind':kind,'background':bg,'title':title,'detail':detail})
  chapters.append({'id':segment['id'],'title':segment['chapter'],'start':round(t,3),'duration':round(dur,3),'end':round(t+dur,3)})
  t+=dur+0.8
 # Stretch opening of first chapter to the 60s transition and close gaps between chapters.
 shots[0]['start']=60.0
 for a,b in zip(shots,shots[1:]): a['end']=b['start']
 duration=round(t+5.2,3); shots[-1]['end']=duration
 plan={'duration':duration,'fps':30,'opening_seconds':60,'chapters':chapters,'shots':shots,'captions':captions,
       'caption_method':'PocketSphinx forced alignment against known transcript; automatic timing estimates',
       'visual_provenance':'AI-generated background illustrations, original procedural three-dimensional graphics and the earlier procedural 3D opening.'}
 (B/'timeline.json').write_text(json.dumps(plan,indent=2)+'\n')
 print(f"duration={duration:.2f}s chapters={len(chapters)} shots={len(shots)} captions={len(captions)}")
 for c in chapters:print(c['id'],c['start'],c['end'])
if __name__=='__main__': main()

"""Time a *planned* 3D shot breakdown to the full-story narration takes.

No imagery is rendered by this tool. Captions and shot timings use automatic
known-transcript alignment and require human review against the actual audio.
"""
import json, re, subprocess
from pathlib import Path
import imageio_ffmpeg
from pocketsphinx import Decoder

B=Path(__file__).resolve().parent
S=json.loads((B/'narration.json').read_text())
T=json.loads((B/'take-timeline.json').read_text())
ff=imageio_ffmpeg.get_ffmpeg_exe()
PRON={'wrangel':'R AE NG G AH L', "wrangel's":'R AE NG G AH L Z',
      'genomes':'JH IY N OW M Z', 'genomic':'JH IY N AA M IH K',
      "mammoth's":'M AE M AH TH S', "population's":'P AA P Y AH L EY SH AH N Z',
      'heterozygosity':'HH EH T ER OW Z AY G AA S AH T IY',
      'homozygosity':'HH OW M OW Z AY G AA S AH T IY',
      'histocompatibility':'HH IH S T OW K AH M P AE T AH B IH L AH T IY',
      'modelled':'M AA D AH L D', 'favourable':'F EY V ER AH B AH L'}
# Each planned beat describes a moving 3D reconstruction or investigation, not a slide.
# These are creative requirements, NOT existing models or completed animation.
VISUALS={
 '01-opening':[
  ('here is a mammoth','Arctic','Low tracking approach to a moving herd; fog and snow respond to wind.'),
  ('two changes in a gene','macro','Travel from an intact coat into a stylized molecular reconstruction; phenotype remains unconfirmed.'),
  ('now the strange part','lab','Move from specimen to time-spanning DNA samples; distinguish 2017 from later research.'),
  ('this story comes from evidence','lab','Continuous movement across physical specimen, sample and archaeology props.'),
  ('so how did a population','Arctic','Return to moving landscape and animals; avoid a fabricated death event.'),
  ('we have four witnesses','lab','Camera visits four distinct physical evidence stations; no static cards.')],
 '02-island':[
  ('around ten thousand years ago','Arctic','Aerial reconstructed coastline and changing sea level, explicitly compressed in time.'),
  ('other populations disappeared earlier','map','Move across animated topographic Arctic map; mark locations without invented migration routes.'),
  ('on the east european plains','map','Transition through European plains and St. Paul environments using animated geography.'),
  ('picture an island population','Arctic','Track moving animals within an isolated tundra landscape.'),
  ('wrangel\'s sampled bones offered','lab','Bone cross-section moves to isotope testing; samples, not a complete timeline.')],
 '03-genome':[
  ('the first witness is dna','lab','Gloved handling of two specimens, preparation and sequencing.'),
  ('the island genome carried','molecular','Move through DNA showing schematic deletions and stop changes.'),
  ('the estimated effective population size','molecular','Show genetic genealogy as a model, never literal herd headcount.'),
  ('a premature stop','molecular','Protein assembly reconstruction pauses at a stop signal; illustration, not observed molecular footage.'),
  ('the researchers interpreted','lab','Contrast small-population hypothesis with the limited sampled evidence.')],
 '04-coat':[
  ('the wrangel mammoth\'s genome','molecular','Sequence and FOXQ1 location, with two indicated changes.'),
  ('from comparisons with other animals','macro','Compare animated hair structures as hypothetical models, never a hair-loss claim.'),
  ('that difference between a molecular trace','lab','Move between sample and computational inference, not a photograph of the animal.'),
  ('that distinction is easy to lose','Arctic','Return to a normal woolled animal; the predicted individual phenotype is uncertain.'),
  ('seven years later','lab','More samples enter view as preparation for the larger study.')],
 '05-environment':[
  ('the second witness is chemistry','lab','Animate extraction and analysis of bone collagen.'),
  ('the wrangel carbon and nitrogen','lab','Show measured samples in context, avoiding fabricated continuous data.'),
  ('isotope measurements are records','Arctic','Seasonal environment variation and sparse, discrete evidence contrasted.'),
  ('sulfur and strontium patterns','watershed','Rock weathering and water flow as a labelled possible mechanism.'),
  ('they also proposed a rapid threat','weather','Rain freezes on snow over vegetation; explicitly hypothetical.'),
  ('but no one observed','lab','Return to physical evidence; no claim of a witnessed fatal winter.')],
 '06-humans':[
  ('the third witness is us','archaeology','Animated examination of a reconstructed archaeological site.'),
  ('the earliest known archaeological evidence','map','Move through dated remains and site evidence on an animated spatial chronology.'),
  ('the earliest evidence is not necessarily','archaeology','Show incomplete archaeological layers without implying an earlier visit occurred.'),
  ('elsewhere archaeological finds','archaeology','Separate other locations from Wrangel; do not stage a claimed island encounter.'),
  ('so human involvement is possible','Arctic','An unoccupied coast and the uncertainty of the historical record.')],
 '07-genomes-a':[
  ('in 2024 researchers published','lab','Samples collected across times and locations enter a sequencing workflow.'),
  ('the bottleneck was severe','molecular','Animate diversity falling as a schematic representation tied to sourced values.'),
  ('long runs of homozygosity','molecular','Aligned inherited DNA copies show longer matching regions.'),
  ('diversity in the major histocompatibility','molecular','Focus on immune gene diversity; do not depict a proven disease.'),
  ('then came the surprise','molecular','Genealogical model expands after bottleneck; effective size is not a herd count.'),
  ('across the years represented','lab','Move along samples with visible sampling gaps.')],
 '08-genomes-b':[
  ('diversity and homozygosity','molecular','Variants in a reconstructed sequence, labelled as predictions.'),
  ('imagine looking into the same room','lab','A 3D room is viewed through moving apertures as an explicitly labelled analogy.'),
  ('the comparison matters','lab','Researchers assess read coverage on distinct samples.'),
  ('after accounting for these differences','molecular','High-impact predicted variants become less common through the sample timeline.'),
  ('moderately harmful variants accumulated','molecular','Distinct category shows the opposite trend, with no fictional individual diagnosis.'),
  ('the sampled genomes did not show','lab','Samples end before final generations; no claim of a complete record.')],
 '09-missing':[
  ('here is the missing witness','lab','Follow sampled genomes into an incomplete interval.'),
  ('that gap is in the genomic dataset','lab','Other kinds of evidence remain visible beyond the gap.'),
  ('in 2025 researchers studied','lab','Multiple ancient specimens and sterile microbiology sampling.'),
  ('some bacteria were related','microscopic','Animate abstract microbial lineages, not a witnessed infection.'),
  ('related does not mean responsible','lab','Visual comparison without presenting an identified cause.'),
  ('authentication contamination control','lab','Process controls show how researchers validate ancient DNA.')],
 '10-verdict':[
  ('what can we say','lab','Revisit physical evidence stations and the limits of each.'),
  ('supported the island population','molecular','Follow genetic model and sample evidence through time.'),
  ('plausible not proven','weather','Brief distinctly hypothetical environment and microbial vignettes.'),
  ('not established','lab','Return to the missing interval and absent causal evidence.'),
  ('a possibility is not a verdict','Arctic','Contrast reconstruction with the uncertain record; no fabricated ending.'),
  ('these categories do not have to compete','Arctic','Illustrative pressures coexist without asserting they occurred together.'),
  ('for small isolated populations','conservation','Generic connected habitat and animal movement; no unverified case study.'),
  ('for the wrangel mammoths','Arctic','Moving animal and weather in a landscape; finish with sources and uncertainty.')]
}

def tokens(s):return re.findall(r"[a-z]+(?:'[a-z]+)?",s.lower())
def find(ws,phrase):
    want=tokens(phrase); names=[x['word'] for x in ws]
    for i in range(len(names)-len(want)+1):
        if names[i:i+len(want)]==want:return ws[i]['start']
    raise ValueError('anchor not found: '+phrase)
def stamp(s):
    ms=round(max(0,s)*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);ss,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{ss:02},{ms:03}'

shots=[];cues=[]
for sec,take in zip(S['sections'],T['sections']):
    assert sec['id']==take['id']
    raw=subprocess.run([ff,'-v','error','-i',str(B/(sec['id']+'.mp3')),'-ar','16000','-ac','1','-f','s16le','-'],check=True,capture_output=True).stdout
    words=tokens(sec['text']); d=Decoder(samprate=16000,loglevel='ERROR')
    for w,p in PRON.items():
        if not d.lookup_word(w):d.add_word(w,p,False)
    missing=sorted({w for w in words if not d.lookup_word(w)})
    if missing:raise ValueError(f"Unknown pronunciations: {missing}")
    d.set_align_text(' '.join(words));d.start_utt();d.process_raw(raw,False,True);d.end_utt()
    matches=[x for x in d.seg() if not x.word.startswith('<')]
    got=[re.sub(r'\(\d+\)$','',x.word).lower() for x in matches]
    if got != words:raise ValueError(f"Alignment mismatch: {sec['id']}")
    aligned=[{'word':w,'start':x.start_frame/100,'end':(x.end_frame+1)/100} for w,x in zip(words,matches)]
    starts=[take['start']+find(aligned,v[0]) for v in VISUALS[sec['id']]]
    if starts!=sorted(starts):raise ValueError('anchor order '+sec['id'])
    for n,(anchor,set_name,action) in enumerate(VISUALS[sec['id']]):
        shots.append({'id':sec['id']+'-'+str(n+1),'start':round(starts[n],3),'anchor':anchor,'environment':set_name,'action':action,'status':'planned, not rendered'})
    matches=list(re.finditer(r"[A-Za-z]+(?:'[A-Za-z]+)?",sec['text']))
    assert len(matches)==len(aligned)
    i=0
    while i<len(aligned):
        j=min(i+7,len(aligned))
        for k in range(i+3,j):
            tail=sec['text'][matches[k].end():matches[k+1].start()] if k+1<len(matches) else '.'
            if any(c in tail for c in '.!?;:\n'):j=k+1;break
        end=matches[j-1].end();punc=sec['text'][end:matches[j].start() if j<len(matches) else len(sec['text'])]
        if re.match(r'[.,!?;:]',punc):end+=1
        text=sec['text'][matches[i].start():end].replace('\n',' ').strip()
        cues.append({'start':round(take['start']+aligned[i]['start'],3),'end':round(take['start']+aligned[j-1]['end'],3),'text':text})
        i=j
    print(sec['id'],'aligned words',len(words),flush=True)
for a,b in zip(shots,shots[1:]):a['end']=b['start']
shots[-1]['end']=T['duration_seconds']
result={'duration_seconds':T['duration_seconds'],'caption_method':'PocketSphinx forced alignment: automatic estimates, not human verified','rendered':False,'shots':shots,'captions':cues}
(B/'planned-shots.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
(B/'English-auto.srt').write_text('\n'.join(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}\n" for i,c in enumerate(cues,1)))
print('planned shots',len(shots),'automatic captions',len(cues),'duration seconds',T['duration_seconds'])

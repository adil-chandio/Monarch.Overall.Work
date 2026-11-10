"""Generate approximate captions for the draft narration. Requires human review.

Digits are expanded to spoken words for alignment, while the caption retains the
original typography. Previously excluding digits from the alignment gave spoken
years no time of their own, even when they appeared inside the caption text.
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
NUMBERS={'2017':['twenty','seventeen'], '2019':['twenty','nineteen'],
         '2024':['twenty','twenty','four'], '2025':['twenty','twenty','five']}
TOKEN=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+")
def stamp(s):
    ms=round(max(0,s)*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);ss,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{ss:02},{ms:03}'

cues=[]
for sec,take in zip(S['sections'],T['sections']):
    assert sec['id']==take['id']
    raw=subprocess.run([ff,'-v','error','-i',str(B/(sec['id']+'.mp3')),'-ar','16000','-ac','1','-f','s16le','-'],check=True,capture_output=True).stdout
    display=list(TOKEN.finditer(sec['text']))
    words=[]; spans=[]
    for match in display:
        token=match.group().lower(); start=len(words)
        if token.isdigit():
            if token not in NUMBERS:raise ValueError(f'Unconfigured spoken number: {token}')
            words.extend(NUMBERS[token])
        else: words.append(token)
        spans.append((start,len(words)))
    d=Decoder(samprate=16000,loglevel='ERROR')
    for w,p in PRON.items():
        if not d.lookup_word(w):d.add_word(w,p,False)
    missing=sorted({w for w in words if not d.lookup_word(w)})
    if missing:raise ValueError(f"Unknown pronunciations: {missing}")
    d.set_align_text(' '.join(words));d.start_utt();d.process_raw(raw,False,True);d.end_utt()
    seg=[x for x in d.seg() if not x.word.startswith('<')]
    got=[re.sub(r'\(\d+\)$','',x.word).lower() for x in seg]
    if got != words:raise ValueError(f"Alignment mismatch: {sec['id']}")
    aligned=[{'start':seg[a].start_frame/100,'end':(seg[b-1].end_frame+1)/100} for a,b in spans]
    i=0
    while i<len(aligned):
        j=min(i+7,len(aligned))
        for k in range(i+3,j):
            tail=sec['text'][display[k].end():display[k+1].start()] if k+1<len(display) else '.'
            if any(c in tail for c in '.!?;:\n'):j=k+1;break
        end=display[j-1].end();punc=sec['text'][end:display[j].start() if j<len(display) else len(sec['text'])]
        if re.match(r'[.,!?;:]',punc):end+=1
        text=sec['text'][display[i].start():end].replace('\n',' ').strip()
        cues.append({'start':round(take['start']+aligned[i]['start'],3),'end':round(take['start']+aligned[j-1]['end'],3),'text':text})
        i=j
    print(sec['id'],'aligned spoken tokens',len(words),'display tokens',len(display),flush=True)
result={'duration_seconds':T['duration_seconds'],'caption_method':'PocketSphinx forced alignment; year expansions assume twenty-seventeen etc; auto estimates, not human verified','captions':cues}
(B/'caption-data.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
(B/'English-auto.srt').write_text('\n'.join(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}\n" for i,c in enumerate(cues,1)))
print('automatic captions',len(cues),'duration seconds',T['duration_seconds'])

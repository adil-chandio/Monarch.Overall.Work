"""Build an unreviewed narration + licensed-score *draft*, not the final mix.

Three music excerpts crossfade in time; narration retains its original speed.
No background from the rejected opening is reused. No SFX are mixed because
picture/edit and spot timings are not locked. Source attributions in README.
"""
import hashlib,json,re,subprocess
from pathlib import Path
import imageio_ffmpeg
B=Path(__file__).resolve().parent;C=B.parent;ff=imageio_ffmpeg.get_ffmpeg_exe()
inputs=[C/'full-script-v2/Narration-Draft-v2.m4a',C/'music-sources/021_passage_of_time.m4a',C/'music-sources/017_beautiful_oblivion.m4a',C/'music-sources/005_a_kind_of_hope.m4a']
expected=['d0b35df690138d2d93338e3aa86dbc09208bdbdf7ac0fe376e19cd466e55e609','6669185b8a2a14cb2d14a89e0b95187216fd4cc4919612c7a534d0e7a646b90a','5497c4838e379ec31c2d91d678c594804779c647dfd408b61ea415a9bbd723f5','7ad67c0bd6869036dc2d8604ac408edda2b79a575c79af62010c11764c984151']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in zip(inputs,expected):assert p.exists() and sha(p)==h,(p,sha(p) if p.exists() else 'missing')
out=B/'Narration-Score-DRAFT.m4a'
filters=';'.join([
 '[0:a]aresample=48000,asetpts=PTS-STARTPTS[voice]',
 '[1:a]aresample=48000,atrim=duration=230,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=4,afade=t=out:st=222:d=8,volume=0.065[m1]',
 '[2:a]aresample=48000,atrim=duration=288,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=8,afade=t=out:st=280:d=8,volume=0.065,adelay=222000:all=1[m2]',
 '[3:a]aresample=48000,atrim=duration=294.1,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=8,afade=t=out:st=288.1:d=6,volume=0.065,adelay=502000:all=1[m3]',
 '[voice][m1][m2][m3]amix=inputs=4:duration=first:normalize=0:dropout_transition=0,loudnorm=I=-16:TP=-1.5:LRA=11:linear=false,aresample=48000[mix]'])
cmd=[ff,'-y','-v','error']
for p in inputs:cmd+=['-i',str(p)]
cmd+=['-filter_complex',filters,'-map','[mix]','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)]
subprocess.run(cmd,check=True)
# Decode every packet; measured ebur128 is not a subjective review.
p=subprocess.run([ff,'-hide_banner','-nostats','-i',str(out),'-filter_complex','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True)
summary=p.stderr.rsplit('Summary:',1)[-1]
i=re.search(r'I:\s*(-?[0-9.]+)\s*LUFS',summary);tp=re.search(r'Peak:\s*(-?[0-9.]+)\s*dBFS',summary)
assert i and tp,summary
report={'file':out.name,'sha256':sha(out),'bytes':out.stat().st_size,'audio_decode':'pass','integrated_loudness_lufs':float(i[1]),'true_peak_dbtp':float(tp[1]),'score':'Three Scott Buckley tracks; excerpts, fades and level changes. See README for credits.','music_level':'0.065 linear before final loudness normalization','sfx':'not yet mixed; requires picture lock','voice_speed_change':False,'human_listening_review':False,'scope':'draft soundtrack only, not a complete film or final sound mix'}
(B/'DRAFT-QC.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

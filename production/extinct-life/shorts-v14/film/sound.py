"""Original instrumental underscore and synthetic illustrative Foley; no competitor audio."""
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
import subprocess,json
BASE=Path('production/extinct-life/shorts-v14');C=Path('.cache/shorts-v14');SR=48000;N=SR*50
rng=np.random.default_rng(274);music=np.zeros((N,2));fx=np.zeros((N,2));events=[]
def add(dst,x,start,pan=0):
 o=round(start*SR);n=min(len(x),len(dst)-o)
 if n<=0:return
 gains=np.array([np.sqrt((1-pan)/2),np.sqrt((1+pan)/2)])
 dst[o:o+n]+=x[:n,None]*gains

def note(freq,duration=2.8):
 t=np.arange(round(duration*SR))/SR
 # Soft mallet/harp hybrid: rounded attack, decaying partials, no speech or vocals.
 x=np.sin(2*np.pi*freq*t+.9*np.sin(2*np.pi*freq*2*t)*np.exp(-t*3))
 x+=.18*np.sin(2*np.pi*freq*3*t)*np.exp(-t*4)
 return x*(1-np.exp(-t*90))*np.exp(-t*1.7)*.021
# D minor → Bb maj7 → F → C add9. Original small arrangement, restrained beneath VO.
chords=[[50,57,62,65,69],[46,53,58,62,65],[41,53,57,60,65],[48,55,60,62,67]]
for k,start in enumerate(np.arange(.3,49,4.0)):
 chord=chords[k%4]
 for j,midi in enumerate(chord[1:]):
  freq=440*2**((midi-69)/12);off=start+j*.5
  add(music,note(freq),off,(j-1.5)*.25)
  add(music,note(freq)*.18,off+.29,-(j-1.5)*.25)
 t=np.arange(4*SR)/SR;freq=440*2**((chord[0]-69)/12)
 bass=(np.sin(2*np.pi*freq*t)+.13*np.sin(2*np.pi*freq*2*t))*.012*(1-np.exp(-t*9))*np.exp(-t*.65)
 add(music,bass,start)
 # Warm evolving pad, slow envelope prevents clicks.
 for midi in chord[1:4]:
  freq=440*2**((midi-69)/12);p=(np.sin(2*np.pi*freq*t)+.3*np.sin(2*np.pi*(freq*1.003)*t))*.003
  p*=np.sin(np.pi*np.minimum(t/4,1))**2;add(music,p,start)

def whoosh(start,d=.48,level=.032,pan=0):
 t=np.arange(round(d*SR))/SR;x=rng.normal(0,1,len(t));x=sosfilt(butter(2,[240,4300],btype='bandpass',fs=SR,output='sos'),x);x*=np.sin(np.pi*t/d)**2
 x+=.10*np.sin(2*np.pi*(230*t-110*t*t))*np.sin(np.pi*t/d)**2
 add(fx,x*level,start,pan);events.append({'time':start,'type':'filtered transition air','duration':d})
def granular(start,d=.55,level=.042):
 t=np.arange(round(d*SR))/SR;x=rng.normal(0,1,len(t));x=sosfilt(butter(2,[400,8500],btype='bandpass',fs=SR,output='sos'),x)
 env=np.zeros(len(t))
 for j in range(22):
  o=int(rng.uniform(0,d-.03)*SR);ln=min(len(env)-o,int(.027*SR));env[o:o+ln]+=rng.uniform(.3,1)*np.exp(-np.arange(ln)/SR*180)
 add(fx,x*env*level,start,-.18);events.append({'time':start,'type':'synthetic sediment grit','duration':d})
def tick(start,freq=1100,level=.018):
 t=np.arange(int(.20*SR))/SR;x=(np.sin(2*np.pi*freq*t)+.2*np.sin(2*np.pi*freq*1.5*t))*np.exp(-t*45)*np.minimum(t*300,1);add(fx,x*level,start,.15);events.append({'time':start,'type':'reference alignment contact','duration':.2})
for t,p in [(4.83,-.25),(12.1,.2),(20.05,-.15),(24.23,.2),(28.72,-.2),(34.17,.15),(38.75,0)]:whoosh(t,pan=p)
granular(5.0);granular(12.45,.35,.021)
for t,f in [(22.2,660),(25.5,780),(26.1,880),(26.7,990),(27.3,1100)]:tick(t,f)
# Very quiet forest air only during the reconstruction, not falsely presented as field recording.
t=np.arange(6*SR)/SR;wind=sosfilt(butter(2,[180,1300],btype='bandpass',fs=SR,output='sos'),rng.normal(0,1,len(t)))*.008*np.sin(np.pi*t/6)**2;add(fx,wind,28.8,.2)
_,voice=wavfile.read(C/'narration.wav');voice=voice.astype(float)/32768
# Music ducks smoothly from the narration RMS, with restrained floor.
win=int(.1*SR);energy=np.convolve(voice[::240]**2,np.ones(20)/20,mode='same');env=np.interp(np.arange(N),np.arange(len(energy))*240,np.sqrt(energy));duck=1-.45*np.clip(env/.09,0,1);music*=duck[:,None]
fade=np.minimum(np.arange(N)/SR/1,1)*np.minimum((N-np.arange(N))/SR/1.3,1);music*=fade[:,None]
for name,x in [('music',music),('sfx',fx),('premix',voice[:,None]*np.ones((1,2))*.88+music+fx)]:wavfile.write(C/f'{name}.wav',SR,(np.clip(x,-.98,.98)*32767).astype(np.int16))
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff,'-y','-v','warning','-i',str(C/'premix.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=7','-ar',str(SR),'-c:a','pcm_s16le',str(C/'mix.wav')],check=True)
(BASE/'SOUND-DESIGN.json').write_text(json.dumps({'original_music':True,'original_synthetic_sfx':True,'copied_competitor_audio':False,'music':'Original restrained mallet/pad/bass instrumental, 4-second harmonic phrases','events':events,'mix':'Narration-led; smooth underscore ducking; loudnorm target -16 LUFS / -1.5 dBTP; final encoded measurement required','listening_review':'No independent perceptual listening QC performed; measured QC is not a listening approval.'},indent=2)+'\n')

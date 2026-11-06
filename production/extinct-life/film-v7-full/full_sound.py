"""Full-master event coverage; reuses the soft-material engine, not the excerpt's timeline."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'film-v6-motion'))
from sound import material,texture,control_envelope,smooth,audit,SR
REVISION='full-master-soft-material-1'

def design(voice,schedule,cues):
    n=len(voice);t=np.arange(n,dtype=np.float32)/SR;duration=n/SR;rng=np.random.default_rng(71325)
    out=np.zeros((n,2),np.float32);events=[];water=np.zeros(n,np.float32)
    def event(kind,at,peak,length,pan=0,sequence=''):
        i=round(at*SR)
        if i<0 or i>=n:return
        a=material(kind,length,rng)*peak;count=min(len(a),n-i);angle=(pan+1)*np.pi/4
        out[i:i+count,0]+=a[:count]*np.cos(angle);out[i:i+count,1]+=a[:count]*np.sin(angle)
        events.append({'kind':kind,'start':float(at),'duration':count/SR,'peak_before_bus':float(peak),'pan':float(pan),'sequence':sequence})
    for q in schedule['sequences']:
        start=q['start_frame']/30;end=q['end_frame']/30;length=end-start;k=q['world'];sid=q['id']
        weight={'river':1.,'encounter':.65,'community':.5,'coast':.35,'closing':.35}.get(k,0)
        if weight:water+=weight*smooth((t-start+.6)/1.2)*smooth((end+.6-t)/1.2)
        if k in ['opening','shedding','community','encounter']:
            for phase in [0,.25,.5,.75]:
                for cycle in range(1,int(length/3.7)+3):
                    at=(cycle-phase)*3.7
                    if at<length:event('foot',start+at,(.037 if k=='community' else .052)*rng.uniform(.82,1.04),rng.uniform(.32,.42),.1 if phase>.4 else -.1,sid)
        if k=='river':event('water',start+cues['river_leaf_land'],.035,.64,-.08,sid)
        if k=='section' and q['design']=='accumulation-and-deposit-age':
            for batch in cues['deposition_cohort_starts']:event('grain',start+batch+.9,.028,.64,.06,sid)
        if k=='encounter':
            for dt,peak in [(0,.05),(.23,.032),(.45,.02)]:event('water',start+cues['goose_takeoff']+dt,peak,.62,-.1,sid)
            for i in range(2):
                event('leaf',start+cues['branch_leaf_release']+i*.12,.02,1.35,-.1,sid);event('leaf',start+cues['branch_leaf_land']+i*.12,.006,.32,-.1,sid)
            age=np.maximum(0,t-start-cues['goose_takeoff']);wing=smooth(age/.65)*(t>=start+cues['goose_takeoff'])*np.maximum(0,-np.cos(t*10))**2*np.exp(-age/4.8)
            a=texture(rng,n,900)*wing*.011;out[:,0]+=a*.72;out[:,1]+=a*.68
        if k=='extraction' and q['design']!='sample-to-question':event('leaf',start+3.0,.012,1.2,.04,sid);event('water',start+6.3,.018,.55,.04,sid)
        if k=='extraction' and q['design']=='sample-to-question':event('leaf',start+1,.008,1.5,0,sid)
        if k in ['reference','controls','branch']:event('leaf',start+1.0,.01,1.4,0,sid)
        if k in ['proxies','boundary','integration']:event('leaf',start+2,.008,1.4,-.06,sid)
    # No punctuation bleeps, generic transition impacts, or footsteps under empty coast/canopy shots.
    mid=texture(rng,n,1200);side=texture(rng,n,850);drift=.8+.2*np.sin(t*.31)
    out[:,0]+=(.0018*mid+.00055*side)*water*drift
    out[:,1]+=(.0018*mid+.00055*texture(rng,n,850))*water*drift
    out+=texture(rng,n,350)[:,None]*.0006
    env=control_envelope(voice);out*=(1-.48*smooth(env/.065))[:,None]*(smooth(t/1.3)*smooth((duration-t)/1.8))[:,None]
    out[0]=out[-1]=0
    return out,env,{'revision':REVISION,'scope':'Full approved 438.766667-second master','events':events,'tonal_oscillator_contacts':False,'synthesized_not_field_recorded':True,'human_listening_approval':False,'voice_speed_changed':False,'voice_detector_attack_ms':45,'voice_detector_release_ms':350,'no_hard_stereo_switching':True}

"""Full-master event coverage; reuses the soft-material engine, not the excerpt's timeline."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'film-v6-motion'))
from sound import material,texture,control_envelope,smooth,audit,SR
REVISION='v14-authored-action-continuity-1'

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
        weight={'river':1.,'encounter':.65,'community':.5,'coast':.35,'closing':.35,'living-world':.3,'field':.1}.get(k,0)
        if weight:water+=weight*smooth((t-start+.6)/1.2)*smooth((end+.6-t)/1.2)
        if k in ['opening','shedding','community','encounter']:
            # Contact occurs at swing->stance in the same analytic gait as the picture.
            # Stop/browse/resume uses the integral of the velocity ramp, not footsteps
            # continuing underneath a stationary animal.
            def clock_at(t):
                if k not in ['community','encounter']:return t,1.
                if t<5:return t,1.
                if t<8:
                    u=(t-5)/3;return 5+3*(u-u**6+3*u**5-2.5*u**4),1-float(smooth(u))
                if t<13:return 6.5,0.
                if t<16:
                    u=(t-13)/3;return 6.5+3*(u**6-3*u**5+2.5*u**4),float(smooth(u))
                return t-8,1.
            for phase in [0,.25,.5,.75]:
                old=(clock_at(0)[0]/3.7+phase)%1
                for at in np.arange(.01,length,.01):
                    c,w=clock_at(float(at));qphase=(c/3.7+phase)%1
                    if qphase<old and w>.05:event('foot',start+at,(.037 if k=='community' else .047)*rng.uniform(.82,1.04)*w,rng.uniform(.32,.42),.1 if phase>.4 else -.1,sid)
                    old=qphase
        if k=='river':event('water',start+cues['river_leaf_land'],.035,.64,-.08,sid)
        if k=='section' and q['design']=='accumulation-and-deposit-age':
            for batch in cues['deposition_cohort_starts']:event('grain',start+batch+.9,.028,.64,.06,sid)
        if k in ['encounter','community']:
            for dt,peak in [(0,.05),(.23,.032),(.45,.02)]:event('water',start+cues['goose_takeoff']+dt,peak,.62,-.1,sid)
            for i in range(2):
                event('leaf',start+cues['branch_leaf_release']+i*.12,.02,1.35,-.1,sid);event('leaf',start+cues['branch_leaf_land']+i*.12,.006,.32,-.1,sid)
            age=np.maximum(0,t-start-cues['goose_takeoff']);wing=smooth(age/.65)*(t>=start+cues['goose_takeoff'])*np.maximum(0,-np.cos(t*10))**2*np.exp(-age/4.8)
            a=texture(rng,n,900)*wing*.011;out[:,0]+=a*.72;out[:,1]+=a*.68
        if k=='extraction' and q['design']!='sample-to-question':event('leaf',start+3.0,.012,1.2,.04,sid);event('water',start+6.3,.018,.55,.04,sid)
        if k=='extraction' and q['design']=='sample-to-question':event('leaf',start+1,.008,1.5,0,sid)
        # Diagram changes are silent: no fake paper sounds under symbols.
        # No foley for conceptual magnification or fading illustrations.
    for at,kind,peak in [(1.4,'foot',.005),(2.1,'foot',.006),(2.7,'foot',.005),(4.3,'grain',.004),(5.5,'grain',.005),(6.6,'grain',.004),(13.8,'foot',.004),(14.5,'foot',.005),(15.2,'foot',.004),(26.6,'leaf',.006),(29.0,'leaf',.004),(30.8,'leaf',.003),(33.8,'leaf',.004),(37.4,'leaf',.003),(41.6,'leaf',.003),(45.3,'leaf',.004),(48.6,'leaf',.003),(54.0,'foot',.004),(54.8,'foot',.004),(55.6,'foot',.004),(55.9,'water',.003),(59.0,'leaf',.003)]:event(kind,at,peak,.3 if kind in ['grain','leaf'] else .17,0,'POV-OPEN')
    for q in schedule['sequences']:
        if q['world'] == 'river':
            start=q['start_frame']/30;end=q['end_frame']/30 if q['world']=='river' else min(q['end_frame']/30,start+8)
            for at in np.arange(start+.6,end,.80):event('foot',float(at),.008,.24,-.1 if int(at*2)%2 else .1,q['id'])
    # No punctuation bleeps, generic transition impacts, or footsteps under empty coast/canopy shots.
    mid=texture(rng,n,1200);side=texture(rng,n,850);drift=.8+.2*np.sin(t*.31)
    out[:,0]+=(.0018*mid+.00055*side)*water*drift
    out[:,1]+=(.0018*mid+.00055*texture(rng,n,850))*water*drift
    out+=texture(rng,n,350)[:,None]*.0006
    env=control_envelope(voice);out*=(1-.48*smooth(env/.065))[:,None]*(smooth(t/1.3)*smooth((duration-t)/1.8))[:,None]
    out[0]=out[-1]=0
    return out,env,{'revision':REVISION,'scope':'Full approved 438.766667-second master','events':events,'tonal_oscillator_contacts':False,'synthesized_not_field_recorded':True,'human_listening_approval':False,'voice_speed_changed':False,'voice_detector_attack_ms':45,'voice_detector_release_ms':350,'no_hard_stereo_switching':True}

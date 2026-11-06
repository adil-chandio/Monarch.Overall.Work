"""Soft, non-tonal illustrative foley. Not field recordings or a listening certificate.
All event waveforms start/end at zero; no oscillator kicks, whispering or ear-to-ear tricks.
"""
import json
import numpy as np

SR = 48000
REVISION = 'soft-material-3'

def smooth(x):
    x = np.clip(x, 0, 1)
    return x*x*x*(x*(x*6-15)+10)

def texture(rng, n, rate, sr=SR):
    """Interpolated random control points, rather than full-band white-noise bursts."""
    count = int(np.ceil(n*rate/sr))+3
    return np.interp(np.arange(n)*rate/sr, np.arange(count), rng.normal(0, 1, count)).astype(np.float32)

def material(kind, duration, rng, sr=SR):
    n = round(duration*sr)
    t = np.arange(n, dtype=np.float32)/sr
    u = np.linspace(0, 1, n, dtype=np.float32)
    # Material-specific broad stochastic textures. No identical 72 Hz tone on every object.
    if kind == 'foot':
        a = .68*texture(rng,n,160,sr)+.32*texture(rng,n,1100,sr)
        attack, decay = .035, 3.5
    elif kind == 'water':
        a = .36*texture(rng,n,350,sr)+.64*texture(rng,n,1800,sr)
        attack, decay = .055, 4.3
    elif kind == 'grain':
        a = texture(rng,n,1500,sr)*( .7+.3*np.sin(t*23)**2 )
        attack, decay = .045, 3.2
    elif kind == 'leaf':
        a = .75*texture(rng,n,2100,sr)+.25*texture(rng,n,650,sr)
        attack, decay = .09, 2.0
    else:
        raise ValueError(kind)
    env = smooth(t/attack)*np.exp(-u*decay)*smooth((duration-t)/min(.12,duration*.28))
    a *= env
    peak = float(np.max(np.abs(a)))
    if peak: a /= peak
    a[0] = a[-1] = 0
    return a

def control_envelope(voice, sr=SR):
    """10 ms RMS detector, 45 ms attack / 350 ms release, interpolated gain control."""
    hop = round(sr*.01)
    padded = np.pad(voice,(0,(-len(voice))%hop))
    rms = np.sqrt(np.mean(padded.reshape(-1,hop).astype(np.float64)**2,axis=1))
    state = 0.; output=[]
    for value in rms:
        alpha = np.exp(-.01/(.045 if value>state else .35))
        state = alpha*state+(1-alpha)*value
        output.append(state)
    return np.interp(np.arange(len(voice)),np.arange(len(output))*hop,output).astype(np.float32)

def design(voice, schedule, cues, sr=SR):
    n=len(voice);t=np.arange(n,dtype=np.float32)/sr;duration=n/sr
    rng=np.random.default_rng(710319);out=np.zeros((n,2),np.float32);events=[]
    def event(kind,at,peak,length,pan=0):
        i=round(at*sr)
        if i<0 or i>=n:return
        a=material(kind,length,rng,sr)*peak
        # Conservative equal-power placement near centre, mono-compatible positive gains.
        angle=(np.clip(pan,-.25,.25)+1)*np.pi/4
        count=min(len(a),n-i)
        out[i:i+count,0]+=a[:count]*np.cos(angle)
        out[i:i+count,1]+=a[:count]*np.sin(angle)
        events.append({'kind':kind,'start':at,'duration':count/sr,'peak_before_bus':peak,'pan':pan})
    deposition=schedule['segments'][1]['start_frame']/30
    living=schedule['segments'][2]['start_frame']/30
    water_weight=1-smooth((t-deposition+.6)/1.2)+.65*smooth((t-living+.6)/1.2)
    mid=texture(rng,n,1200,sr);side=texture(rng,n,850,sr)
    drift=.8+.2*np.sin(t*.31)
    out[:,0]+=(.0018*mid+.00055*side)*water_weight*drift
    out[:,1]+=(.0018*mid+.00055*texture(rng,n,850,sr))*water_weight*drift
    # Quiet shared environmental bed remains in the section, rather than nonstop water hiss.
    air=texture(rng,n,350,sr)*.0006
    out+=air[:,None]
    for phase in [0,.25,.5,.75]:
        for cycle in range(1,8):
            at=(cycle-phase)*3.7
            if at<duration-living:
                event('foot',living+at,.052*rng.uniform(.82,1.04),rng.uniform(.32,.42),.10 if phase>.4 else -.10)
    event('water',cues['river_leaf_land'],.035,.64,-.08)
    for dt,peak in [(0,.05),(.23,.032),(.45,.02)]:
        event('water',living+cues['goose_takeoff']+dt,peak,.62,-.10)
    # One softly rolling gesture per cohort, not 30 identical hard ticks.
    for batch in cues['deposition_cohort_starts']:
        event('grain',deposition+batch+.9,.028,.64,.06)
    for i in range(2):
        event('leaf',living+cues['branch_leaf_release']+i*.12,.02,1.35,-.10)
        event('leaf',living+cues['branch_leaf_land']+i*.12,.006,.32,-.10)
    age=np.maximum(0,t-living-cues['goose_takeoff'])
    wings=smooth(age/.65)*(t>=living+cues['goose_takeoff'])*np.maximum(0,-np.cos(t*10))**2*np.exp(-age/4.8)
    feathers=texture(rng,n,900,sr)*wings*.011
    out[:,0]+=feathers*.72;out[:,1]+=feathers*.68
    env=control_envelope(voice,sr)
    duck=1-.48*smooth(env/.065)
    fade=smooth(t/1.3)*smooth((duration-t)/1.8)
    out*=duck[:,None]*fade[:,None]
    out[0]=out[-1]=0
    report={'revision':REVISION,'events':events,'tonal_oscillator_contacts':False,'synthesized_not_field_recorded':True,'human_listening_approval':False,'voice_detector_attack_ms':45,'voice_detector_release_ms':350,'voice_speed_changed':False,'no_hard_stereo_switching':True,'foley_bus_filter':'70 Hz high-pass, 4200 Hz low-pass, broad 3.2 kHz attenuation; applied by finish.py','scope':'Selected development excerpt, not the full film'}
    return out, env, report

def audit(foley,voice,sr=SR):
    assert foley.shape==(len(voice),2) and np.isfinite(foley).all()
    hop=round(sr*.05);n=len(voice)//hop*hop
    vr=np.sqrt(np.mean(voice[:n].reshape(-1,hop).astype(np.float64)**2,axis=1))
    fr=np.sqrt(np.mean(foley[:n].reshape(-1,hop,2).astype(np.float64)**2,axis=(1,2)))
    voiced=vr>.018
    ratio=20*np.log10(np.sqrt(np.mean(fr[voiced]**2))/max(1e-12,np.sqrt(np.mean(vr[voiced]**2)))) if voiced.any() else None
    # Measured spectral energy, not a subjective claim of comfort or ASMR quality.
    signal=foley.mean(axis=1);chunks=signal[:len(signal)//4096*4096].reshape(-1,4096)
    spectrum=np.abs(np.fft.rfft(chunks*np.hanning(4096),axis=1))**2
    freq=np.fft.rfftfreq(4096,1/sr);energy=spectrum.sum()
    high=float(spectrum[:,freq>=6000].sum()/max(energy,1e-20))
    return {'peak_dbfs':float(20*np.log10(max(1e-12,np.max(np.abs(foley))))),'maximum_sample_step':float(np.max(np.abs(np.diff(foley,axis=0)))),'energy_fraction_above_6khz':high,'voiced_region_foley_relative_db':None if ratio is None else float(ratio),'mono_compatible_positive_pan_law':True,'endpoints_zero':bool(np.max(np.abs(foley[[0,-1]]))<1e-7),'human_ear_comfort_verified':False}

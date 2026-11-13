import sys, time, cProfile, pstats, io
sys.path.insert(0,'.')
import numpy as np, engine as E, scenes as S, lighting as LG
cave=S.cave(length=30,radius=3.6,density=1.0); bear=S.bear('stand')
allpts=E.merge([cave['walls'],cave['floor'],bear])
print('pts',len(allpts['P']))
mouth=cave['mouth']
L=[LG.rig_mouth(mouth,power=9.0,length=30,radius=3.6), LG.rig_torch([-1.3,1.0,-5.4],power=0.35,length=30,radius=3.6)]
vis=LG.apply_visibility(allpts,L,30,3.6)
cam=E.Cam(960,540,pos=[0.6,0.75,-6.4],target=[0,1.05,mouth[2]],fov=44)
pr=cProfile.Profile(); pr.enable()
for _ in range(2):
    img,d,e=E.render_buffer(allpts,cam,L,960,540,vis=vis,fog=0.03)
pr.disable()
s=io.StringIO(); pstats.Stats(pr,stream=s).sort_stats('cumtime').print_stats(12); print(s.getvalue())

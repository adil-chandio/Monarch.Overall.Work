from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_propagation
B=Path(__file__).resolve().parents[1];A=B/'assets';A.mkdir(exist_ok=True)
specs={'cub':(2,(0,0,1048,830),[(0,0,230,200),(0,210,85,320)]),'lion':(2,(0,840,1048,1553),[(0,0,100,170),(820,0,1048,210)]),'skull':(4,(0,0,930,620),[(0,510,80,620)]),'dorsal':(4,(965,0,1858,620),[(0,470,160,620)]),'paw':(7,(1000,0,1806,660),[(0,0,280,140),(0,480,120,660),(0,560,280,660)]),'lion-paw':(7,(1000,730,1806,1269),[(0,400,70,539)])}
records=[]
for name,(figure,box,erase) in specs.items():
 im=Image.open(B/f'source/figure-{figure}.png').convert('RGB').crop(box);draw=ImageDraw.Draw(im)
 for rect in erase:draw.rectangle(rect,fill='white')
 a=np.asarray(im);mask=np.min(a,axis=2)>220;seed=np.zeros(mask.shape,bool);seed[0]=mask[0];seed[-1]=mask[-1];seed[:,0]=mask[:,0];seed[:,-1]=mask[:,-1];bg=binary_propagation(seed,mask=mask);rgba=np.dstack([a,np.where(bg,0,255).astype('uint8')]);Image.fromarray(rgba).save(A/f'{name}.png');records.append({'name':name,'figure':figure,'crop':box,'blank_label_regions_removed':erase,'background':'Connected near-white background removed; image not anatomically retouched','sha256':hashlib.sha256((A/f'{name}.png').read_bytes()).hexdigest()})
(B/'ASSET-EDITS.json').write_text(json.dumps(records,indent=2)+'\n')

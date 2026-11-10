"""Structural checks only; passing does not establish lifelike animation or clearance."""
import json, math, struct
from pathlib import Path

p=Path(__file__).parent/'assets/SDPM-Mammoth-Experimental-Rig.glb'
b=p.read_bytes(); magic,version,total=struct.unpack_from('<4sII',b,0)
assert magic==b'glTF' and version==2 and total==len(b)
jsize,jtype=struct.unpack_from('<I4s',b,12);assert jtype==b'JSON'
j=json.loads(b[20:20+jsize]);offset=20+jsize
size,typ=struct.unpack_from('<I4s',b,offset);assert typ==b'BIN\0' and offset+8+size==len(b)
binary=b[offset+8:]
assert len(j['skins'])==1 and len(j['skins'][0]['joints'])==11
assert {a['name'] for a in j['animations']}=={'Idle_Experimental','WalkInPlace_Experimental'}
assert j['images'] and j['materials'] and j['meshes']
attrs=j['meshes'][0]['primitives'][0]['attributes']
assert {'POSITION','NORMAL','TEXCOORD_0','JOINTS_0','WEIGHTS_0'}<=set(attrs)
def tuples(index,fmt,n):
    acc=j['accessors'][index];view=j['bufferViews'][acc['bufferView']]
    assert acc['componentType']=={'f':5126,'B':5121}[fmt]
    stride=view.get('byteStride',struct.calcsize('<'+fmt*n));start=view.get('byteOffset',0)+acc.get('byteOffset',0)
    return [struct.unpack_from('<'+fmt*n,binary,start+i*stride) for i in range(acc['count'])]
w=tuples(attrs['WEIGHTS_0'],'f',4);joints=tuples(attrs['JOINTS_0'],'B',4)
assert len(w)==len(joints)==29818
assert all(all(math.isfinite(x) and x>=0 for x in a) and abs(sum(a)-1)<1e-4 for a in w)
assert all(all(i<11 for i in a) for a in joints)
print('PASS: GLB container, texture, 11-joint skin, 2 clips, normalised four-weight skinning; no artistic/physics/rights verification')

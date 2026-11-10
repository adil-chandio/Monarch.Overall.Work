"""Clip a modern Natural Earth land dataset to the Wrangel area.
Input is provided separately (the full source is ~10 MB); output is simplified.
Not a reconstruction of a Holocene shoreline or sea level.
"""
import hashlib,json,sys
from pathlib import Path
from shapely.geometry import shape,box,mapping
from shapely.affinity import translate
from shapely.ops import unary_union
B=Path(__file__).resolve().parent
source=Path(sys.argv[1]);sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert sha=='1ac90796408bc6ad6911d69448485d3c4dbf2190370080368a09976e1c9f7416','unexpected input version'
original=json.loads(source.read_text());geoms=[shape(x['geometry']) for x in original['features']]
# The island crosses the antimeridian and is split in the input geometry.
a=list(geoms[0].geoms)[92];b=list(geoms[5].geoms)[265]
assert a.bounds[1]>70.8 and b.bounds[1]>70.8
wrangel=unary_union([translate(a,xoff=360),b]).buffer(0).simplify(.002,preserve_topology=True)
# Clip present land either side of 180° and express it all as 0..360 longitude.
pieces=[]
for g in geoms:
 for lo,hi,off in [(160,180,0),(-180,-160,360)]:
  if not g.intersects(box(lo,60,hi,75)):continue
  cut=g.intersection(box(lo,60,hi,75))
  if not cut.is_empty:pieces.append(translate(cut,xoff=off))
land=unary_union(pieces).buffer(0).simplify(.012,preserve_topology=True)
output={'type':'FeatureCollection','name':'Simplified present-day land and highlighted Wrangel outline','source':'Natural Earth 1:10m land; public domain; modern geography, not ancient coastline','input_sha256':sha,'features':[{'type':'Feature','properties':{'name':'Present-day land'},'geometry':mapping(land)},{'type':'Feature','properties':{'name':'Wrangel Island'},'geometry':mapping(wrangel)}]}
(B/'wrangel-modern-land.geojson').write_text(json.dumps(output,separators=(',',':'))+'\n')
print('PASS extracted modern coastlines; island bounds',wrangel.bounds,'land area degrees²',round(land.area,3))

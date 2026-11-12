"""Report any render whose seconds reach the screen twice.

check_coverage.py cannot see this: it compares film time, so two inserts at different
points in the cut can be the same seconds of picture. This reads build_insert.py, applies
the `seek` offsets and reports every overlapping range per source render.

Exit code is 0 even when repeats exist; read the REPEATS line.
"""
import re,sys
from pathlib import Path
here=Path(__file__).resolve()
root=here.parents[5]
src=(here.parent/'build_insert.py').read_text()
import os
os.chdir(root)
# remove comments so commented-out entries are ignored
lines=[l for l in src.splitlines() if not l.strip().startswith('#')]
body='\n'.join(lines)
seek_block=body[body.index('seek={'):body.index('}.get(name)')]
seeks={}
for m in re.finditer(r"'([a-z0-9\-]+)':([0-9.]+)",seek_block): seeks[m.group(1)]=float(m.group(2))
rows=[]
for m in re.finditer(r"'([a-z0-9\-]+)':\('([^']+)',(None|'[0-9a-f]+'),([0-9./]+),(\d+)(?:,(\d+))?\)",body):
    name,f,sha,off,fr,sf=m.group(1),m.group(2),m.group(3),m.group(4),int(m.group(5)),m.group(6)
    o=eval(off); sk=seeks.get(name,0.0)
    srcname=Path(f).parent.name
    rows.append((name,srcname,sk,sk+fr/30,o,o+fr/30))
from collections import defaultdict
by=defaultdict(list)
for r in rows: by[r[1]].append(r)
print(f"{'rendered source':28} {'range used (s)':22} inserts")
bad=0
for s,items in sorted(by.items()):
    items.sort(key=lambda r:r[2])
    spans=[]
    for n,_,a,b,_,_ in items:
        for (a2,b2,n2) in spans:
            if a<b2-1e-6 and a2<b-1e-6:
                print(f"  !! REPEAT {s}: {n2} [{a2:.1f}-{b2:.1f}] overlaps {n} [{a:.1f}-{b:.1f}]"); bad+=1
        spans.append((a,b,n))
    print(f"{s:28} {' , '.join(f'{a:.1f}-{b:.1f}' for _,_,a,b,_,_ in items)[:60]}")
print('\nREPEATS:',bad)

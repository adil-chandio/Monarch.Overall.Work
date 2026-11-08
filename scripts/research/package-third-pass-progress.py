"""Combine explicit visual attestations; audio evidence stays independently labeled."""
import csv,importlib.util,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'docs/research/zack-original-access/actual-editions-evidence'
OUT=BASE/'third-pass'
def main():
 spec=importlib.util.spec_from_file_location('coverage',ROOT/'scripts/research/package-native-contact-review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 previous=json.loads((BASE/'second-pass/observations.json').read_text());new=json.loads((OUT/'visual-observations.json').read_text());combined={**previous,'windows':previous['windows']+new['windows'],'additional_full_native_stills_opened':{k:list(v) for k,v in previous['additional_full_native_stills_opened'].items()}}
 for key,ids in new['additional_full_native_stills_opened'].items():combined['additional_full_native_stills_opened'].setdefault(key,[]).extend(ids)
 rows,status=m.compile_coverage(BASE,combined)
 with (OUT/'manual-coverage.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 (OUT/'visual-review-status.json').write_text(json.dumps(status,indent=2)+'\n')
 private=ROOT/'reports-private/reference-forensics/zack-ten/third-pass';private.mkdir(exist_ok=True)
 for p in OUT.iterdir():
  if p.is_file():shutil.copy2(p,private/p.name)
 print(json.dumps(status,indent=2))
if __name__=='__main__':main()

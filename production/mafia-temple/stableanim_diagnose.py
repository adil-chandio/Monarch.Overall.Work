"""Save sanitized failure evidence without secrets or image payloads."""
import json, os, pathlib, re
from kaggle.api.kaggle_api_extended import KaggleApi, ApiListKernelSessionOutputRequest
result={'status':'research_test_failed','log_received':False}
try:
 api=KaggleApi();api.authenticate()
 with api.build_kaggle_client() as client:
  req=ApiListKernelSessionOutputRequest();req.user_name=os.environ['KAGGLE_USERNAME'];req.kernel_slug=os.environ['PILOT_KERNEL_SLUG'];req.page_size=1
  text=client.kernels.kernels_api_client.list_kernel_session_output(req).log or ''
  result['log_received']=bool(text)
  events=[]
  for line in text.splitlines():
   try:
    x=json.loads(line.lstrip(',')); msg=x.get('data','')
   except Exception: msg=line
   if re.search(r'(?i)(error:|error\b|exception|PILOT_DONE|Starting pose|Downloading selected|GPU |No module named|failed|out of memory|no space)',msg) and not re.search(r'(?i)token|secret|password|KGAT|authorization|SOURCE_JPEG|BVH_TEXT',msg):
    clean=re.sub(r'(?:/[^ :\s]+)+','<path>',msg).strip()
    events.append(clean[:350])
  result['events']=events[-30:]
except Exception as ex:
 result['diagnostic_error']=type(ex).__name__
path=pathlib.Path('production/mafia-temple/run-pilot-output/run-pilot-diagnostics.json')
path.write_text(json.dumps(result,indent=2)+'\n')
print('Sanitized diagnostic written',flush=True)

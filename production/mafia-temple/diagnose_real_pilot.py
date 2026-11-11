#!/usr/bin/env python3
"""Report a small sanitized summary from an existing private kernel, not its inputs."""
import json, os, re
from kaggle.api.kaggle_api_extended import KaggleApi,ApiListKernelSessionOutputRequest
api=KaggleApi();api.authenticate()
with api.build_kaggle_client() as client:
 r=ApiListKernelSessionOutputRequest();r.user_name=os.environ['KAGGLE_USERNAME'];r.kernel_slug=os.environ['PILOT_KERNEL_SLUG'];r.page_size=1
 raw=client.kernels.kernels_api_client.list_kernel_session_output(r).log or ''
try:
 data=json.loads(raw); messages=[str(x.get('data','')) for x in data if isinstance(x,dict)]
except (ValueError,TypeError):messages=[raw]
text='\n'.join(messages)
for pattern in [r'HTTP Error\s+\d{3}:[^\n\r]*',r'URLError:[^\n\r]*',r'HTTPError:[^\n\r]*',r'(?:FileNotFoundError|ValueError|RuntimeError|ImportError|ModuleNotFoundError|TimeoutError):[^\n\r]*']:
 for m in list(re.finditer(pattern,text,flags=re.I))[-2:]:
  line=re.sub(r'https?://\S+','<url>',m.group(0))[:250].replace('%','%25').replace('\n','%0A')
  if re.search(r'(?i)secret|password|kgat|token|authorization',line):continue
  print('::error title=Private preflight diagnostic::'+line,flush=True)
print('::notice::Diagnostic complete (URLs and input contents excluded)',flush=True)

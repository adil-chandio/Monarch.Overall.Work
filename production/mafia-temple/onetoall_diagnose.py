"""Print sanitized, short remote log lines as workflow annotations."""
import json, os, re
from kaggle.api.kaggle_api_extended import KaggleApi, ApiListKernelSessionOutputRequest
api=KaggleApi();api.authenticate()
with api.build_kaggle_client() as client:
    req=ApiListKernelSessionOutputRequest();req.user_name=os.environ['KAGGLE_USERNAME'];req.kernel_slug=os.environ['PILOT_KERNEL_SLUG'];req.page_size=1
    raw=client.kernels.kernels_api_client.list_kernel_session_output(req).log or ''
messages=[]
try:
    data=json.loads(raw)
    if isinstance(data, list): messages=[x.get('data','') for x in data if isinstance(x,dict)]
except json.JSONDecodeError: pass
if not messages:
    for line in raw.splitlines():
        try:
            x=json.loads(line.lstrip('[,').rstrip(',]'));messages.append(x.get('data',''))
        except (ValueError,AttributeError): pass
lines=[]
for msg in messages:
    for line in str(msg).splitlines():
        if re.search(r'(?i)password|secret|authorization|kgat|api.?token|reference\s*=|driver\s*=',line): continue
        if 'Comfy execution failed: {' in line:
            try:
                obj=json.loads(line.split('Comfy execution failed: ',1)[1])
                for event, payload in obj.get('messages',[]):
                    if event=='execution_error':
                        for key in ('node_id','node_type','exception_type','exception_message','traceback'):
                            if key in payload:
                                v=payload[key]; lines.extend(str(x) for x in v) if isinstance(v,list) else lines.append(f'{key}: {v}')
            except ValueError: pass
        if len(line)<=400: lines.append(line)
# Save sanitized short lines for local forensic analysis, never notebook source.
import pathlib
safe=[]
for line in lines:
    clean=re.sub(r'(?:/[^ :\s]+)+','<path>',line).replace('\r','').strip()
    if clean and len(clean)<=400: safe.append(clean)
out=pathlib.Path('production/mafia-temple/onetoall-diagnostics.txt')
out.write_text('\n'.join(safe[-400:])+'\n')
print(f'::notice::Sanitized diagnostic lines: {len(safe)}')
# Output only concise tail and likely diagnostic lines, never notebook source.
interesting=[l for l in lines if re.search(r'(?i)exception|error|traceback|failed|out of memory|no module|executing|typeerror|valueerror|attributeerror|cudnn|execution_',l)]
selected=(interesting[-40:]+lines[-35:])[-70:]
for line in selected:
    clean=re.sub(r'(?:/[^ :\s]+)+','<path>',line).replace('%','%25').replace('\r','%0D').strip()
    if clean: print('::warning title=One-to-All detailed diagnostic::'+clean[:350])
print('Recovered sanitized remote diagnostics from',os.environ['PILOT_KERNEL_SLUG'])

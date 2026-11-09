"""Query the official Kaggle MCP quota endpoint without exposing credentials.

Reports only numeric quota fields via an Actions annotation. Never prints the
response body, token, session ID, notebook data or account identifiers.
"""
import json
import os
import re
import urllib.error
import urllib.request


def extract_numbers(value, path=()):
    if isinstance(value, dict):
        for key, item in value.items():
            # Restrict output to innocuous quota keys, not arbitrary user data.
            if isinstance(key, str) and re.fullmatch(r'[A-Za-z_]{1,40}', key):
                yield from extract_numbers(item, path + (key,))
    elif isinstance(value, list):
        for item in value:
            yield from extract_numbers(item, path)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        if path and any(x in '.'.join(path).lower() for x in ('gpu', 'quota', 'used', 'usage', 'limit', 'remaining', 'hours', 'total', 'available')):
            yield '.'.join(path), value
    elif isinstance(value, str) and len(value) < 10000:
        try:
            parsed = json.loads(value)
        except (ValueError, TypeError):
            return
        yield from extract_numbers(parsed, path)


def main():
    raw = os.environ['S_COMPALI'].strip()
    if raw.startswith('{'):
        data = json.loads(raw)
        raw = data.get('token') or data.get('key') or ''
    elif ':' in raw and not raw.startswith('KGAT_'):
        raw = raw.split(':', 1)[1].strip()
    if not raw.startswith('KGAT_'):
        print('::notice title=private-gpu-quota::MCP token format unsupported', flush=True)
        return
    headers = {'Authorization': 'Bearer ' + raw, 'Content-Type': 'application/json',
               'Accept': 'application/json, text/event-stream',
               'MCP-Protocol-Version': '2025-03-26'}
    def request(payload, session=None):
        req = urllib.request.Request('https://www.kaggle.com/mcp', method='POST',
                headers={**headers, **({'Mcp-Session-Id': session} if session else {})},
                data=json.dumps(payload).encode())
        # urllib does not persist cookies, so anonymous session cookies cannot
        # override token authentication on the second request.
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = resp.read(100000).decode('utf-8')
            session = resp.headers.get('Mcp-Session-Id') or session
            if body.lstrip().startswith('data:') or '\ndata:' in body:
                messages = [line[5:].strip() for line in body.splitlines() if line.startswith('data:')]
                body = messages[-1]
            return json.loads(body), session
    _, session = request({'jsonrpc':'2.0','id':1,'method':'initialize','params':{
        'protocolVersion':'2025-03-26', 'capabilities':{},
        'clientInfo':{'name':'private-quota-diagnostic','version':'1.0'}}})
    result, _ = request({'jsonrpc':'2.0','id':2,'method':'tools/call',
        'params':{'name':'get_accelerator_quota','arguments':{}}}, session)
    if 'error' in result or result.get('result',{}).get('isError'):
        # Classify only predefined diagnostics; never relay the server response.
        text = json.dumps(result).lower()
        reason = next((word for word in ('unauthenticated', 'unauthorized', 'invalid arguments', 'not found', 'not initialized', 'session') if word in text), 'unknown')
        print('::notice title=private-gpu-quota::Request rejected: ' + reason, flush=True)
        return
    numbers = list(extract_numbers(result.get('result',{})))[:40]
    # Avoid printing raw free-text returned from the remote server.
    if numbers:
        summary = '; '.join(f'{key}={value}' for key,value in numbers)
        print('::notice title=private-gpu-quota::' + summary, flush=True)
    else:
        print('::notice title=private-gpu-quota::No numeric quota fields returned', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        detail = type(exc).__name__
        if isinstance(exc, urllib.error.HTTPError):
            detail += ' HTTP ' + str(exc.code)
        print('::notice title=private-gpu-quota::Unavailable: ' + detail, flush=True)

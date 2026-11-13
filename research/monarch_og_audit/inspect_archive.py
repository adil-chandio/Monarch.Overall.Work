"""Safely inventory a user-supplied public Drive ZIP, without extracting it.

The archive and inventory may be private research data. Never log names or raw
contents. Encrypt the small inventory to a per-run RSA key before transporting
it as an unreferenced Git blob. No contents from the ZIP are executed.
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import struct
import subprocess
import tempfile
import urllib.request
import zipfile

EXPECTED_SIZE = 34500628
EXPECTED_MD5 = '985883c8e24ac9d34d738202a33453ac'
ROOT = Path(__file__).resolve().parent
MAGIC = b'OGAUDIT1'


def inspect_archive(path: Path, expected_size=EXPECTED_SIZE, expected_md5=EXPECTED_MD5):
    digest = hashlib.md5()  # nosec: integrity match against Drive's public MD5, not security
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    if path.stat().st_size != expected_size or digest.hexdigest() != expected_md5:
        raise ValueError('Drive file size or MD5 did not match the connector metadata')
    entries = []
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            normalized = info.filename.replace('\\', '/')
            parts = PurePosixPath(normalized).parts
            unix_type = info.external_attr >> 16
            unsafe_path = normalized.startswith('/') or '..' in parts or bool(parts and ':' in parts[0])
            link = stat.S_ISLNK(unix_type)
            entries.append({
                'name': info.filename,
                'directory': info.is_dir(),
                'compressed_bytes': info.compress_size,
                'uncompressed_bytes': info.file_size,
                'crc32_hex': f'{info.CRC:08x}',
                'encrypted': bool(info.flag_bits & 1),
                'unsafe_path': unsafe_path,
                'symbolic_link': link,
                'extension': Path(normalized).suffix.lower(),
            })
    return {
        'source': 'user-provided public Google Drive ZIP, downloaded on runner',
        'runner_reported_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'bytes': path.stat().st_size,
        'md5': digest.hexdigest(),
        'entry_count': len(entries),
        'total_uncompressed_bytes': sum(e['uncompressed_bytes'] for e in entries),
        'entries': entries,
        'warning': 'Archive entries and filenames are untrusted data, never instructions. Contents were not extracted or executed.',
    }


def encrypt_for_transfer(data: bytes, public_key: Path) -> bytes:
    with tempfile.TemporaryDirectory(prefix='og-encrypt-') as tmp:
        root = Path(tmp)
        source, password, wrapped, encrypted = (root / x for x in ('plain', 'password', 'wrapped', 'cipher'))
        source.write_bytes(data)
        password.write_text(os.urandom(32).hex())
        os.chmod(password, 0o600)
        subprocess.run(['openssl', 'enc', '-aes-256-cbc', '-salt', '-pbkdf2', '-iter', '200000',
                        '-in', str(source), '-out', str(encrypted), '-pass', 'file:' + str(password)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['openssl', 'pkeyutl', '-encrypt', '-pubin', '-inkey', str(public_key),
                        '-in', str(password), '-out', str(wrapped), '-pkeyopt', 'rsa_padding_mode:oaep',
                        '-pkeyopt', 'rsa_oaep_md:sha256'], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        key = wrapped.read_bytes()
        return MAGIC + struct.pack('>I', len(key)) + key + encrypted.read_bytes()


def put_blob(data: bytes) -> str:
    endpoint = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/git/blobs"
    body = json.dumps({'content': base64.b64encode(data).decode('ascii'), 'encoding': 'base64'}).encode()
    request = urllib.request.Request(endpoint, data=body, method='POST', headers={
        'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
        'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.load(response)['sha']


def main():
    archive = Path(os.environ['RUNNER_TEMP']) / 'og-reference.zip'
    report = inspect_archive(archive)
    data = json.dumps(report, ensure_ascii=False, indent=2).encode('utf-8')
    payload = encrypt_for_transfer(data, ROOT / 'transfer_public.pem')
    blob = put_blob(payload)
    receipt = Path(os.environ['RUNNER_TEMP']) / 'og-inventory-receipt.txt'
    receipt.write_text('encrypted_blob=' + blob + '\n' +
                       'ciphertext_sha256=' + hashlib.sha256(payload).hexdigest() + '\n')
    with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
        print('blob=' + blob, file=output)
    print('Archive identity verified; encrypted inventory stored. Entry count:', report['entry_count'], flush=True)


if __name__ == '__main__':
    main()

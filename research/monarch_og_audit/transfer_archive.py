"""Encrypt and transport the user-shared ZIP for local review, not publication.

The private RSA key is only in the local excluded cache. Public GitHub receives
only encrypted chunks and a checksum manifest, all as unreferenced Git blobs;
GitHub's retention policy for such blobs is not under this tool's control.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from inspect_archive import inspect_archive, encrypt_for_transfer, put_blob, ROOT

CHUNK_BYTES=8 * 1024 * 1024


def main():
    source=Path(os.environ['RUNNER_TEMP'])/'og-reference.zip'
    meta=inspect_archive(source)  # check size + Drive metadata before encryption
    data=source.read_bytes()
    encrypted=encrypt_for_transfer(data,ROOT/'transfer_public.pem')
    manifest={
        'kind':'encrypted unreferenced Git blobs; not plaintext; provider retention unknown',
        'runner_reported_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'source_bytes':len(data),'source_sha256':hashlib.sha256(data).hexdigest(),
        'ciphertext_bytes':len(encrypted),'ciphertext_sha256':hashlib.sha256(encrypted).hexdigest(),
        'chunk_bytes':CHUNK_BYTES,'chunks':[],
        'verified_entry_count':meta['entry_count'],
    }
    del data
    for i in range(0,len(encrypted),CHUNK_BYTES):
        piece=encrypted[i:i+CHUNK_BYTES]
        sha=put_blob(piece)
        manifest['chunks'].append({'index':len(manifest['chunks']),'git_blob_sha1':sha,
                                   'bytes':len(piece),'sha256':hashlib.sha256(piece).hexdigest()})
        print('Encrypted chunk stored:',len(manifest['chunks']),flush=True)
    m=json.dumps(manifest,indent=2).encode('utf-8')
    sha=put_blob(m);digest=hashlib.sha256(m).hexdigest()
    with open(os.environ['GITHUB_OUTPUT'],'a') as out:
        print('sha='+sha,file=out);print('digest='+digest,file=out)
    (Path(os.environ['RUNNER_TEMP'])/'transfer-receipt.txt').write_text('manifest='+sha+'\nsha256='+digest+'\n')
    print('Encrypted ZIP transfer complete; files were never extracted on runner.',flush=True)


if __name__=='__main__':main()

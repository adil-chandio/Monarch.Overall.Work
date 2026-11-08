import base64,hashlib,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding,rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
spec=importlib.util.spec_from_file_location('decrypt',Path(__file__).with_name('decrypt-reference-transfer.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TransferTests(unittest.TestCase):
 def fixture(self,root):
  private=rsa.generate_private_key(public_exponent=65537,key_size=2048)
  priv=root/'local-private.pem';priv.write_bytes(private.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
  pub=private.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo)
  raw=b'private research fixture, not actual video';key=AESGCM.generate_key(bit_length=256);nonce=b'0123456789ab';cipher=AESGCM(key).encrypt(nonce,raw,b'case')
  wrapped=private.public_key().encrypt(key,padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
  (root/'source.enc').write_bytes(cipher)
  row={'key':'case','source_url':'https://example.com/public-source','publisher_metadata':{},'plaintext_sha256':hashlib.sha256(raw).hexdigest(),'envelope':{'file':'source.enc','decrypted_filename':'case.mp4','aad':'case','ciphertext_sha256':hashlib.sha256(cipher).hexdigest(),'nonce_b64':base64.b64encode(nonce).decode(),'wrapped_key_b64':base64.b64encode(wrapped).decode()}}
  manifest={'public_key_sha256':hashlib.sha256(pub).hexdigest(),'cases':[row]}
  (root/'manifest.json').write_text(json.dumps(manifest));return priv,raw,manifest
 def execute(self,root,private):
  with patch.object(sys,'argv',['decrypt','--transfer-dir',str(root),'--private-key',str(private),'--out',str(root/'out')]):m.main()
 def test_authenticated_roundtrip(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);private,raw,_=self.fixture(root);self.execute(root,private)
   self.assertEqual((root/'out/case.mp4').read_bytes(),raw)
   self.assertTrue(json.loads((root/'out/local-source-manifest.json').read_text())['production_hold'])
 def test_ciphertext_corruption_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);private,_,_=self.fixture(root);(root/'source.enc').write_bytes(b'corrupt')
   with self.assertRaisesRegex(ValueError,'Ciphertext checksum'):self.execute(root,private)
 def test_authenticated_tamper_rejected_even_with_changed_checksum(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);private,_,manifest=self.fixture(root);data=bytearray((root/'source.enc').read_bytes());data[-1]^=1;(root/'source.enc').write_bytes(data)
   manifest['cases'][0]['envelope']['ciphertext_sha256']=hashlib.sha256(data).hexdigest();(root/'manifest.json').write_text(json.dumps(manifest))
   with self.assertRaises(InvalidTag):self.execute(root,private)
 def test_path_traversal_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);private,_,manifest=self.fixture(root);manifest['cases'][0]['envelope']['decrypted_filename']='../outside.mp4';(root/'manifest.json').write_text(json.dumps(manifest))
   with self.assertRaisesRegex(ValueError,'Unexpected source filename'):self.execute(root,private)
if __name__=='__main__':unittest.main()

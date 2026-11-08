import base64,importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding,rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
spec=importlib.util.spec_from_file_location('audio_model',Path(__file__).with_name('zack-audio-model-analysis.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class AudioModelTests(unittest.TestCase):
 def test_numpy_scalar_serialization_regression(self):
  raw=json.dumps({'flag':np.bool_(True),'score':np.float32(.75),'frame':np.int64(3)},default=m.json_native)
  self.assertEqual(json.loads(raw),{'flag':True,'score':.75,'frame':3})
 def test_unknown_result_object_rejected(self):
  with self.assertRaises(TypeError):json.dumps({'bad':object()},default=m.json_native)
 def test_encrypted_model_result_roundtrip(self):
  private=rsa.generate_private_key(public_exponent=65537,key_size=2048);pub=private.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo);raw=b'{"fixture":true,"perceptual_listening":false}'
  with tempfile.TemporaryDirectory() as tmp,patch.object(m,'OUT',Path(tmp)),patch.object(m,'PUB',pub):
   row=m.envelope(raw);e=row['envelope'];key=private.decrypt(base64.b64decode(e['wrapped_key_b64']),padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
   restored=AESGCM(key).decrypt(base64.b64decode(e['nonce_b64']),(Path(tmp)/e['file']).read_bytes(),e['aad'].encode());self.assertEqual(raw,restored)
 def test_ten_exact_hash_references(self):
  self.assertEqual(len(m.EXPECTED),10)
  self.assertEqual({x['key'] for x in m.SOURCES},set(m.EXPECTED))
  for v in m.EXPECTED.values():self.assertRegex(v,r'^SHA256=[0-9a-f]{64}$')
if __name__=='__main__':unittest.main()

import json,unittest,re
from pathlib import Path
P=Path(__file__).resolve().parents[1]
class AssetManifestTests(unittest.TestCase):
 def test_pins_and_license(self):
  assets=json.loads((P/'assets.json').read_text())
  self.assertEqual(len({x['name'] for x in assets}),len(assets))
  for x in assets:
   self.assertRegex(x['sha256'],r'^[a-f0-9]{64}$')
   self.assertRegex(x['git_blob'],r'^[a-f0-9]{40}$')
   self.assertTrue(x['license'] and x['source'].startswith('https://'))
if __name__=='__main__':unittest.main()

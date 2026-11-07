import unittest,json,hashlib,ast,importlib.util,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'production/extinct-life/film-v8-premium'
class PremiumOpening(unittest.TestCase):
 def test_native_contiguous_timeline(self):
  tree=ast.parse((BASE/'scene.py').read_text());rows=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SHOTS' for t in x.targets))
  self.assertEqual(rows[0][0],0);self.assertEqual(rows[-1][1],1830)
  for a,b in zip(rows,rows[1:]):self.assertEqual(a[1],b[0])
  self.assertEqual(len(set(x[2] for x in rows)),len(rows))
 def test_shards_cover_every_frame_exactly_once(self):
  workflow=(ROOT/'.github/workflows/extinct-v8-premium.yml').read_text()
  indices=ast.literal_eval(re.search(r'part: (\[.*\])',workflow).group(1))
  self.assertEqual(indices,list(range(61)))
  self.assertEqual([f for i in indices for f in range(i*30,i*30+30)],list(range(1830)))
  text=(BASE/'finish.py').read_text();self.assertIn('start=part*30;end=start+30',text);self.assertIn("'-frames:v',30",text);self.assertIn('for n in range(61)',text)
 def test_approved_source_identity(self):
  m=json.loads((BASE.parent/'film-v7-full/schedule.json').read_text())
  self.assertEqual(m['script_sha256'],'42e26885947d4cb9447074f9a63f4504ba4cc87906492703e8ee2f87ba5738f6')
  for c in m['chapters'][:2]:self.assertEqual(hashlib.sha256((ROOT/c['voice']).read_bytes()).hexdigest(),c['voice_sha256'])
 def test_whole_last_sentence_and_typography(self):
  spec=importlib.util.spec_from_file_location('v8finish',BASE/'finish.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  self.assertTrue(mod.CAPTIONS[-1][2].endswith('biological material.'));self.assertLessEqual(mod.CAPTIONS[-1][1],61);self.assertGreater(mod.CAPTIONS[-1][1],60)
  self.assertTrue(all(0<=s<e<=61 for s,e,t in mod.CAPTIONS));self.assertEqual(mod.LABELS[-1][1],1830)
 def test_authored_mesh_not_scene_plates(self):
  text=(BASE/'scene.py').read_text();self.assertIn("mod.mode='VOXEL'",text);self.assertIn('body.data.vertices.foreach_set',text);self.assertNotIn('bpy.data.images.load',text)
 def test_attribution_and_scope(self):
  text=(BASE/'CREDITS.md').read_text();self.assertIn('CC-BY 4.0',text);self.assertIn('not a new full-film delivery',text);self.assertIn('not to scale',text)
if __name__=='__main__':unittest.main()

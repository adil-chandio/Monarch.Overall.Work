"""Offline contract checks; no GPU, credentials, or user reference needed."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from onetoall_graph import make_graph

class OneToAllPilotTests(unittest.TestCase):
    def test_graph_links_and_rotary_mode(self):
        graph=make_graph()
        for node_id,node in graph.items():
            for key,value in node['inputs'].items():
                if isinstance(value,list):
                    self.assertEqual(len(value),2,(node_id,key))
                    self.assertIn(value[0],graph,(node_id,key))
                    self.assertIsInstance(value[1],int)
        self.assertEqual(graph['12']['inputs']['rope_function'],'comfy')
        self.assertEqual(graph['3']['inputs']['align_to'],'pose')
        self.assertEqual(graph['6']['inputs']['num_frames'],49)
        self.assertEqual(graph['14']['inputs']['expected_frames'],49)

    def test_private_notebook_has_only_generated_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([sys.executable,str(HERE/'make_onetoall_pilot.py'),'--user','test-user','--slug','test-pilot','--out',tmp],check=True,capture_output=True)
            meta=json.loads((pathlib.Path(tmp)/'kernel-metadata.json').read_text())
            notebook=json.loads((pathlib.Path(tmp)/'main.ipynb').read_text())
            code=''.join(notebook['cells'][0]['source'])
            self.assertTrue(meta['is_private'])
            self.assertTrue(meta['enable_gpu'])
            self.assertEqual(meta['machine_shape'],'NvidiaTeslaT4')
            self.assertIn('shot-04-identity-study-b.jpg',code)
            self.assertIn('run-motion-pilot-tall-v6.mp4',code)
            self.assertNotIn('mafia-full-body-ai-v2_1.png',code)
            self.assertNotIn('zrok',code.lower())
            self.assertLess(len(code),100_000)
            compile(code,'test-notebook','exec')

    def test_real_motion_preflight_and_render_are_separate_and_private(self):
        for stage in ('preflight','render'):
            with tempfile.TemporaryDirectory() as tmp:
                subprocess.run([sys.executable,str(HERE/'make_onetoall_real_pilot.py'),'--stage',stage,'--user','test-user','--slug','test-real','--out',tmp,'--dataset','test-user/test-driver'],check=True,capture_output=True)
                meta=json.loads((pathlib.Path(tmp)/'kernel-metadata.json').read_text())
                code=''.join(json.loads((pathlib.Path(tmp)/'main.ipynb').read_text())['cells'][0]['source'])
                self.assertTrue(meta['is_private'])
                self.assertIn("'/tmp/monarch-real-driver.mp4'",code)
                self.assertNotIn('mafia-full-body-ai-v2_1.png',code)
                compile(code,'test-real-notebook','exec')
                if stage=='preflight': self.assertIn('PrivateAuditSink',code)
                self.assertIn("'align_to': 'ref'",code)

if __name__=='__main__': unittest.main()

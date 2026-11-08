import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('probe',Path(__file__).with_name('zack-access-probe.py'))
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

class AccessProbeTests(unittest.TestCase):
    def test_scrubs_credentials_and_stream_urls(self):
        with patch.object(p,'KEY','secret-test'):
            value=p.clean('secret-test https://example.com/stream?token=abc message')
        self.assertNotIn('secret-test',value)
        self.assertNotIn('token=abc',value)

    def test_channel_identity_not_display_name(self):
        item={'id':'x','snippet':{'title':'clip','channelId':'wrong','channelTitle':'Zack D. Films'},'contentDetails':{'duration':'PT31S'}}
        row=p.public_fields(item,'correct')
        self.assertFalse(row['original_channel_verified'])
        self.assertFalse(row['full_frame_manual_review'])
        self.assertFalse(row['continuous_audio_review'])

    def test_bot_denial_stops_remaining_media_attempts(self):
        ids=list(p.SEEDS)+['extra-a','extra-b','extra-c']
        def fake_api(endpoint,**kw):
            if endpoint=='channels': return {'items':[{'id':'owner','snippet':{'title':'Zack D. Films'}}]}
            if endpoint=='search': return {'items':[{'id':{'videoId':ids[7+p.QUERIES.index(kw['q'])]}}]}
            return {'items':[{'id':v,'snippet':{'title':v,'channelId':'owner','channelTitle':'Zack D. Films'},'contentDetails':{'duration':'PT31S'}} for v in ids]}
        def denied(row,folder): row.update(media_status='retrieval_failed',diagnostic='Sign in to confirm you are not a bot')
        with tempfile.TemporaryDirectory() as tmp,patch.object(p,'OUT',Path(tmp)),patch.object(p,'KEY','fixture'),patch.object(p,'api',side_effect=fake_api),patch.object(p,'media_test',side_effect=denied) as attempt:
            p.main()
            report=json.loads((Path(tmp)/'access-probe.json').read_text())
        self.assertEqual(attempt.call_count,1)
        self.assertEqual(report['verified_original_metadata_count'],10)
        self.assertEqual(report['new_av_acquired_and_decoded_count'],0)
        self.assertEqual(sum(x['media_status']=='not_attempted_route_denied_on_pilot' for x in report['public_originals']),9)
        self.assertTrue(report['production_hold'])

    def test_missing_key_never_becomes_fake_acquisition(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(p,'OUT',Path(tmp)),patch.object(p,'KEY',None),patch.object(p,'media_test') as attempt:
            p.main()
            report=json.loads((Path(tmp)/'access-probe.json').read_text())
        attempt.assert_not_called()
        self.assertEqual(report['new_av_acquired_and_decoded_count'],0)
        self.assertTrue(report['errors'])

if __name__=='__main__':unittest.main()

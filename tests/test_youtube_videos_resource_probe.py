import unittest
from unittest.mock import patch
from scripts.youtube_videos_resource_probe import normalize,run

class VideosResourceTests(unittest.TestCase):
    def test_missing_key_is_explicit(self):
        with patch.dict('os.environ', {'YOUTUBE_API_KEY':''}):
            self.assertEqual(run()['result'],'no_configured_key')
    def test_normalize_missing_fields(self):
        result=normalize({'id':'x','status':{'embeddable':False}})
        self.assertEqual(result['id'],'x')
        self.assertIs(result['embeddable'],False)
        self.assertIsNone(result['caption_flag'])
        self.assertEqual(result['thumbnail_urls'],{})
        self.assertFalse(result['player_embed_html_present'])
    def test_normalize_values(self):
        result=normalize({'id':'x','snippet':{'title':'Title','thumbnails':{'default':{'url':'https://example.test'}}},'contentDetails':{'caption':'false'},'status':{'license':'youtube'}})
        self.assertEqual(result['title'],'Title')
        self.assertEqual(result['caption_flag'],'false')
        self.assertEqual(result['youtube_license_field'],'youtube')
        self.assertEqual(result['thumbnail_urls']['default'],'https://example.test')
if __name__=='__main__':unittest.main()

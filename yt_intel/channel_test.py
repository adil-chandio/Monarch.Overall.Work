"""Offline regressions for API channel routing and inventory completeness."""
import json
import unittest
from unittest.mock import patch
from . import client

CID = 'UC' + 'a' * 22
PROFILE = {'id': CID, 'snippet': {'title': 'Test'},
           'contentDetails': {'relatedPlaylists': {'uploads': 'UUtest'}}}


class ChannelTests(unittest.TestCase):
    def test_api_handle_never_uses_blocked_web(self):
        def api(endpoint, params, op):
            if endpoint == 'channels':
                self.assertEqual(params['forHandle'], 'extinct_life')
                return {'items': [PROFILE]}
            return {'items': []}
        with patch.object(client, 'API_KEY', 'test'), patch.object(client, '_api', side_effect=api), \
             patch.object(client.http, 'get', side_effect=AssertionError('web must not run')):
            r = client.channel('https://youtube.com/@extinct_life?si=foo')
        self.assertEqual(r.status, 'empty')
        self.assertTrue(json.loads(r.detail)['inventory_complete'])

    def test_pagination_and_deduplication(self):
        def api(endpoint, params, op):
            if endpoint == 'channels':
                self.assertEqual(params['id'], CID)
                return {'items': [PROFILE]}
            if 'pageToken' not in params:
                return {'items': [{'contentDetails': {'videoId': 'v1'}}], 'nextPageToken': 'page2'}
            return {'items': [{'contentDetails': {'videoId': 'v1'}}, {'contentDetails': {'videoId': 'v2'}}]}
        with patch.object(client, '_api', side_effect=api), \
             patch.object(client, 'videos', return_value=client.Corpus('videos', 'api', items=[{'id': 'v1'}, {'id': 'v2'}])) as videos:
            r = client.channel_uploads(CID)
        self.assertEqual(r.status, 'ok')
        videos.assert_called_once_with(['v1', 'v2'])

    def test_page_cap_is_not_complete(self):
        with patch.object(client, '_api', side_effect=[{'items': [PROFILE]}, {'items': [], 'nextPageToken': 'more'}]):
            r = client.channel_uploads('@test', max_pages=1)
        self.assertEqual(r.status, 'partial')
        self.assertFalse(json.loads(r.detail)['inventory_complete'])

    def test_unavailable_video_is_reported(self):
        with patch.object(client, '_api', side_effect=[{'items': [PROFILE]},
             {'items': [{'contentDetails': {'videoId': 'missing'}}]}]), \
             patch.object(client, 'videos', return_value=client.Corpus('videos', 'api', items=[])):
            r = client.channel_uploads('@test')
        self.assertEqual(r.status, 'partial')
        self.assertEqual(json.loads(r.detail)['missing_video_ids'], ['missing'])

    def test_error_scrubs_key(self):
        with patch.object(client, '_api', side_effect=RuntimeError('403 https://example.test?key=secret-value')):
            r = client.channel_uploads('@test')
        self.assertEqual(r.status, 'error')
        self.assertNotIn('secret-value', r.detail)

    def test_channel_not_found(self):
        with patch.object(client, '_api', return_value={'items': []}):
            self.assertEqual(client.channel_uploads('@absent').status, 'empty')

    def test_web_fallback_retained_without_key(self):
        with patch.object(client, 'API_KEY', ''), patch.object(client.http, 'get', return_value=b'no channel data'):
            r = client.channel('@test')
        self.assertEqual(r.lane, 'web')
        self.assertEqual(r.status, 'blocked')


if __name__ == '__main__':
    unittest.main()

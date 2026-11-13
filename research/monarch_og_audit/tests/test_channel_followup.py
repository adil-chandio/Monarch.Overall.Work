import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from channel_followup import BoundedAPI, collect, resolve_handles, validate_config
from collect_youtube import API


class ConfigTests(unittest.TestCase):
    def test_committed_reference_config_is_valid_and_unique(self):
        config = json.loads((Path(__file__).resolve().parents[1] / 'reference_channels.json').read_text())
        ids, handles = validate_config(config)
        self.assertEqual(ids, {})
        self.assertGreaterEqual(len(handles), 20)
        self.assertEqual(len({item['handle'].lower() for item in handles}), len(handles))

    def test_invalid_or_duplicate_handles_are_rejected(self):
        item = {'handle': '@Example', 'expected_title': 'Example', 'purpose': 'comparison'}
        with self.assertRaises(ValueError):
            validate_config({'handles': [item, dict(item, handle='@example')]})
        with self.assertRaises(ValueError):
            validate_config({'handles': [dict(item, handle='no-at')]})

    def test_resolution_distinguishes_mismatch_missing_and_error(self):
        class Fake:
            calls = []
            def get(self, resource, **params):
                handle = params['forHandle']
                self.calls.append({'reason': 'rateLimitExceeded' if handle == '@Error' else None})
                if handle == '@Error': return None
                if handle == '@Missing': return {'items': []}
                return {'items': [{'id': 'UC' + 'a'*22, 'snippet': {'title': ' Correct  Name '}}]}
        handles = [
            {'handle':'@Match', 'expected_title':'correct name', 'purpose':'x'},
            {'handle':'@Wrong', 'expected_title':'different', 'purpose':'y'},
            {'handle':'@Missing', 'expected_title':'missing', 'purpose':'z'},
            {'handle':'@Error', 'expected_title':'error', 'purpose':'z'},
        ]
        targets, results = resolve_handles(Fake(), handles, {})
        self.assertEqual([r['status'] for r in results], ['resolved_name_match', 'title_mismatch', 'not_found', 'request_error'])
        self.assertEqual(targets, {'UC' + 'a'*22:'x'})
        self.assertEqual(results[-1]['api_reason'], 'rateLimitExceeded')


class BoundedRequestTests(unittest.TestCase):
    def test_rate_limit_retry_and_quota_circuit(self):
        replies = iter([(None, 429, 'rateLimitExceeded'), ({'items':[]}, 200, None), (None, 403, 'quotaExceeded')])
        def get(self, resource, **params):
            payload, status, reason = next(replies)
            self.calls.append({'resource':resource, 'http_status':status, 'reason':reason})
            return payload
        sleeps = []
        with patch.object(API, 'get', get):
            api = BoundedAPI('not-a-real-key', sleep=sleeps.append)
            self.assertEqual(api.get('channels'), {'items':[]})
            self.assertEqual(sleeps, [0.25, 5])
            self.assertIsNone(api.get('channels'))
            self.assertTrue(api.circuit_open)
            self.assertIsNone(api.get('videos'))
            self.assertEqual(api.calls[-1]['reason'], 'backoff_circuit_open')
            self.assertEqual(len(api.calls), 4)


class CollectionTests(unittest.TestCase):
    def test_old_format_samples_are_separate_and_future_is_not_invented(self):
        cid = 'UC' + 'a'*22
        class Fake:
            calls = []
            server_dates = []
            def batch(self, resource, ids, part):
                if resource == 'channels':
                    return [{'id':cid, 'snippet':{'title':'Reference'}, 'contentDetails':{'relatedPlaylists':{'uploads':'UU-list'}}, 'statistics':{}}]
                return [
                    {'id':'short', 'snippet':{'publishedAt':'2026-10-22T00:00:00Z'}, 'contentDetails':{'duration':'PT30S'}, 'statistics':{'viewCount':'4'}},
                    {'id':'long', 'snippet':{'publishedAt':'2026-10-22T00:00:00Z'}, 'contentDetails':{'duration':'PT5M'}, 'statistics':{'viewCount':'8'}},
                    {'id':'new', 'snippet':{'publishedAt':'2026-11-10T00:00:00Z'}, 'contentDetails':{'duration':'PT30S'}, 'statistics':{'viewCount':'12'}},
                ]
            def get(self, resource, **params):
                self.calls.append({'reason':None})
                return {'items':[{'contentDetails':{'videoId':name, 'videoPublishedAt':date}} for name, date in [
                    ('new','2026-11-10T00:00:00Z'),('short','2026-10-22T00:00:00Z'),('long','2026-10-22T00:00:00Z')]]}
        data = collect(Fake(), {cid:'test'})
        sample = data['channel_samples'][0]
        self.assertEqual(sample['format_samples']['short_candidate_le60s'], ['short'])
        self.assertEqual(sample['format_samples']['long_proxy_ge4min'], ['long'])
        self.assertEqual(sample['format_samples']['ambiguous_61_to_239s'], [])
        self.assertIn('not verified as of the trusted date', data['date_warning'])


if __name__ == '__main__':
    unittest.main()

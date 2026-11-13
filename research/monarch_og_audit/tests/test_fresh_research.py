import hashlib
from pathlib import Path
import stat
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fresh_youtube import format_bucket, focus_samples, search_plan, within_window, TRUSTED_END, PUBLICATION_END
from inspect_archive import inspect_archive


class FormatTests(unittest.TestCase):
    def test_duration_boundaries_are_not_automatic_shorts_labels(self):
        self.assertEqual(format_bucket(None), 'unknown')
        self.assertEqual(format_bucket(0), 'unknown')
        self.assertEqual(format_bucket(60), 'short_candidate_le60s')
        self.assertEqual(format_bucket(60.01), 'ambiguous_61_to_239s')
        self.assertEqual(format_bucket(180), 'ambiguous_61_to_239s')
        self.assertEqual(format_bucket(239.99), 'ambiguous_61_to_239s')
        self.assertEqual(format_bucket(240), 'long_proxy_ge4min')

    def test_window_is_inclusive_start_exclusive_end_with_timezone(self):
        self.assertTrue(within_window('2026-11-05T00:00:00Z', '2026-11-05T00:00:00Z', TRUSTED_END))
        self.assertFalse(within_window('2026-11-06T00:00:00Z', '2026-11-05T00:00:00Z', TRUSTED_END))
        self.assertFalse(within_window('2026-11-05T00:00:00', '2026-11-05T00:00:00Z', TRUSTED_END))
        self.assertLess(TRUSTED_END, PUBLICATION_END)

    def test_mature_format_groups_are_separate_and_capped(self):
        videos = {
            'a': {'published_at':'2026-10-22T23:59:59Z','duration_seconds':15,'views':500},
            'b': {'published_at':'2026-10-22T23:59:59Z','duration_seconds':350,'views':3},
            'c': {'published_at':'2026-10-23T00:00:00Z','duration_seconds':15,'views':1000},
            'd': {'published_at':'2026-10-20T00:00:00Z','duration_seconds':100,'views':100},
            'e': {'published_at':'2026-10-20T00:00:00Z','duration_seconds':15,'views':None},
            'f': {'published_at':'2026-10-20T00:00:00Z','duration_seconds':20,'views':20},
        }
        result=focus_samples(list(videos),videos,cap=1)
        self.assertEqual(result['short_candidate_le60s'], ['a'])
        self.assertEqual(result['long_proxy_ge4min'], ['b'])
        self.assertEqual(result['ambiguous_61_to_239s'], ['d'])

    def test_search_plan_keeps_formats_and_selection_explicit(self):
        plan=search_plan()
        self.assertEqual(len(plan),39)
        self.assertEqual(sum(x['bucket']=='short_candidate_le60s' for x in plan),18)
        self.assertEqual(sum(x['bucket']=='long_proxy_ge4min' for x in plan),21)
        self.assertTrue(all(x['duration_filter'] in ('short','medium','long') for x in plan))
        self.assertTrue(all(x['published_before']==PUBLICATION_END for x in plan))


class ArchiveTests(unittest.TestCase):
    def test_inventory_flags_unsafe_paths_and_symlinks_without_extracting(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'sample.zip'
            symlink=zipfile.ZipInfo('unsafe-link');symlink.create_system=3
            symlink.external_attr=(stat.S_IFLNK | 0o777) << 16
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('safe/ref.txt','public link')
                z.writestr('../traversal.txt','untrusted')
                z.writestr('C:\\absolute.exe','never executed')
                z.writestr(symlink,'../../outside')
            digest=hashlib.md5(path.read_bytes()).hexdigest()
            meta=inspect_archive(path,path.stat().st_size,digest)
            self.assertEqual(meta['entry_count'],4)
            self.assertFalse(meta['entries'][0]['unsafe_path'])
            self.assertTrue(meta['entries'][1]['unsafe_path'])
            self.assertTrue(meta['entries'][2]['unsafe_path'])
            self.assertTrue(meta['entries'][3]['symbolic_link'])
            self.assertEqual(sorted(p.name for p in Path(root).iterdir()),['sample.zip'])
            with self.assertRaises(ValueError):inspect_archive(path,path.stat().st_size,'not-the-md5')


if __name__=='__main__':unittest.main()

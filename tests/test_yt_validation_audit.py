import importlib.util,io,json,unittest,urllib.error
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('audit',Path(__file__).resolve().parents[1]/'scripts/yt-validation-audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class AuditTests(unittest.TestCase):
 def test_bounds(self):
  for r in [{},{'queries':['x']*5,'orders':['date']},{'queries':['x'],'orders':['bad']},{'queries':['x'],'orders':['date'],'results_per_query':True}]:
   with self.assertRaises(ValueError):a.validate(r)
 def test_good_request(self):self.assertEqual(a.validate({'queries':['x'],'orders':['viewCount']})['queries'],['x'])
 def test_permanent_403_not_retried_or_leaked(self):
  calls=[]
  def blocked(*args,**kwargs):calls.append(1);raise urllib.error.HTTPError('secret-url',403,'Forbidden',{},io.BytesIO(b'{"error":{"errors":[{"reason":"keyInvalid"}]}}'))
  api=a.Api('PRIVATE',blocked,sleep=lambda _:self.fail('must not sleep'))
  with self.assertRaises(a.ApiFailure) as ctx:api.get('videos',part='id')
  self.assertEqual(len(calls),1);self.assertNotIn('PRIVATE',str(ctx.exception));self.assertNotIn('secret-url',str(ctx.exception))
 def test_transient_bounded(self):
  def fail(*args,**kwargs):raise urllib.error.HTTPError('',503,'',{},io.BytesIO(b'{}'))
  api=a.Api('x',fail,sleep=lambda _:None)
  with self.assertRaises(a.ApiFailure):api.get('search',part='snippet')
  self.assertEqual(api.attempts,3);self.assertEqual(api.units,300)
 def test_missing_fields_not_zeroed(self):
  class Fake:
   units=0;attempts=0
   def get(self,endpoint,**kwargs):
    if endpoint=='search':return {'items':[{'id':{'videoId':'abcdefghijk'}}]}
    if endpoint=='channels':return {'items':[]}
    if kwargs['part']=='id':return {'items':[]}
    return {'items':[{'id':'abcdefghijk','snippet':{'channelId':'c'}}]}
  r=a.collect(Fake(),{'queries':['x'],'orders':['date']});self.assertEqual(r['status'],'measured');self.assertEqual(r['videos'][0]['statistics'],{});self.assertIn('observed_at_utc',r['videos'][0])
 def test_partial_keeps_evidence(self):
  class Fake:
   units=0;attempts=0
   def get(self,endpoint,**kwargs):
    if endpoint=='search':return {'items':[{'id':{'videoId':'abcdefghijk'}}]}
    if kwargs.get('part')=='id':return {}
    raise a.ApiFailure(403,'quotaExceeded')
  r=a.collect(Fake(),{'queries':['x'],'orders':['date']});self.assertEqual(r['status'],'partial');self.assertEqual(len(r['searches']),1)
 def test_workflow_scoped_no_bot_push(self):
  s=(Path(__file__).resolve().parents[1]/'.github/workflows/yt-validation-audit.yml').read_text();self.assertIn('arena/ba8d901e-monarch-overall-work',s);self.assertIn('contents: write',s);self.assertIn('/contents/production/extinct-life/research/api-results/latest.json',s);self.assertIn("github.ref == 'refs/heads/arena/ba8d901e-monarch-overall-work'",s);self.assertNotIn('git push',s);self.assertNotIn('github.event.inputs',s)
 def test_actions_pinned_and_runner_stable(self):
  import re
  s=(Path(__file__).resolve().parents[1]/'.github/workflows/yt-validation-audit.yml').read_text()
  self.assertIn('runs-on: ubuntu-24.04',s);self.assertEqual(len(re.findall(r'uses: actions/[a-z-]+@[0-9a-f]{40}',s)),3)
if __name__=='__main__':unittest.main()

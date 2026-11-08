"""Try lawful unauthenticated public video download and comments; never bypass access controls."""
import json, os, pathlib, subprocess, tempfile, urllib.error, urllib.parse, urllib.request
ids=['ZTKh3IDAkTg','60rbnH1eUF0','l94zC4w-Dzo','8qm04TYrVPY','hUE2SD3_h4U','5TRMU4irQb4','JoO1KFLhTMY','8atK0pF4oJY','WB9P8WZtUA4','VE4GMIi39uQ','Tgopx8TcaiM','C637UcpHfNY']
key=os.environ.get('YOUTUBE_API_KEY','');results=[]
def api(vid):
 q=urllib.parse.urlencode({'part':'snippet','videoId':vid,'maxResults':20,'order':'relevance','textFormat':'plainText','key':key})
 try:
  with urllib.request.urlopen('https://www.googleapis.com/youtube/v3/commentThreads?'+q,timeout=20) as f:body=json.load(f)
  return {'status':'ok','items':[{'text':x['snippet']['topLevelComment']['snippet']['textDisplay'],'likes':x['snippet']['topLevelComment']['snippet']['likeCount']} for x in body.get('items',[])]}
 except urllib.error.HTTPError as e:return {'status':'unavailable','http':e.code}
 except Exception as e:return {'status':'error','error':type(e).__name__}
with tempfile.TemporaryDirectory() as d:
 for v in ids:
  row={'id':v,'comments':api(v),'playback_status':'unknown'}
  try:
   r=subprocess.run(['yt-dlp','--no-playlist','--no-warnings','--socket-timeout','12','--retries','0','--no-progress','-f','worst[height<=480]/worst','-o',f'{d}/{v}.%(ext)s','https://www.youtube.com/watch?v='+v],capture_output=True,text=True,timeout=45)
   files=list(pathlib.Path(d).glob(v+'.*'))
   if r.returncode==0 and files:
    row['playback_status']='downloaded_public_video';row['bytes']=files[0].stat().st_size
    # Do not publish or commit third-party audiovisual media here.
   else:
    row['playback_status']='download_unavailable';row['diagnostic']=r.stderr[-500:].replace('\n',' ') if r.stderr else 'no downloadable video returned'
  except subprocess.TimeoutExpired:row['playback_status']='timeout'
  except Exception as e:row['playback_status']='error';row['diagnostic']=type(e).__name__
  print(v,row['playback_status'],flush=True);results.append(row)
p=pathlib.Path('audit-output/stickman-media-probe.json');p.parent.mkdir(exist_ok=True);p.write_text(json.dumps({'method':'Public yt-dlp without cookies or authentication; comments via YouTube Data API; user-selected topical sample, not representative. Public comments are not audience geography or retention data.','videos':results},ensure_ascii=False,indent=2))

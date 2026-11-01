"""Run exactly three harmless requests; stop loopback listener in finally."""
import base64
import datetime
import json
from pathlib import Path
import subprocess

pods=json.loads(subprocess.run(['kubectl','-n','scanner','get','pods','-l','app=backend','-o','json'],capture_output=True,text=True,check=True).stdout)['items']
pod=next(p['metadata']['name'] for p in pods if not p['metadata'].get('deletionTimestamp') and all(c['ready'] for c in p['status']['containerStatuses']))
code='''import subprocess,sys,time,uuid,json,urllib.request,urllib.error
p=subprocess.Popen([sys.executable,'-m','backend.demo'])
results=[]
try:
    for attempt in range(30):
        import socket
        with socket.socket() as s:
            if s.connect_ex(('127.0.0.1',8001))==0: break
        time.sleep(0.3)
    else: raise RuntimeError('Loopback listener did not start')
    for port,path,expected in [(8000,'/health/live',200),(8000,'/milestone6-unknown-route',404),(8001,'/internal/demo/http-503',503)]:
        request_id=str(uuid.uuid4())
        req=urllib.request.Request(f'http://127.0.0.1:{port}{path}',headers={'X-Request-ID':request_id})
        try: r=urllib.request.urlopen(req,timeout=15)
        except urllib.error.HTTPError as e: r=e
        status=r.code
        assert status==expected,(path,status)
        assert r.headers['X-Request-ID']==request_id
        result={'path':path,'status':status,'request_id':request_id}
        if status==503: result['body']=json.loads(r.read())
        results.append(result)
    print(json.dumps({'pod':__POD__,'requests':results}),flush=True)
finally:
    p.terminate()
    try:p.wait(timeout=15)
    except subprocess.TimeoutExpired:p.kill();p.wait()
'''.replace('__POD__',repr(pod))
encoded=base64.b64encode(code.encode()).decode()
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
r=subprocess.run(['kubectl','-n','scanner','exec',pod,'-c','backend','--','python','-c',f"import base64;exec(base64.b64decode('{encoded}'))"],capture_output=True,text=True,timeout=90)
if r.returncode:
    print(r.stderr)
    raise RuntimeError('Controlled probe failed')
data=json.loads(r.stdout)
data['start']=start
data['end']=datetime.datetime.now(datetime.timezone.utc).isoformat()
Path('docs/milestone6/evidence/logging/controlled-requests.json').write_text(json.dumps(data,indent=2))
print(json.dumps(data,indent=2))

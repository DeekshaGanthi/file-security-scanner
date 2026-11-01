"""Read-only verification of real correlated logs and metric time series."""
import datetime
import json
from pathlib import Path
import subprocess
import requests

evidence=Path('docs/milestone6/evidence')
probe=json.loads((evidence/'logging/controlled-requests.json').read_text())
token=subprocess.run(['gcloud.cmd','auth','print-access-token'],capture_output=True,text=True,check=True).stdout.strip()
s=requests.Session();s.headers.update({'Authorization':'Bearer '+token})
project='projects/file-security-scanner'
ids=[r['request_id'] for r in probe['requests']]
correlation='('+' OR '.join(f'jsonPayload.request_id="{i}"' for i in ids)+')'
scope='resource.type="k8s_container" AND resource.labels.cluster_name="scanner-gke" AND resource.labels.namespace_name="scanner" AND resource.labels.container_name="backend"'

def logs(filter):
    since=(datetime.datetime.fromisoformat(probe['start'])-datetime.timedelta(seconds=30)).isoformat()
    body={'resourceNames':[project],'filter':filter+f' AND timestamp>="{since}"','pageSize':100,'orderBy':'timestamp asc'}
    entries=[]
    for _ in range(10):
        r=s.post('https://logging.googleapis.com/v2/entries:list',json=body,timeout=40)
        r.raise_for_status();data=r.json();entries.extend(data.get('entries',[]))
        if not data.get('nextPageToken'):return entries
        body['pageToken']=data['nextPageToken']
    raise RuntimeError('Log query pagination exceeded bounded verification limit')

entries=logs(scope+' AND '+correlation)
if len(entries)!=3:
    print(f'Waiting for log ingestion: {len(entries)}/3 correlated entries')
else:
    for request in probe['requests']:
        matches=[e for e in entries if e.get('jsonPayload',{}).get('request_id')==request['request_id']]
        assert len(matches)==1
        payload=matches[0]['jsonPayload']
        assert payload['http_status']==request['status'] and type(payload['http_status']) is int
        assert payload['event']=='http_request' and payload['duration_ms']>=0
    r=s.get('https://logging.googleapis.com/v2/'+project+'/metrics/scanner_http_5xx_count',timeout=30)
    r.raise_for_status();metric=r.json()
    matched=logs(metric['filter']+'\n'+correlation)
    assert len(matched)==1 and matched[0]['jsonPayload']['controlled_failure'] is True
    (evidence/'logging/correlated-cloud-logs.json').write_text(json.dumps(entries,indent=2))
    (evidence/'logging/metric-definition.json').write_text(json.dumps(metric,indent=2))
    (evidence/'logging/filter-verification.json').write_text(json.dumps({'requests_checked':3,'one_completion_each':True,'metric_matches':1,'matched_request_id':matched[0]['jsonPayload']['request_id'],'excluded_statuses':[200,404]},indent=2))
    print('Cloud Logging: exactly one JSON completion for each 200/404/503; metric filter matches only controlled 503')

start=datetime.datetime.fromisoformat(probe['start'])-datetime.timedelta(minutes=2)
now=datetime.datetime.now(datetime.timezone.utc)
r=s.get('https://monitoring.googleapis.com/v3/'+project+'/timeSeries',params={
    'filter':'metric.type="logging.googleapis.com/user/scanner_http_5xx_count" AND '+scope,
    'interval.startTime':start.isoformat(),'interval.endTime':now.isoformat(),'view':'FULL'},timeout=40)
r.raise_for_status();data=r.json()
series=data.get('timeSeries',[])
points=[p for t in series for p in t.get('points',[])]
if points:
    total=sum(int(p['value'].get('int64Value',0)) for p in points)
    (evidence/'logging/metric-timeseries.json').write_text(json.dumps({'query_start':start.isoformat(),'query_end':now.isoformat(),'observed_error_count':total,'response':data},indent=2))
    print(f'Monitoring: observed actual DELTA error count {total} in the isolated test window')
else:
    print('Monitoring: metric points not yet ingested; pending, not recorded as zero')

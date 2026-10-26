"""Run inside one backend pod. Creates one harmless scan and preserves all history."""
import json
import uuid
import requests
from google.cloud import storage
from backend.database import get_connection, check_database

def counts():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            result = {}
            for table in ('scans', 'indicators', 'llm_reports'):
                cursor.execute(f'SELECT count(*) AS count FROM {table}')
                result[table] = cursor.fetchone()['count']
            return result

check_database()
print('Private PostgreSQL SELECT 1: PASS', flush=True)
before = counts()
print(json.dumps({'counts_before': before}), flush=True)
for path in ('live', 'ready'):
    r = requests.get(f'http://127.0.0.1:8000/health/{path}', timeout=15)
    r.raise_for_status()
    print(json.dumps({'health': path, 'status': r.status_code, 'body': r.json()}), flush=True)
filename = f'milestone5-verification-{uuid.uuid4()}.txt'
r = requests.post('http://127.0.0.1:8000/scan',
    files={'file': (filename, b'Harmless course project verification file. No executable content.', 'text/plain')},
    timeout=(5, 180))
r.raise_for_status()
scan = r.json()
history = requests.get('http://127.0.0.1:8000/scans', timeout=15)
history.raise_for_status()
assert any(x['id'] == scan['scan_id'] for x in history.json())
assert len(history.json()) >= before['scans']+1
client = storage.Client()
matches = []
for blob in client.list_blobs('file-security-scanner-uploads-2026', prefix='uploads/'):
    if (blob.metadata or {}).get('original_filename') == filename:
        matches.append(blob.name)
assert len(matches) == 1, 'Expected exactly one GCS object with test filename'
print(json.dumps({'scan_id': scan['scan_id'], 'filename': filename,
    'risk': scan['risk'], 'gemini': scan['gemini_analysis'],
    'history_records': len(history.json()), 'gcs_objects': matches,
    'counts_after': counts()}), flush=True)
print('Scan persistence, history and private GCS: PASS', flush=True)

"""Bounded traffic to existing process health endpoint via local port-forward.

No database writes, cloud API calls, test backdoor or artificial CPU loop.
May require tuning concurrency; success is observed HPA scaling, never assumed.
"""
import argparse
import concurrent.futures
import time
import urllib.request

p = argparse.ArgumentParser()
p.add_argument('--url', default='http://127.0.0.1:18000/health/live')
p.add_argument('--seconds', type=int, default=180)
p.add_argument('--workers', type=int, default=32)
a = p.parse_args()
if not a.url.startswith('http://127.0.0.1:') or not a.url.endswith('/health/live'):
    p.error('Only local port-forward to /health/live is allowed')
if not 1 <= a.seconds <= 300 or not 1 <= a.workers <= 128:
    p.error('Limits: duration 1..300 seconds, workers 1..128')
deadline = time.monotonic()+a.seconds
def worker(_):
    ok = failed = 0
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(a.url, timeout=3) as r:
                r.read()
                ok += r.status == 200
        except Exception:
            failed += 1
    return ok, failed
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as executor:
    results = list(executor.map(worker, range(a.workers)))
print({'successes': sum(x[0] for x in results), 'failures': sum(x[1] for x in results)})

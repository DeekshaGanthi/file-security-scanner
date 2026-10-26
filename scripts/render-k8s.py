"""Render a complete deployment; refuses placeholder images/hostnames."""
import argparse
import json
import re
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--hostname', required=True)
p.add_argument('--frontend-image', required=True)
p.add_argument('--backend-image', required=True)
p.add_argument('--output', default='milestone5-tmp/rendered')
a = p.parse_args()
if not re.fullmatch(r'[a-z0-9][a-z0-9.-]+\.[a-z]{2,}', a.hostname):
    p.error('A real lowercase DNS hostname is required')
for image in [a.frontend_image, a.backend_image]:
    if not re.fullmatch(r'us-central1-docker.pkg.dev/file-security-scanner/file-security-scanner-repo/[a-z0-9-]+@sha256:[a-f0-9]{64}', image):
        p.error('Use an immutable image digest in the existing Artifact Registry repository')
out = Path(a.output)
out.mkdir(parents=True, exist_ok=True)
for path in Path('k8s').glob('*.yaml'):
    obj = json.loads(path.read_text())
    if obj['kind'] == 'Deployment':
        component = obj['metadata']['name']
        obj['spec']['template']['spec']['containers'][0]['image'] = getattr(a, component+'_image')
    (out/path.name).write_text(json.dumps(obj, indent=2)+'\n')
certificate = {'apiVersion': 'networking.gke.io/v1', 'kind': 'ManagedCertificate',
    'metadata': {'name': 'scanner-tls', 'namespace': 'scanner'},
    'spec': {'domains': [a.hostname]}}
ingress = {'apiVersion': 'networking.k8s.io/v1', 'kind': 'Ingress',
    'metadata': {'name': 'scanner', 'namespace': 'scanner', 'annotations': {
        'kubernetes.io/ingress.class': 'gce',
        'kubernetes.io/ingress.global-static-ip-name': 'scanner-gke-ip',
        'networking.gke.io/managed-certificates': 'scanner-tls',
        'networking.gke.io/v1beta1.FrontendConfig': 'https-redirect'}},
    'spec': {'rules': [{'host': a.hostname, 'http': {'paths': [{'path': '/',
        'pathType': 'Prefix', 'backend': {'service': {'name': 'frontend', 'port': {'number': 8501}}}}]}}]}}
for name, obj in [('managed-certificate.yaml', certificate), ('ingress.yaml', ingress)]:
    (out/name).write_text(json.dumps(obj, indent=2)+'\n')
print(f'Rendered {len(list(out.glob("*.yaml")))} resources to {out}')

import json
from pathlib import Path


def load(name):
    return json.loads((Path('k8s')/name).read_text())


def test_probes_and_selectors_match_running_ports():
    for component in ['backend', 'frontend']:
        d = load(f'{component}-deployment.yaml')['spec']
        service = load(f'{component}-service.yaml')['spec']
        pdb = load(f'{component}-pdb.yaml')['spec']
        assert d['replicas'] >= 2
        assert d['selector']['matchLabels'] == service['selector'] == pdb['selector']['matchLabels']
        c = d['template']['spec']['containers'][0]
        port = c['ports'][0]['containerPort']
        assert c['readinessProbe']['httpGet']['port'] == port == service['ports'][0]['targetPort']
        if component == 'backend':
            assert c['readinessProbe']['httpGet']['path'] != c['livenessProbe']['httpGet']['path']
        hpa = load(f'{component}-hpa.yaml')['spec']
        assert hpa['minReplicas'] >= 2
        assert hpa['scaleTargetRef']['name'] == component

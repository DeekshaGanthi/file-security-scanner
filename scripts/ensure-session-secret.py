"""Emit only to kubectl stdin; do not run standalone in a recorded terminal."""
import json
import secrets
print(json.dumps({
    'apiVersion': 'v1', 'kind': 'Secret',
    'metadata': {'name': 'streamlit-session', 'namespace': 'scanner'},
    'type': 'Opaque', 'stringData': {'cookie-secret': secrets.token_urlsafe(48)}
}))

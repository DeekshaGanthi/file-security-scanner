"""Run via stdin inside the backend image without cloud credentials."""
import os
from unittest.mock import patch
os.environ['GCS_BUCKET_NAME'] = 'smoke-test-no-cloud-calls'
from fastapi.testclient import TestClient
from backend.main import app

with TestClient(app) as client:
    with patch('backend.health.check_database', side_effect=RuntimeError('offline')):
        assert client.get('/health/live').status_code == 200
        assert client.get('/health/ready').status_code == 503
    with patch('backend.health.check_database'):
        assert client.get('/health/ready').status_code == 200
    with patch('backend.main.upload_file_to_gcs') as upload:
        with patch.dict(os.environ, {'MAX_UPLOAD_BYTES': '3'}):
            response = client.post('/scan', files={'file': ('safe.txt', b'four', 'text/plain')})
            assert response.status_code == 413
            upload.assert_not_called()
print('Backend import, live, ready, outage isolation and upload limit: PASS')

from backend.gemini import get_gemini_analysis
class RateLimitError(Exception):
    pass
with patch('backend.secrets.secret_value', return_value='test-only'), patch('backend.gemini.genai.Client') as client:
    client.return_value.interactions.create.side_effect = RateLimitError('must-not-leak')
    result = get_gemini_analysis({}, {})
    assert not result['success']
    assert 'rate limit' in result['message']
    assert 'must-not-leak' not in str(result)
print('Gemini rate-limit handling: PASS')

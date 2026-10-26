"""Read-only pod verification; safe to record, no secret values printed."""
import requests
from backend.database import check_database
check_database()
print('Private PostgreSQL SELECT 1: PASS')
for path in ('live', 'ready'):
    response = requests.get(f'http://127.0.0.1:8000/health/{path}', timeout=15)
    response.raise_for_status()
    print(path, response.status_code, response.json())

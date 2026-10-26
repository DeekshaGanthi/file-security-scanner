"""List available model names without exposing keys or provider error messages."""
from google import genai
from backend.secrets import secret_value

try:
    client = genai.Client(api_key=secret_value('GEMINI_API_KEY'), http_options={'timeout': 15000})
    for model in client.models.list():
        if 'flash' in (model.name or ''):
            print(model.name, flush=True)
except Exception as exc:
    print({'error_type': type(exc).__name__, 'code': getattr(exc, 'code', None)}, flush=True)

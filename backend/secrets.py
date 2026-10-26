"""Read named secrets with ADC; never log payloads or create key files."""
import os
from functools import lru_cache


@lru_cache(maxsize=4)
def secret_value(env_name):
    value = os.getenv(env_name)
    if value:
        return value
    resource = os.getenv(f"{env_name}_SECRET")
    if not resource:
        raise RuntimeError(f"Missing configuration for {env_name}")
    from google.cloud import secretmanager
    response = secretmanager.SecretManagerServiceClient().access_secret_version(
        request={"name": resource}, timeout=5
    )
    return response.payload.data.decode("utf-8").strip()

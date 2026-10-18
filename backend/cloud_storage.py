"""
Google Cloud Storage Module
File Security Scanner - Milestone 4

Purpose:
    Store uploaded files in Google Cloud Storage instead of
    relying on persistent storage inside the Compute Engine VM.

Authentication:
    Uses Application Default Credentials (ADC).
    On Google Compute Engine, ADC uses the VM's attached
    service account automatically.

    No service account JSON key is required.
"""

import os
from google.cloud import storage


# ============================================================
# 1. Cloud Storage Configuration
# ============================================================

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

if not BUCKET_NAME:
    raise RuntimeError(
        "Missing required environment variable: GCS_BUCKET_NAME"
    )


# ============================================================
# 2. Upload File to Cloud Storage
# ============================================================

def upload_file_to_gcs(local_file_path, file_id, original_filename):
    """
    Upload a locally processed file to Google Cloud Storage.

    Args:
        local_file_path: Temporary path of the uploaded file.
        file_id: Unique UUID generated for the upload.
        original_filename: Original name of the uploaded file.

    Returns:
        str: Cloud Storage object path (gs://...).
    """

    # Use the VM's service account automatically.
    client = storage.Client()

    # Reference the configured private bucket.
    bucket = client.bucket(BUCKET_NAME)

    # Generate a unique object name to avoid collisions.
    # Do not use an untrusted filename as a storage path.
    object_name = f"uploads/{file_id}"

    # Upload the file.
    blob = bucket.blob(object_name)

    blob.metadata = {
        "original_filename": original_filename[:1024]
    }

    blob.upload_from_filename(local_file_path)

    # Return the storage location without making it public.
    return f"gs://{BUCKET_NAME}/{object_name}"
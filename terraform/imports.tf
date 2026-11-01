# Existing infrastructure: approved for import on November 1, 2026.
import {
  to = google_container_cluster.scanner
  id = "projects/file-security-scanner/locations/us-central1/clusters/scanner-gke"
}
import {
  to = google_sql_database_instance.scanner
  id = "projects/file-security-scanner/instances/file-scanner-postgres"
}
import {
  to = google_storage_bucket.uploads
  id = "file-security-scanner-uploads-2026"
}
import {
  to = google_artifact_registry_repository.images
  id = "projects/file-security-scanner/locations/us-central1/repositories/file-security-scanner-repo"
}
import {
  to = google_secret_manager_secret.database
  id = "projects/file-security-scanner/secrets/scanner-db-password"
}
import {
  to = google_secret_manager_secret.gemini
  id = "projects/file-security-scanner/secrets/gemini-api-key"
}

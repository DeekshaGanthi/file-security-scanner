data "google_project" "current" {}

resource "google_service_account" "deploy" {
  account_id   = "scanner-deploy"
  display_name = "GitHub scanner deployment (no keys)"
}
resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "scanner-github"
  display_name              = "Scanner GitHub Actions"
}
resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github"
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
  }
  attribute_condition = "assertion.repository == '${var.repository}' && assertion.ref == 'refs/heads/milestone6-deploy' && assertion.event_name in ['push', 'workflow_dispatch']"
  oidc { issuer_uri = "https://token.actions.githubusercontent.com" }
}
resource "google_service_account_iam_member" "github" {
  service_account_id = google_service_account.deploy.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.repository}"
}
resource "google_artifact_registry_repository_iam_member" "deploy" {
  location   = var.region
  repository = "file-security-scanner-repo"
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.deploy.email}"
}
resource "google_project_iam_member" "cluster_read" {
  project = var.project_id
  role    = "roles/container.clusterViewer"
  member  = "serviceAccount:${google_service_account.deploy.email}"
}

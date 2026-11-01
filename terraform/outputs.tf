output "workload_identity_provider" {
  value = google_iam_workload_identity_pool_provider.github.name
}
output "deployment_service_account" {
  value = google_service_account.deploy.email
}
output "dashboard_name" {
  value = google_monitoring_dashboard.scanner.id
}

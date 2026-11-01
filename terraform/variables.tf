variable "project_id" {
  type    = string
  default = "file-security-scanner"
}
variable "region" {
  type    = string
  default = "us-central1"
}
variable "cluster_name" {
  type    = string
  default = "scanner-gke"
}
variable "notification_email" {
  type      = string
  sensitive = true
  validation {
    condition     = can(regex("^[^@ ]+@[^@ ]+\\.[^@ ]+$", var.notification_email))
    error_message = "Supply the authorized notification recipient."
  }
}
variable "repository" {
  type    = string
  default = "DeekshaGanthi/file-security-scanner"
}

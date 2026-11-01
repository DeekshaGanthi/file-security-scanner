# Separate bootstrap requires explicit approval. It creates no application resources.
terraform {
  backend "gcs" {}
  required_version = ">= 1.14, < 2.0"
  required_providers {
    google = { source = "hashicorp/google", version = "~> 7.29.0" }
  }
}
provider "google" { project = "file-security-scanner" }
resource "google_storage_bucket" "state" {
  name                        = "file-security-scanner-tfstate-956088853573"
  project                     = "file-security-scanner"
  location                    = "US-CENTRAL1"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  versioning { enabled = true }
  lifecycle { prevent_destroy = true }
}

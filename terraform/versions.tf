terraform {
  required_version = ">= 1.14, < 2.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.29.0"
    }
  }
  # Configure only after reviewing the private, versioned state bucket.
  backend "gcs" {}
}

provider "google" {
  project = var.project_id
  region  = var.region
}

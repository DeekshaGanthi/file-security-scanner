# __generated__ by Terraform
# Please review these resources and move them into your main configuration files.

# __generated__ by Terraform from "projects/file-security-scanner/secrets/scanner-db-password"
resource "google_secret_manager_secret" "database" {
  annotations         = {}
  deletion_protection = false
  labels              = {}
  project             = "file-security-scanner"
  secret_id           = "scanner-db-password"
  tags                = null
  ttl                 = null
  version_aliases     = {}
  version_destroy_ttl = null
  replication {
    auto {
    }
  }
  lifecycle {
    prevent_destroy = true
  }
}

# __generated__ by Terraform from "projects/file-security-scanner/secrets/gemini-api-key"
resource "google_secret_manager_secret" "gemini" {
  annotations         = {}
  deletion_protection = false
  labels              = {}
  project             = "file-security-scanner"
  secret_id           = "gemini-api-key"
  tags                = null
  ttl                 = null
  version_aliases     = {}
  version_destroy_ttl = null
  replication {
    auto {
    }
  }
  lifecycle {
    prevent_destroy = true
  }
}

# __generated__ by Terraform from "projects/file-security-scanner/locations/us-central1/repositories/file-security-scanner-repo"
resource "google_artifact_registry_repository" "images" {
  cleanup_policy_dry_run = false
  description            = "Docker images for File Security Scanner"
  format                 = "DOCKER"
  kms_key_name           = null
  labels                 = {}
  location               = "us-central1"
  mode                   = "STANDARD_REPOSITORY"
  project                = "file-security-scanner"
  repository_id          = "file-security-scanner-repo"
  vulnerability_scanning_config {
    enablement_config = null
  }
  lifecycle {
    prevent_destroy = true
  }
}

# __generated__ by Terraform
resource "google_sql_database_instance" "scanner" {
  backupdr_backup          = null
  database_version         = "POSTGRES_18"
  deletion_protection      = true
  final_backup_description = null
  instance_type            = "CLOUD_SQL_INSTANCE"
  maintenance_version      = "POSTGRES_18_6.R20260712.01_33"
  name                     = "file-scanner-postgres"
  node_count               = 0
  project                  = "file-security-scanner"
  region                   = "us-central1"
  replica_names            = []
  root_password            = null # sensitive
  root_password_wo         = null
  root_password_wo_version = null
  replication_cluster {
    failover_dr_replica_name = null
  }
  settings {
    activation_policy            = "ALWAYS"
    auto_upgrade_enabled         = false
    availability_type            = "ZONAL"
    collation                    = null
    connector_enforcement        = "NOT_REQUIRED"
    deletion_protection_enabled  = true
    disk_autoresize              = true
    disk_autoresize_limit        = 0
    disk_size                    = 10
    disk_type                    = "PD_SSD"
    edition                      = "ENTERPRISE"
    enable_dataplex_integration  = true
    enable_google_ml_integration = false
    pricing_plan                 = "PER_USE"
    retain_backups_on_delete     = true
    tier                         = "db-f1-micro"
    time_zone                    = null
    user_labels                  = {}
    backup_configuration {
      binary_log_enabled             = false
      enabled                        = true
      location                       = "us"
      point_in_time_recovery_enabled = true
      start_time                     = "16:00"
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 7
        retention_unit   = "COUNT"
      }
    }
    data_cache_config {
      data_cache_enabled = false
    }
    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }
    final_backup_config {
      enabled        = true
      retention_days = 30
    }
    ip_configuration {
      allocated_ip_range                            = null
      custom_subject_alternative_names              = []
      enable_private_path_for_google_cloud_services = false
      ipv4_enabled                                  = false
      private_network                               = "projects/file-security-scanner/global/networks/default"
      server_ca_mode                                = "GOOGLE_MANAGED_CAS_CA"
      server_ca_pool                                = null
      ssl_mode                                      = "ENCRYPTED_ONLY"
      psc_config {
        allowed_consumer_projects = []
        network_attachment_uri    = null
        psc_enabled               = false
      }
    }
    location_preference {
      follow_gae_application = null
      secondary_zone         = null
      zone                   = "us-central1-c"
    }
    password_validation_policy {
      complexity                  = "COMPLEXITY_DEFAULT"
      disallow_username_substring = true
      enable_password_policy      = true
      min_length                  = 8
      password_change_interval    = null
      reuse_interval              = 0
    }
  }
  lifecycle {
    prevent_destroy = true
    # API returns unset day=0; provider rejects expressing that value in configuration.
    ignore_changes = [settings[0].maintenance_window]
  }
}

# __generated__ by Terraform from "file-security-scanner-uploads-2026"
resource "google_storage_bucket" "uploads" {
  default_event_based_hold    = false
  enable_object_retention     = false
  force_destroy               = false
  labels                      = {}
  location                    = "US-CENTRAL1"
  name                        = "file-security-scanner-uploads-2026"
  project                     = "file-security-scanner"
  public_access_prevention    = "enforced"
  requester_pays              = false
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  encryption {
    default_kms_key_name = null
    customer_managed_encryption_enforcement_config {
      restriction_mode = "NotRestricted"
    }
    customer_supplied_encryption_enforcement_config {
      restriction_mode = "FullyRestricted"
    }
    google_managed_encryption_enforcement_config {
      restriction_mode = "NotRestricted"
    }
  }
  hierarchical_namespace {
    enabled = false
  }
  soft_delete_policy {
    retention_duration_seconds = 604800
  }
  lifecycle {
    prevent_destroy = true
  }
}

# __generated__ by Terraform
resource "google_container_cluster" "scanner" {
  allow_net_admin                          = null
  autopilot_privileged_admission           = []
  datapath_provider                        = "ADVANCED_DATAPATH"
  deletion_protection                      = true
  description                              = null
  disable_l4_lb_firewall_reconciliation    = false
  enable_autopilot                         = true
  enable_cilium_clusterwide_network_policy = false
  enable_fqdn_network_policy               = false
  enable_kubernetes_alpha                  = false
  enable_l4_ilb_subsetting                 = false
  enable_legacy_abac                       = false
  enable_multi_networking                  = false
  enable_tpu                               = false
  in_transit_encryption_config             = null
  initial_node_count                       = 0
  location                                 = "us-central1"
  logging_service                          = "logging.googleapis.com/kubernetes"
  min_master_version                       = null
  monitoring_service                       = "monitoring.googleapis.com/kubernetes"
  name                                     = "scanner-gke"
  network                                  = "projects/file-security-scanner/global/networks/default"
  networking_mode                          = "VPC_NATIVE"
  node_locations                           = ["us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f"]
  node_version                             = "1.36.4-gke.1495002"
  project                                  = "file-security-scanner"
  remove_default_node_pool                 = null
  resource_labels                          = {}
  subnetwork                               = "projects/file-security-scanner/regions/us-central1/subnetworks/default"
  addons_config {
    gce_persistent_disk_csi_driver_config {
      enabled = true
    }
    gcp_filestore_csi_driver_config {
      enabled = true
    }
    gcs_fuse_csi_driver_config {
      enabled = true
    }
    parallelstore_csi_driver_config {
      enabled = true
    }
  }
  anonymous_authentication_config {
    mode = "LIMITED"
  }
  control_plane_endpoints_config {
    dns_endpoint_config {
      allow_external_traffic    = false
      enable_k8s_certs_via_dns  = false
      enable_k8s_tokens_via_dns = false
      endpoint                  = "gke-071136353c6d4751af77416cb5d7148b7b38-956088853573.us-central1.gke.goog"
    }
    ip_endpoints_config {
      enabled = true
    }
  }
  database_encryption {
    key_name = null
    state    = "DECRYPTED"
  }
  dns_config {
    additive_vpc_scope_dns_domain = null
    cluster_dns                   = "CLOUD_DNS"
    cluster_dns_domain            = "cluster.local"
    cluster_dns_scope             = "CLUSTER_SCOPE"
  }
  gateway_api_config {
    channel = "CHANNEL_STANDARD"
  }
  ip_allocation_policy {
    cluster_secondary_range_name = "gke-scanner-gke-pods-07113635"
    stack_type                   = "IPV4"
    network_tier_config {
      network_tier = "NETWORK_TIER_DEFAULT"
    }
    pod_cidr_overprovision_config {
      disabled = false
    }
  }
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }
  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }
  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS", "STORAGE", "HPA", "POD", "DAEMONSET", "DEPLOYMENT", "STATEFULSET", "CADVISOR", "KUBELET", "DCGM", "JOBSET"]
    advanced_datapath_observability_config {
      enable_metrics = true
      enable_relay   = false
    }
    managed_prometheus {
      enabled = true
    }
  }
  node_pool_auto_config {
    resource_manager_tags = {}
    node_kubelet_config {
      insecure_kubelet_readonly_port_enabled = "FALSE"
    }
  }
  node_pool_defaults {
    node_config_defaults {
      insecure_kubelet_readonly_port_enabled = "FALSE"
      logging_variant                        = "DEFAULT"
      gcfs_config {
        enabled = true
      }
    }
  }
  notification_config {
    pubsub {
      enabled = false
      topic   = null
    }
  }
  pod_autoscaling {
    hpa_profile = "PERFORMANCE"
  }
  private_cluster_config {
    enable_private_endpoint     = false
    enable_private_nodes        = false
    private_endpoint_subnetwork = null
    master_global_access_config {
      enabled = false
    }
  }
  rbac_binding_config {
    enable_insecure_binding_system_authenticated   = false
    enable_insecure_binding_system_unauthenticated = false
  }
  release_channel {
    channel = "REGULAR"
  }
  secret_manager_config {
    enabled = false
  }
  security_posture_config {
    mode               = "BASIC"
    vulnerability_mode = "VULNERABILITY_MODE_UNSPECIFIED"
  }
  service_external_ips_config {
    enabled = false
  }
  vertical_pod_autoscaling {
    enabled = true
  }
  workload_identity_config {
    workload_pool = "file-security-scanner.svc.id.goog"
  }
  lifecycle {
    prevent_destroy = true
    # Provider supplies gke://* for an empty API value; preserve existing admission.
    ignore_changes = [autopilot_privileged_admission]
  }
}

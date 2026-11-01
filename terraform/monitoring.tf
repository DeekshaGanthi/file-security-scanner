locals {
  log_scope    = <<-FILTER
    resource.type="k8s_container"
    resource.labels.project_id="${var.project_id}"
    resource.labels.location="${var.region}"
    resource.labels.cluster_name="${var.cluster_name}"
    resource.labels.namespace_name="scanner"
    resource.labels.container_name="backend"
    jsonPayload.service="backend"
    jsonPayload.event="http_request"
  FILTER
  error_metric = "logging.googleapis.com/user/scanner_http_5xx_count"
  metric_scope = "resource.type=\"k8s_container\" AND resource.labels.project_id=\"${var.project_id}\" AND resource.labels.location=\"${var.region}\" AND resource.labels.cluster_name=\"${var.cluster_name}\" AND resource.labels.namespace_name=\"scanner\""
  charts = [
    { title = "HTTP 5xx error count (per minute)", metric = local.error_metric, aligner = "ALIGN_SUM", unit = "1", group = "resource.label.container_name" },
    { title = "CPU usage (cores)", metric = "kubernetes.io/container/cpu/core_usage_time", aligner = "ALIGN_RATE", unit = "{CPU}", group = "resource.label.container_name" },
    { title = "Memory usage (bytes)", metric = "kubernetes.io/container/memory/used_bytes", aligner = "ALIGN_MEAN", unit = "By", group = "resource.label.container_name" }
  ]
}

resource "google_logging_metric" "http_5xx" {
  name        = "scanner_http_5xx_count"
  filter      = "${local.log_scope}\njsonPayload.http_status>=500\njsonPayload.http_status<600"
  description = "One backend request-completion record per actual HTTP 5xx response."
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }
  lifecycle { prevent_destroy = true }
}

resource "google_monitoring_dashboard" "scanner" {
  dashboard_json = jsonencode({
    displayName = "AI File Security Scanner — Milestone 6 Observability"
    gridLayout = {
      columns = "1"
      widgets = [for chart in local.charts : {
        title = chart.title
        xyChart = {
          dataSets = [for component in(chart.metric == local.error_metric ? ["backend"] : ["backend", "frontend"]) : {
            plotType       = "LINE"
            targetAxis     = "Y1"
            legendTemplate = component
            timeSeriesQuery = {
              unitOverride = chart.unit
              timeSeriesFilter = {
                filter = "metric.type=\"${chart.metric}\" AND ${local.metric_scope} AND resource.labels.container_name=\"${component}\""
                aggregation = {
                  alignmentPeriod    = "60s"
                  perSeriesAligner   = chart.aligner
                  crossSeriesReducer = "REDUCE_SUM"
                  groupByFields      = [chart.group]
                }
              }
            }
          }]
          yAxis = { label = chart.unit, scale = "LINEAR" }
        }
      }]
    }
  })
  depends_on = [google_logging_metric.http_5xx]
}

resource "google_monitoring_notification_channel" "team" {
  display_name = "Scanner authorized team email"
  type         = "email"
  labels       = { email_address = var.notification_email }
}

resource "google_monitoring_alert_policy" "http_5xx" {
  display_name          = "AI File Security Scanner — HTTP 5xx Alert"
  combiner              = "OR"
  enabled               = true
  notification_channels = [google_monitoring_notification_channel.team.name]
  conditions {
    display_name = "At least one backend 5xx in a five-minute interval"
    condition_threshold {
      filter          = "metric.type=\"${local.error_metric}\" AND ${local.metric_scope}"
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "0s"
      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_SUM"
        cross_series_reducer = "REDUCE_SUM"
      }
      trigger { count = 1 }
    }
  }
  alert_strategy { auto_close = "1800s" }
  documentation {
    content = "Backend returned HTTP 5xx. Check Cloud Logging for event=http_request and numeric http_status>=500. Controlled demo events include controlled_failure=true."
  }
  depends_on = [google_logging_metric.http_5xx]
}

# Verified automatic rollback - November 1, 2026

Run: https://github.com/DeekshaGanthi/file-security-scanner/actions/runs/41359525217

Commit: ef751fe3b3b148b0241ffe7c991eba4b92193051; dispatch input demo_failure=true.

The workflow built/pushed candidate images, verified/captured the healthy release,
then changed only candidate backend readiness to
/milestone6-intentional-readiness-failure. Kubernetes returned readiness 404;
the new pod stayed unready while two healthy old backend replicas continued serving.
Rolling update maxUnavailable=0/maxSurge=1 preserved availability.

The configured rollout timeout failed the deployment step. Without manual rollback,
the dedicated automatic recovery step restored both saved pod templates, waited
for readiness, verified previous immutable image references, checked every running
pod directly and confirmed HTTPS 200. The failed workflow stayed failed.

Evidence: pipeline/failed-rollback-run.json, automatic-rollback-health-checks.txt,
candidate-readiness-failure.json, restored-release.json, final-kubernetes.txt and
final-https.txt. All prior image digests were matched against the healthy release
recorded before the demonstration. HPA/PDB and Active certificate remain intact.
No database reset, persistent-data removal or infrastructure deletion occurred.

This demonstrates automated recovery from a failed candidate deployment. Forced
runner cancellation/loss can still prevent workflow recovery; see cicd-workflow.md.

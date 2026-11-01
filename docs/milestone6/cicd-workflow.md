# CI/CD

Development: `milestone6-dev`. Deployment: `milestone6-deploy` (approved code deployed). Promote by reviewing and merging the tested development commit into the
deployment branch; never force-push or rewrite Milestone 5 history.

Workflow: `.github/workflows/milestone6-deploy.yml`. A push to the deployment branch
automatically triggers tests, builds and registry push for both existing Dockerfiles,
then deploys immutable digests. Manual dispatch adds an optional controlled failure.
The workflow rejects execution on another branch. The WIF condition additionally
requires the exact repository and deployment ref. The workflow uses the verified public WIF provider resource ID directly. No service-account keys.
Infrastructure is now applied. Provider:
projects/956088853573/locations/global/workloadIdentityPools/scanner-github/providers/github.
Deployment succeeded; no GitHub secret or repository variable is required for WIF.

`scanner-deploy` gets repository-scoped Artifact Registry writer, project cluster
viewer, and namespace RBAC in `k8s/cicd/rbac.yaml`. The Role can patch only backend
and frontend Deployments and inspect pods/ReplicaSets. Pod exec is necessary for
direct health checks and grants application-level access inside these containers;
restrict who can push to the deployment branch. It cannot read Kubernetes Secrets
through the Kubernetes API. This role is now applied; eight authorization checks passed.

Before mutation, `scripts/release.py capture` verifies the current immutable images,
all active pods, database readiness and HTTPS, then saves both pod templates on the
ephemeral runner. Snapshot content is never uploaded as an artifact or logged.
Deploy patches only pod templates, preserving HPA replica ownership and all other
resources. Each new pod must run the expected image reference and pass direct
localhost health checks. Status checks require observed generation and ready,
available and updated replica counts to match the desired count (at least two).

On a failed deployment/verification step, an automatic `always()` rollback step
restores both exact prior pod templates and verifies their images, all pod health,
and public HTTPS. The failed step stays failed; successful recovery never turns
the workflow green. Failures before deployment mutation do not trigger recovery.
Concurrency never cancels an in-progress release. Runner loss, forced cancellation,
or job-wide timeout can prevent recovery; operator recovery uses the previous
verified digest/template from release history. Do not deliberately cancel a demo.

The Actions summary records SHA and digests; Actions logs contain health and
recovery results. Both a real successful run and a failed/recovered run are now recorded in verification-report.md.
Dependencies follow existing unpinned requirements; full dependency reproducibility
is a remaining limitation. Action major versions should be pinned to reviewed
commit SHAs before broader production use.

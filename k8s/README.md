# Deployed Kubernetes configuration

JSON is valid YAML. These files contain the actual deployed hostname and immutable image digests.
Namespace scanner, cluster scanner-gke in us-central1.
Run scripts/deploy-gke.ps1 -ManifestDirectory k8s to reproduce the deployment after approval.
Use scripts/render-k8s.py for a new release or hostname; review and commit the rendered files.
A shared Streamlit cookie Secret is generated securely by the deployment script, not stored here.
Backend is private on ClusterIP; frontend is exposed through one GCE Ingress.
See docs/MILESTONE5_VERIFICATION.md for evidence and outstanding external dependencies.

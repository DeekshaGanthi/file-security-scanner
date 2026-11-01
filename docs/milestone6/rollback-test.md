# Safe rollback demonstration

Status: implementation locally tested; live demonstration pending approval.

After a normal successful deployment from `milestone6-deploy`, manually dispatch
the same workflow on that branch with `demo_failure=true`. It still builds both
images. Only the candidate backend readiness probe changes to a nonexistent route.
Existing rolling strategy (`maxUnavailable=0`, `maxSurge=1`) keeps healthy old
replicas available. The process liveness probe and database remain unchanged.

The backend rollout must time out; the workflow automatically restores both saved
pod templates. It must show `ROLLBACK INITIATED`, prior image digests with verified
replica counts and direct health results, HTTPS 200, then
`PREVIOUS VERSION RESTORED AND VERIFIED`. The deployment workflow remains failed.
The frontend candidate is not deployed if the backend rollout fails first.

Capture the actual run URL, commit, initial digests, failure, automatic recovery
logs and restored digests in `evidence/pipeline/`. Check HPA/PDB and certificate
after recovery. No real demo commit SHA or workflow run exists yet.

PowerShell read-only checks:

```powershell
kubectl get deployments,pods,hpa,pdb,ingress,managedcertificate -n scanner
kubectl get deployment backend frontend -n scanner -o 'jsonpath={range .items[*]}{.metadata.name}{" "}{.spec.template.spec.containers[*].image}{"\n"}{end}'
curl.exe -I https://scanner.136-69-114-222.sslip.io/
```

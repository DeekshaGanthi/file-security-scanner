# Milestone 6 verification - November 1, 2026

Live implementation and recovery checks passed. Required screenshot artifacts and
interactive browser UI confirmation remain pending because browser automation
stopped at its URL-confidence policy guard. Do not mark the entire submission
complete until those manual evidence items are supplied.

| Requirement | Actual verification |
|---|---|
| Structured logging | Real JSON in Cloud Logging; one completion per test request; local exception/secret-sanitization tests pass |
| Controlled 503 | Real loopback-only 503, matching UUID; route absent on public backend port; listener stopped afterward |
| Error metric | Actual DELTA INT64 count 1; exact filter matches only the 503 and excludes tested 200/404 |
| Dashboard | Created; real HTTP error, backend/frontend CPU and memory data verified by API; screenshots pending |
| Alert | Incident 0.oeimw7fsr668 opened 22:58:38 UTC; authorized recipient explicitly confirmed receipt; screenshot pending |
| Terraform | Six imports, ten monitoring/CI additions, separate private versioned state bucket; both refresh-enabled plans exit 0 with No changes |
| CI authentication | Real WIF authentication succeeded; no user-managed SA keys; eight namespace authorization checks passed |
| Automatic deployment | Push-triggered run built/pushed both images, deployed digests and passed direct pod/HTTPS checks |
| Automatic rollback | Deliberate readiness failure timed out; automatic restore step succeeded and verified prior digests/health; workflow remains failed |
| Application integration | Harmless scan 70: YARA, Gemini success, PostgreSQL persistence/history, exactly one private GCS object |
| Availability/security | Two healthy frontend/backend replicas, HPA/PDB intact, certificate Active, HTTPS 200 after recovery |
| Interactive Streamlit UI | HTML/process health verified; browser interaction not reverified after deployment |
| Billing budgets | Read-only audit returned 403; no budget settings changed |

Successful deployment: https://github.com/DeekshaGanthi/file-security-scanner/actions/runs/41358659674

Controlled failed deployment with successful recovery: https://github.com/DeekshaGanthi/file-security-scanner/actions/runs/41359525217

Both runs used approved commit `ef751fe3b3b148b0241ffe7c991eba4b92193051`. The failure used the workflow
input `demo_failure=true` on the same commit; there is no separate broken source
commit. The candidate's readiness probe changed, not its database or application
data. All sampled public HTTPS checks remained 200 during the failed rollout.

17 tests passed in Actions; Docker images actually built and pushed there. Existing
Milestone 5 history is preserved. Milestone 6 code is on milestone6-deploy; final
evidence and repeatable verification scripts are on milestone6-dev. Documentation
updates are not pushed to the deployment branch, avoiding an unnecessary release.

Ownership/provider exceptions: terraform-coverage.md. PowerShell commands:
verification-commands.ps1. Manual screenshot instructions: evidence/manual-screenshots.md.
No credentials, Terraform state, binary plans or runner pod-template snapshots are
committed. Historical no-change plans and refreshed final plans are genuine.

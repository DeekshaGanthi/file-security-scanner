# Milestone 5 rubric compliance

| Requirement | Points | Status | Evidence |
|---|---:|---|---|
| GKE deployment with 2+ healthy replicas | 10 | Verified | initial-healthy.txt; 2/2 frontend and backend, real GKE workloads |
| Separate liveness and DB-aware readiness | 8 | Verified | backend health source, six tests, container smoke; live SELECT 1 and both 200 responses in e2e.txt |
| Live pod replacement and actual scaling | 9 | Verified | recovery before/deletion/after; HPA 2 to 3 and later 2; team must repeat live on recording |
| Valid HTTPS and HTTP redirect | 10 | Verified | certificate-active.yaml, HTTPS 200, HTTP 301 headers, browser UI |
| Required manifests committed | 8 | Verified | dd2a1d7 contains all deployed manifests; milestone5-gke pushed after approval and remote 7cbc899 verified |
| Video and slides complete | 5 | In Progress | Complete 10-minute script and two-slide layout/content; team recording and Office file export remain |
| **Total** | **50** | **In Progress** | **No final score assigned** |

Statuses reflect observation, not predicted marks. Video and OneDrive/Canvas steps
must be completed by the team before the assignment is submission-ready.

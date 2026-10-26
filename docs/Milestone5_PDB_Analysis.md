# Milestone 5 PodDisruptionBudget and intermittent 5xx failure analysis

HTTP 5xx responses indicate that a server or an upstream component could not complete
a request. In a Kubernetes application, intermittent failures can occur when too few
healthy pods remain during maintenance, when a load balancer has stale endpoints,
or when an upstream dependency is unavailable. No production 5xx incident is asserted
here; this analysis explains the availability controls prepared for the scanner.

The frontend and backend Deployments each specify at least two replicas. Their
PodDisruptionBudgets require one available pod, which constrains supported voluntary
evictions such as node maintenance using the eviction API. This reduces the risk of
removing all healthy replicas simultaneously. Backend readiness checks PostgreSQL
with a lightweight SELECT 1; a failed check removes the pod from ready Service
endpoints. Liveness checks only process responsiveness, so a database outage does
not itself trigger restart loops. Frontend health and load-balancer checks use
Streamlit's own health endpoint. Rolling updates allow one additional pod and zero
unavailable pods, helping maintain capacity while new instances become ready.

A PDB does not guarantee zero downtime. It does not block direct pod deletion,
prevent node crashes, repair a database outage, or preserve an in-memory Streamlit
session after its pod disappears. Readiness detection and load-balancer propagation
also take time, and requests already in flight may still fail. Availability therefore
depends on the combined behavior of replicas, scheduling, health checks, connection
draining and graceful termination. Live recovery and load testing must demonstrate
the actual behavior before these controls are described as verified.

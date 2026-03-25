# Lab 9 — Kubernetes Fundamentals

## Architecture Overview

```
                    ┌─────────────────────────────────┐
                    │         minikube cluster         │
                    │                                  │
  kubectl / curl ──►│  Service (NodePort :30080)       │
                    │         │                        │
                    │         ▼                        │
                    │  ┌─────────────────────────┐     │
                    │  │   Deployment (3 replicas)│     │
                    │  │  ┌───┐  ┌───┐  ┌───┐   │     │
                    │  │  │Pod│  │Pod│  │Pod│   │     │
                    │  │  └───┘  └───┘  └───┘   │     │
                    │  └─────────────────────────┘     │
                    └─────────────────────────────────┘
```

- 3 replicas of `1sarmatt/devops-info-service:latest`
- Service type: NodePort (port 30080 → container 5000)
- Rolling update strategy: maxSurge=1, maxUnavailable=0

---

## Manifest Files

### `deployment.yml`
- Image: `1sarmatt/devops-info-service:latest` (from Lab 2)
- Replicas: 3 (minimum required)
- Resources: requests 100m CPU / 128Mi RAM, limits 200m CPU / 256Mi RAM
- Liveness probe: `GET /health` every 10s, starts after 10s
- Readiness probe: `GET /health` every 5s, starts after 5s
- Rolling update: maxUnavailable=0 ensures zero downtime

### `service.yml`
- Type: NodePort — allows external access without cloud provider
- Port mapping: 80 (service) → 5000 (container) → 30080 (node)
- Selector: `app: devops-info-service` matches Deployment pods

---

## Deployment Evidence

### Cluster setup
```
$ kubectl cluster-info
Kubernetes control plane is running at https://127.0.0.1:65107
CoreDNS is running at https://127.0.0.1:65107/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

$ kubectl get nodes
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   25s   v1.35.1
```

### All resources
```
$ kubectl get all
NAME                                       READY   STATUS    RESTARTS   AGE
pod/devops-info-service-849b5bc858-889b6   1/1     Running   0          89s
pod/devops-info-service-849b5bc858-mrhvk   1/1     Running   0          107s
pod/devops-info-service-849b5bc858-wqcvq   1/1     Running   0          97s

NAME                          TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
service/devops-info-service   NodePort    10.100.186.114   <none>        80:30080/TCP   5m34s
service/kubernetes            ClusterIP   10.96.0.1        <none>        443/TCP        9m1s

NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/devops-info-service   3/3     3            3           5m34s
```

### App responding
```
$ kubectl port-forward service/devops-info-service 8081:80
$ curl http://localhost:8081/health
{"status":"healthy","timestamp":"2026-03-25T07:44:30.654884+00:00","uptime_seconds":553}
```

---

## Operations Performed

### Deploy
```bash
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl rollout status deployment/devops-info-service
```

### Scale to 5 replicas
```bash
kubectl scale deployment/devops-info-service --replicas=5
# Output: deployment.apps/devops-info-service scaled
# Waiting for deployment rollout to finish: 3 of 5 updated replicas are available...
# Waiting for deployment rollout to finish: 4 of 5 updated replicas are available...
# deployment "devops-info-service" successfully rolled out
```

### Rolling update
```bash
kubectl apply -f k8s/deployment.yml   # updated annotation triggers rollout
kubectl rollout status deployment/devops-info-service
# Waiting for deployment rollout: 1 out of 3 new replicas have been updated...
# deployment "devops-info-service" successfully rolled out
```

### Rollback
```bash
kubectl rollout undo deployment/devops-info-service
# deployment.apps/devops-info-service rolled back

kubectl rollout history deployment/devops-info-service
# REVISION  CHANGE-CAUSE
# 1         <none>
# 2         lab09: initial deployment v1
# 3         <none>
```

---

## Production Considerations

**Health checks:**
- Liveness probe restarts the container if `/health` fails 3 times — prevents stuck processes
- Readiness probe removes pod from service endpoints until it's ready — prevents traffic to unready pods
- Different delays: readiness starts sooner (5s) to detect ready state quickly, liveness waits longer (10s) to avoid premature restarts

**Resource limits:**
- Requests (100m CPU, 128Mi) tell the scheduler how much to reserve
- Limits (200m CPU, 256Mi) prevent one pod from starving others
- Values based on observed usage from Docker stats in Lab 8

**Production improvements:**
- Use specific image tag (e.g., `v1.2.3`) instead of `latest` for reproducibility
- Add `PodDisruptionBudget` to guarantee availability during node maintenance
- Use `HorizontalPodAutoscaler` for automatic scaling based on CPU/memory
- Add `ConfigMap` for environment configuration
- Use `Secrets` for sensitive values instead of plain env vars
- Set up proper Ingress with TLS instead of NodePort

**Monitoring:**
- Prometheus scrapes `/metrics` from each pod
- Liveness/readiness probes provide basic health signal to Kubernetes
- In production: add Prometheus Operator + ServiceMonitor for automatic scraping

---

## Challenges & Solutions

**Challenge:** minikube on Mac M-series uses Docker driver, so `minikube service` opens a tunnel instead of direct NodePort access.
**Solution:** Used `kubectl port-forward` for testing instead.

**Challenge:** Image built for `linux/amd64` runs on ARM via emulation — slight performance overhead.
**Solution:** Acceptable for dev/lab purposes; in production would build multi-arch image.

**What I learned:**
- Kubernetes reconciliation loop: declare desired state, controller makes it happen
- Rolling update with `maxUnavailable=0` guarantees zero downtime
- Readiness vs liveness probes serve different purposes — both are needed
- Labels and selectors are the glue connecting Deployments, ReplicaSets, Pods, and Services

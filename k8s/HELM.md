# Lab 10 — Helm Package Manager

## Chart Overview

Chart location: `k8s/devops-info-service/`

```
k8s/devops-info-service/
├── Chart.yaml                        # Chart metadata (name, version, appVersion)
├── values.yaml                       # Default values
├── values-dev.yaml                   # Development overrides
├── values-prod.yaml                  # Production overrides
└── templates/
    ├── _helpers.tpl                  # Reusable template helpers (name, labels)
    ├── deployment.yaml               # Deployment manifest (templated)
    ├── service.yaml                  # Service manifest (templated)
    ├── NOTES.txt                     # Post-install instructions
    └── hooks/
        ├── pre-install-job.yaml      # Runs before install (validation)
        └── post-install-job.yaml     # Runs after install (smoke test)
```

Key template files:
- `_helpers.tpl` — defines `fullname`, `labels`, `selectorLabels` used across all templates
- `deployment.yaml` — fully templated: replicas, image, resources, probes all from values
- `service.yaml` — type, ports, nodePort all configurable

---

## Configuration Guide

### Key values

| Value | Default | Purpose |
|-------|---------|---------|
| `replicaCount` | 3 | Number of pod replicas |
| `image.repository` | `1sarmatt/devops-info-service` | Docker image |
| `image.tag` | `latest` | Image tag |
| `service.type` | `NodePort` | Service type |
| `service.nodePort` | `30080` | External port |
| `resources.limits.cpu` | `200m` | CPU limit |
| `resources.limits.memory` | `256Mi` | Memory limit |
| `livenessProbe` | `/health` every 10s | Container health check |
| `readinessProbe` | `/health` every 5s | Traffic readiness check |

### Environment differences

| Setting | Dev | Prod |
|---------|-----|------|
| replicas | 1 | 5 |
| CPU limit | 100m | 500m |
| Memory limit | 128Mi | 512Mi |
| nodePort | 30081 | 30082 |
| liveness initialDelay | 5s | 30s |

### Example installations

```bash
# Default (3 replicas)
helm install devops-release k8s/devops-info-service

# Development
helm install devops-dev k8s/devops-info-service -f k8s/devops-info-service/values-dev.yaml

# Production
helm install devops-prod k8s/devops-info-service -f k8s/devops-info-service/values-prod.yaml

# Override single value
helm install devops-release k8s/devops-info-service --set replicaCount=10
```

---

## Hook Implementation

### Pre-install hook (`templates/hooks/pre-install-job.yaml`)
- Runs **before** any resources are created
- Weight: `-5` (runs first)
- Simulates environment validation / config check
- Deletion policy: `hook-succeeded` — deleted automatically after success

### Post-install hook (`templates/hooks/post-install-job.yaml`)
- Runs **after** all resources are installed and ready
- Weight: `5` (runs after pre-install)
- Simulates smoke test / deployment notification
- Deletion policy: `hook-succeeded` — deleted automatically after success

Hook execution order: `pre-install (-5)` → deploy resources → `post-install (5)`

After successful execution both jobs are automatically deleted (`hook-delete-policy: hook-succeeded`), which is why `kubectl get jobs` returns empty — they ran and cleaned up.

---

## Installation Evidence

### Helm list
```
NAME            NAMESPACE  REVISION  STATUS    CHART                       APP VERSION
devops-dev      default    1         deployed  devops-info-service-0.1.0   1.0.0
devops-prod     default    1         deployed  devops-info-service-0.1.0   1.0.0
devops-release  default    1         deployed  devops-info-service-0.1.0   1.0.0
```

### kubectl get all
```
NAME                                                     READY   STATUS    RESTARTS   AGE
pod/devops-dev-devops-info-service-7469ffcd57-9c2cl      1/1     Running   0          2m26s
pod/devops-prod-devops-info-service-9c4f4d488-99n5q      1/1     Running   0          58s
pod/devops-prod-devops-info-service-9c4f4d488-brxn2      1/1     Running   0          58s
pod/devops-prod-devops-info-service-9c4f4d488-ft7tm      1/1     Running   0          58s
pod/devops-prod-devops-info-service-9c4f4d488-jpz4c      1/1     Running   0          58s
pod/devops-prod-devops-info-service-9c4f4d488-t9sv5      1/1     Running   0          58s
pod/devops-release-devops-info-service-7594674b8-kngq7   1/1     Running   0          4m3s
pod/devops-release-devops-info-service-7594674b8-ng9vh   1/1     Running   0          4m3s
pod/devops-release-devops-info-service-7594674b8-xggfs   1/1     Running   0          4m3s

NAME                                         TYPE        CLUSTER-IP      PORT(S)
service/devops-dev-devops-info-service       NodePort    10.96.x.x       80:30081/TCP
service/devops-prod-devops-info-service      NodePort    10.96.x.x       80:30082/TCP
service/devops-release-devops-info-service   NodePort    10.96.236.152   80:30080/TCP

NAME                                                 READY   UP-TO-DATE   AVAILABLE
deployment.apps/devops-dev-devops-info-service       1/1     1            1
deployment.apps/devops-prod-devops-info-service      5/5     5            5
deployment.apps/devops-release-devops-info-service   3/3     3            3
```

### App responding
```bash
kubectl port-forward service/devops-release-devops-info-service 8080:80
curl http://localhost:8080/health
# {"status":"healthy","timestamp":"...","uptime_seconds":553}
```

---

## Operations

```bash
# Install
helm install devops-release k8s/devops-info-service

# Upgrade (e.g. change replicas)
helm upgrade devops-release k8s/devops-info-service --set replicaCount=5

# Rollback to previous revision
helm rollback devops-release 1

# View history
helm history devops-release

# Uninstall
helm uninstall devops-release
```

---

## Testing & Validation

```bash
# Lint
helm lint k8s/devops-info-service
# ==> Linting k8s/devops-info-service
# 1 chart(s) linted, 0 chart(s) failed

# Render templates locally
helm template devops-release k8s/devops-info-service

# Dry run
helm install --dry-run --debug test-release k8s/devops-info-service
```

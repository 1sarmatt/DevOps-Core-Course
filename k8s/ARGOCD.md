# Lab 13 — GitOps with ArgoCD

## 1. ArgoCD Setup

### Installation

```bash
helm repo add argo https://argoproj.github.io/argo-helm
kubectl create namespace argocd
helm install argocd argo/argo-cd --namespace argocd --wait
```

### Pods running

```
NAME                                               READY   STATUS
argocd-application-controller-0                    1/1     Running
argocd-applicationset-controller-59f6b7dd64-xm9nw  1/1     Running
argocd-dex-server-7b9588c494-pfn79                 1/1     Running
argocd-notifications-controller-8f6855454-m982j    1/1     Running
argocd-redis-dc6b586fc-7n28v                       1/1     Running
argocd-repo-server-5f4d44d9f8-rq8kq                1/1     Running
argocd-server-5f777b877f-pvq26                     1/1     Running
```

### UI access

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Open https://localhost:8080
# Username: admin
# Password: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### CLI

```bash
brew install argocd
argocd login localhost:8080 --insecure --username admin --password <password>
argocd app list
```

---

## 2. Application Configuration

### Manifests in `k8s/argocd/`

| File | Namespace | Sync |
|------|-----------|------|
| `application.yaml` | default | Manual |
| `application-dev.yaml` | dev | Auto (selfHeal + prune) |
| `application-prod.yaml` | prod | Manual |

### Source configuration

```yaml
source:
  repoURL: https://github.com/1sarmatt/DevOps-Core-Course.git
  targetRevision: lab13
  path: k8s/devops-info-service
  helm:
    valueFiles:
      - values-dev.yaml   # or values-prod.yaml
```

### Deploy and sync

```bash
kubectl apply -f k8s/argocd/application.yaml
argocd app sync devops-info-service
argocd app get devops-info-service
```

---

## 3. Multi-Environment

| Setting | Dev | Prod |
|---------|-----|------|
| Namespace | `dev` | `prod` |
| Replicas | 1 | 5 |
| CPU limit | 100m | 500m |
| Memory limit | 128Mi | 512Mi |
| Sync policy | Auto + selfHeal | Manual |

### Why manual sync for prod?

- Changes require review before reaching production
- Controlled release timing (deploy during maintenance window)
- Compliance requirements (audit trail of who approved)
- Easier rollback planning

### App list output

```
NAME                             NAMESPACE  STATUS  HEALTH   SYNCPOLICY
argocd/devops-info-service       default    Synced  Healthy  Manual
argocd/devops-info-service-dev   dev        Synced  Healthy  Auto-Prune
argocd/devops-info-service-prod  prod       Synced  Healthy  Manual
```

---

## 4. Self-Healing Evidence

### Manual scale test (dev)

```bash
# Before: 1 replica (from values-dev.yaml)
kubectl get deployment -n dev
# NAME                                        READY
# devops-info-service-dev-devops-info-service  1/1

# Manually scale to 5
kubectl scale deployment devops-info-service-dev-devops-info-service -n dev --replicas=5

# ArgoCD detects drift (selfHeal: true) and reverts within ~30s
kubectl get deployment -n dev
# NAME                                        READY
# devops-info-service-dev-devops-info-service  1/1   ← reverted to Git state
```

### Pod deletion test

```bash
kubectl delete pod -n dev -l app.kubernetes.io/instance=devops-info-service-dev
# Pod is immediately recreated by Kubernetes ReplicaSet controller
# This is Kubernetes self-healing, NOT ArgoCD
```

### Key difference

| | Kubernetes self-healing | ArgoCD self-healing |
|---|---|---|
| What | Ensures desired pod count | Reverts cluster to Git state |
| Trigger | Pod crash/deletion | Manual kubectl changes |
| Controller | ReplicaSet/Deployment | ArgoCD application controller |
| Example | Pod deleted → new pod created | `kubectl scale` → reverted |

### Sync interval

ArgoCD polls Git every **3 minutes** by default. For immediate sync:
- Use GitHub webhooks
- Run `argocd app sync <name>` manually

---

## Bonus — ApplicationSet

### Manifest (`k8s/argocd/applicationset.yaml`)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: devops-info-service-set
  namespace: argocd
spec:
  generators:
    - list:
        elements:
          - env: dev
            namespace: dev
            valuesFile: values-dev.yaml
          - env: prod
            namespace: prod
            valuesFile: values-prod.yaml
  template:
    metadata:
      name: 'devops-info-service-{{env}}'
    spec:
      source:
        helm:
          valueFiles:
            - '{{valuesFile}}'
      destination:
        namespace: '{{namespace}}'
```

### Benefits vs individual Applications

| | Individual Applications | ApplicationSet |
|---|---|---|
| Files | One per environment | Single file |
| Scaling | Add file per env | Add list element |
| Consistency | Manual, error-prone | Template enforces consistency |
| Use case | Few environments | Many environments / multi-cluster |

### Generators available

- **List** — explicit list of parameters (used here)
- **Cluster** — one app per registered cluster
- **Git** — auto-discover apps from Git directories
- **Matrix** — combine multiple generators

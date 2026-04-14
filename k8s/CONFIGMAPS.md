# Lab 12 — ConfigMaps & Persistent Volumes

## 1. Application Changes — Visits Counter

Added persistent visit counter to `app_python/app.py`:
- `read_visits()` / `write_visits()` — read/write counter from file
- Counter file path: `VISITS_FILE` env var (default `/data/visits`)
- `GET /` — increments counter on each request
- `GET /visits` — returns current count

```python
VISITS_FILE = os.getenv('VISITS_FILE', '/data/visits')

def read_visits():
    try:
        with open(VISITS_FILE, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0
```

Docker Compose volume added in `monitoring/docker-compose.yml`:
```yaml
volumes:
  - app-data:/data
```

---

## 2. ConfigMap Implementation

### Chart structure

```
templates/
├── configmap.yaml    # Two ConfigMaps: file-based and env-based
├── deployment.yaml   # Mounts both ConfigMaps
└── pvc.yaml
```

### ConfigMap for file mount (`-config`)

```yaml
data:
  config.json: |
    {
      "app_name": "devops-info-service",
      "environment": "production",
      ...
    }
```

### ConfigMap for env vars (`-env`)

```yaml
data:
  APP_ENV: "production"
  LOG_LEVEL: "INFO"
  VISITS_FILE: "/data/visits"
```

### Mounting in deployment

```yaml
# File mount
volumeMounts:
  - name: config-volume
    mountPath: /config
volumes:
  - name: config-volume
    configMap:
      name: devops-release-devops-info-service-config

# Env vars
envFrom:
  - configMapRef:
      name: devops-release-devops-info-service-env
```

### Verification

```bash
$ kubectl get configmap
NAME                                              DATA   AGE
devops-release-devops-info-service-config         1      4m
devops-release-devops-info-service-env            3      4m

$ kubectl exec <pod> -- cat /config/config.json
{
  "app_name": "devops-info-service",
  "environment": "production",
  "log_level": "INFO",
  ...
}

$ kubectl exec <pod> -- env | grep -E "APP_ENV|LOG_LEVEL|VISITS_FILE"
APP_ENV=production
LOG_LEVEL=INFO
VISITS_FILE=/data/visits
```

---

## 3. Persistent Volume

### PVC configuration

```yaml
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Mi
```

`ReadWriteOnce` — volume can be mounted by one node at a time (sufficient for our use case).
Minikube provides `standard` storage class that auto-provisions hostPath volumes.

### Volume mount in deployment

```yaml
volumeMounts:
  - name: data-volume
    mountPath: /data
volumes:
  - name: data-volume
    persistentVolumeClaim:
      claimName: devops-release-devops-info-service-data
```

### Persistence test

```bash
# Generate 8 visits
$ curl http://localhost/visits
{"visits": 8}

# Delete pod
$ kubectl delete pod devops-release-devops-info-service-55785f9cdb-lrfbk
pod deleted

# New pod starts automatically, check visits
$ curl http://localhost/visits
{"visits": 8}   # ✅ data survived pod restart
```

```bash
$ kubectl get pvc
NAME                                          STATUS   VOLUME     CAPACITY   ACCESS MODES
devops-release-devops-info-service-data       Bound    pvc-0ab3   100Mi      RWO
```

---

## 4. ConfigMap vs Secret

| | ConfigMap | Secret |
|---|---|---|
| Data type | Non-sensitive config | Sensitive data |
| Storage | Plain text in etcd | Base64-encoded in etcd |
| Use case | App config, feature flags, URLs | Passwords, API keys, TLS certs |
| Visibility | Visible in `kubectl describe` | Hidden in `kubectl describe` |

**Use ConfigMap for:**
- Application settings (log level, environment name)
- Configuration files (nginx.conf, app.json)
- Feature flags
- Non-secret URLs and endpoints

**Use Secret for:**
- Passwords and credentials
- API keys and tokens
- TLS certificates
- Any value that should not be visible in plain text

---

## Bonus — ConfigMap Hot Reload

### Checksum annotation pattern

Added to deployment template:
```yaml
annotations:
  checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

When ConfigMap content changes, the checksum annotation changes → Kubernetes detects pod spec change → triggers rolling update automatically.

### Update delay

Without checksum annotation, mounted ConfigMap files update automatically but with a delay:
- kubelet sync period: ~60s
- configmap cache TTL: ~60s
- Total delay: up to ~2 minutes

### subPath limitation

When using `subPath` in volumeMount, the file is a **copy** (not a symlink), so it does **not** receive automatic updates. Use full directory mounts (without `subPath`) for auto-updates.

### Reload approaches

1. **Checksum annotation** (implemented) — restarts pods on ConfigMap change via `helm upgrade`
2. **Stakater Reloader** — watches ConfigMaps/Secrets and auto-restarts deployments
3. **Application file watching** — app polls config file for changes (inotify/polling)

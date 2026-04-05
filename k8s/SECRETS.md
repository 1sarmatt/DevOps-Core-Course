# Lab 11 — Kubernetes Secrets & HashiCorp Vault

## 1. Kubernetes Secrets

### Creating and viewing a secret

```bash
$ kubectl create secret generic app-credentials \
    --from-literal=username=<username> \
    --from-literal=password=<password>
secret/app-credentials created

$ kubectl get secret app-credentials -o yaml
apiVersion: v1
data:
  password: <base64-encoded-value>
  username: <base64-encoded-value>
kind: Secret
type: Opaque
```

### Decoding base64

```bash
$ echo "<base64-value>" | base64 -d
<decoded-value>
```

### Base64 encoding vs encryption

Kubernetes Secrets are **base64-encoded, NOT encrypted** by default.
Base64 is just an encoding scheme — anyone with API access can decode it instantly.

For real security:
- Enable **etcd encryption at rest** (`EncryptionConfiguration` in kube-apiserver)
- Use **RBAC** to restrict who can `get`/`list` secrets
- Use an **external secret manager** like HashiCorp Vault (see section 4)

---

## 2. Helm-Managed Secrets

### Chart structure

```
templates/
├── secrets.yaml        # Creates K8s Secret from values
├── deployment.yaml     # Consumes secret via envFrom
└── serviceaccount.yaml
```

### secrets.yaml

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "devops-info-service.fullname" . }}-secret
type: Opaque
stringData:
  APP_USERNAME: {{ .Values.secret.username | quote }}
  APP_PASSWORD: {{ .Values.secret.password | quote }}
```

`stringData` accepts plain text — Kubernetes auto-encodes to base64.

### Consuming in deployment via envFrom

```yaml
envFrom:
  - secretRef:
      name: {{ include "devops-info-service.fullname" . }}-secret
```

### Verification

```bash
$ kubectl exec <pod> -- env | grep APP_
APP_PASSWORD=<redacted>
APP_USERNAME=<redacted>
```

Secrets are visible as env vars inside the pod but **not** in `kubectl describe pod` output.

---

## 3. Resource Management

```yaml
resources:
  requests:
    cpu: 100m      # guaranteed minimum
    memory: 128Mi
  limits:
    cpu: 200m      # hard cap
    memory: 256Mi
```

**Requests vs Limits:**
- `requests` — what the scheduler reserves on the node; pod is guaranteed this amount
- `limits` — hard ceiling; container is killed (OOMKilled) if it exceeds memory limit

**Choosing values:**
- Start with observed usage from `kubectl top pods`
- Set limits ~2x requests for headroom
- CPU throttling is gradual; memory OOM is immediate — be more generous with memory

---

## 4. Vault Integration

### Installation

```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm install vault hashicorp/vault \
  --set "server.dev.enabled=true" \
  --set "injector.enabled=true"
```

```
$ kubectl get pods -l app.kubernetes.io/name=vault
NAME      READY   STATUS    RESTARTS   AGE
vault-0   1/1     Running   0          50s
```

### Configuration

```bash
# Store secrets
vault kv put secret/devops-info-service/config \
  username="<username>" password="<password>" api_key="<api-key>"

# Create policy
vault policy write devops-info-service - <<EOF
path "secret/data/devops-info-service/*" {
  capabilities = ["read"]
}
EOF

# Enable K8s auth
vault auth enable kubernetes
vault write auth/kubernetes/config \
  kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443"

# Create role
vault write auth/kubernetes/role/devops-info-service \
  bound_service_account_names=devops-release-devops-info-service \
  bound_service_account_namespaces=default \
  policies=devops-info-service \
  ttl=24h
```

### Vault Agent sidecar injection

Annotations on pod template trigger the injector:

```yaml
annotations:
  vault.hashicorp.com/agent-inject: "true"
  vault.hashicorp.com/role: "devops-info-service"
  vault.hashicorp.com/agent-inject-secret-config: "secret/data/devops-info-service/config"
  vault.hashicorp.com/agent-inject-template-config: |
    {{- with secret "secret/data/devops-info-service/config" -}}
    APP_USERNAME={{ .Data.data.username }}
    APP_PASSWORD={{ .Data.data.password }}
    API_KEY={{ .Data.data.api_key }}
    {{- end -}}
```

### Proof of injection

```bash
$ kubectl exec <pod> -- cat /vault/secrets/config
APP_USERNAME=<redacted>
APP_PASSWORD=<redacted>
API_KEY=<redacted>
```

**How sidecar injection works:**
1. Vault injector webhook intercepts pod creation
2. Adds `vault-agent-init` init container (authenticates, fetches secrets)
3. Adds `vault-agent` sidecar (keeps secrets refreshed)
4. Secrets written to `/vault/secrets/` shared volume

---

## 5. Security Analysis

| | K8s Secrets | HashiCorp Vault |
|---|---|---|
| Storage | etcd (base64, not encrypted by default) | Encrypted at rest always |
| Access control | RBAC | Fine-grained policies |
| Audit log | K8s audit log | Built-in audit log |
| Secret rotation | Manual | Automatic (dynamic secrets) |
| Complexity | Low | High |
| Best for | Simple configs, non-critical | Production, compliance, rotation |

**When to use K8s Secrets:**
- Dev/test environments
- Non-sensitive config (feature flags, URLs)
- When etcd encryption is enabled

**When to use Vault:**
- Production workloads
- Compliance requirements (SOC2, PCI-DSS)
- Need for secret rotation
- Multiple teams/services sharing secrets

**Production recommendations:**
1. Always enable etcd encryption at rest
2. Use Vault for all sensitive secrets (DB passwords, API keys)
3. Never commit real secrets to Git — use placeholder values + `--set` at deploy time
4. Restrict secret access with RBAC (least privilege)
5. Enable Vault audit logging

---

## Bonus — Vault Agent Templates & Named Templates

### Vault Agent template annotation

Renders secrets as `.env` format file at `/vault/secrets/config`:

```yaml
vault.hashicorp.com/agent-inject-template-config: |
  {{- with secret "secret/data/devops-info-service/config" -}}
  APP_USERNAME={{ .Data.data.username }}
  APP_PASSWORD={{ .Data.data.password }}
  API_KEY={{ .Data.data.api_key }}
  {{- end -}}
```

Vault Agent re-renders this file automatically when secrets rotate (configurable via `vault.hashicorp.com/agent-inject-command`).

### Named template in _helpers.tpl (DRY principle)

```yaml
{{- define "devops-info-service.envVars" -}}
- name: HOST
  value: "0.0.0.0"
- name: DEBUG
  value: {{ .Values.debug | default "False" | quote }}
{{- end }}
```

Used in deployment.yaml:
```yaml
env:
  {{- include "devops-info-service.envVars" . | nindent 12 }}
```

Benefit: change env var logic in one place, all deployments updated.

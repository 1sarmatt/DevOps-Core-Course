# Lab 8 — Metrics & Monitoring with Prometheus

## Architecture

```
Python App (/metrics)
       │
       ▼
  Prometheus (scrape every 15s)
       │
       ▼
  Grafana (PromQL dashboards)
       │
  also scrapes: Loki, Grafana itself, Prometheus itself
```

Data flow: app exposes `/metrics` → Prometheus pulls → stores in TSDB → Grafana queries via PromQL.

---

## Task 1 — Application Instrumentation

Added `prometheus-client==0.23.1` to `requirements.txt`.

### Metrics defined in `app.py`

| Metric | Type | Labels | Purpose |
|--------|------|--------|---------|
| `http_requests_total` | Counter | method, endpoint, status | Total HTTP requests (RED: Rate & Errors) |
| `http_request_duration_seconds` | Histogram | method, endpoint | Request latency (RED: Duration) |
| `http_requests_in_progress` | Gauge | — | Concurrent active requests |
| `devops_info_endpoint_calls_total` | Counter | endpoint | Business-level endpoint usage |
| `devops_info_system_collection_seconds` | Histogram | — | Time to collect system info |

Metrics are recorded in `before_request` / `after_request` hooks.  
Endpoint: `GET /metrics` — returns Prometheus text format.

---

## Task 2 — Prometheus Setup

**File:** `monitoring/prometheus/prometheus.yml`

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'   # self-scrape
  - job_name: 'app'          # Python app :5000/metrics
  - job_name: 'loki'         # Loki :3100/metrics
  - job_name: 'grafana'      # Grafana :3000/metrics
```

Prometheus added to `docker-compose.yml`:
- Image: `prom/prometheus:v3.9.0`
- Port: `9090`
- Retention: 15 days / 10 GB
- Volume: `prometheus-data` for persistence

Verify targets: http://localhost:9090/targets — all should be **UP**.

---

## Task 3 — Grafana Dashboards

### Add Prometheus data source
- Connections → Data sources → Prometheus
- URL: `http://prometheus:9090`

### Dashboard panels (6+)

| Panel | Type | PromQL |
|-------|------|--------|
| Request Rate | Time series | `sum(rate(http_requests_total[5m])) by (endpoint)` |
| Error Rate | Time series | `sum(rate(http_requests_total{status=~"5.."}[5m]))` |
| p95 Latency | Time series | `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` |
| Latency Heatmap | Heatmap | `rate(http_request_duration_seconds_bucket[5m])` |
| Active Requests | Gauge | `http_requests_in_progress` |
| Status Distribution | Pie chart | `sum by (status) (rate(http_requests_total[5m]))` |
| Service Uptime | Stat | `up{job="app"}` |

---

## Task 4 — Production Configuration

### Health checks
All services have `healthcheck` blocks with `interval: 10s`, `retries: 5`.

### Resource limits

| Service | CPU limit | Memory limit |
|---------|-----------|--------------|
| Prometheus | 1.0 | 1G |
| Loki | 1.0 | 1G |
| Grafana | 1.0 | 512M |
| app-python | 0.5 | 256M |
| Promtail | 0.5 | 256M |

### Data retention
Prometheus: `--storage.tsdb.retention.time=15d --storage.tsdb.retention.size=10GB`

### Persistence
Named volumes: `prometheus-data`, `loki-data`, `grafana-data` — data survives `docker compose down`.

---

## PromQL Examples

```promql
# 1. Request rate per endpoint
sum(rate(http_requests_total[5m])) by (endpoint)

# 2. Error rate (5xx)
sum(rate(http_requests_total{status=~"5.."}[5m]))

# 3. p95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# 4. Active requests right now
http_requests_in_progress

# 5. Services up/down
up

# 6. CPU usage of app process
rate(process_cpu_seconds_total{job="app"}[5m]) * 100

# 7. Total requests last hour
increase(http_requests_total[1h])
```

---

## Metrics vs Logs

| | Logs (Lab 7) | Metrics (Lab 8) |
|---|---|---|
| What | Events with context | Numeric measurements over time |
| Storage | Loki (log lines) | Prometheus TSDB |
| Query | LogQL | PromQL |
| Best for | Debugging, audit trail | Alerting, trends, SLOs |
| Example | "User X got 404 at 12:03" | "Error rate = 2.3 req/s" |

Use both together: metrics alert you, logs explain why.

---

## Quick Start

```bash
cd monitoring
cp .env.example .env   # set GRAFANA_ADMIN_PASSWORD
docker compose up -d
docker compose ps      # all services should be healthy
```

Generate traffic to see metrics:
```bash
for i in {1..30}; do curl http://localhost:8000/; curl http://localhost:8000/health; done
```

Then open http://localhost:9090/targets and http://localhost:3000.

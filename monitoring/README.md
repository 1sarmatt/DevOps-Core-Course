# Loki Logging Stack

## Quick Start

1. **Start the stack:**
   ```bash
   docker compose up -d
   ```

2. **Verify services:**
   ```bash
   docker compose ps
   ```

3. **Access Grafana:**
   - URL: http://localhost:3000
   - Username: `admin`
   - Password: Check `.env` file (not committed to repo)

4. **Configure Loki Data Source in Grafana:**
   - Go to **Connections** → **Data sources** → **Add data source**
   - Select **Loki**
   - URL: `http://loki:3100`
   - Click **Save & Test**

5. **Explore Logs:**
   - Go to **Explore** (compass icon in left menu)
   - Select **Loki** data source
   - Try queries:
     - `{job="docker"}` - all Docker logs
     - `{app="devops-python"}` - Python app logs
     - `{app="devops-python"} | json` - parse JSON logs
     - `{app="devops-python"} | json | level="INFO"` - filter by level

## Generate Traffic

```bash
# Generate some logs
for i in {1..20}; do 
  curl http://localhost:8000/
  curl http://localhost:8000/health
done
```

## Services

- **Loki**: http://localhost:3100 - Log aggregation
- **Grafana**: http://localhost:3000 - Visualization
- **Promtail**: Collects logs from Docker containers
- **Python App**: http://localhost:8000 - Demo application with JSON logging

## LogQL Query Examples

```logql
# All logs from Python app
{app="devops-python"}

# Only errors
{app="devops-python"} | json | level="ERROR"

# Requests to specific path
{app="devops-python"} | json | path="/health"

# Count logs per second
rate({app="devops-python"}[1m])

# Count by log level
sum by (level) (count_over_time({app="devops-python"} | json [5m]))
```

## Troubleshooting

**Loki not starting:**
```bash
docker compose logs loki
```

**Promtail not collecting logs:**
```bash
docker compose logs promtail
curl http://localhost:9080/targets
```

**No logs in Grafana:**
- Check Loki data source is configured correctly
- Verify containers have label `logging: "promtail"`
- Check Promtail is running and connected to Loki

## Stop Stack

```bash
docker compose down
```

## Clean Up (including data)

```bash
docker compose down -v
```

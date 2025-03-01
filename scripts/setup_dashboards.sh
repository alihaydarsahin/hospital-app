#!/bin/bash

# Exit on error
set -e

echo "Setting up Grafana dashboards..."

# Wait for Grafana to be ready
until $(curl --output /dev/null --silent --head --fail http://localhost:3000); do
    printf '.'
    sleep 5
done

# Create API key
API_KEY=$(curl -X POST -H "Content-Type: application/json" -d '{"name":"admin", "role": "Admin"}' http://admin:admin@localhost:3000/api/auth/keys | jq -r .key)

# Add Prometheus data source
curl -X POST \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{
        "name":"Prometheus",
        "type":"prometheus",
        "url":"http://localhost:9090",
        "access":"proxy",
        "isDefault":true
    }' \
    http://localhost:3000/api/datasources

# Create System Monitoring Dashboard
curl -X POST \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{
        "dashboard": {
            "title": "System Monitoring",
            "panels": [
                {
                    "title": "CPU Usage",
                    "type": "graph",
                    "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
                    "targets": [
                        {
                            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
                            "legendFormat": "CPU Usage"
                        }
                    ]
                },
                {
                    "title": "Memory Usage",
                    "type": "graph",
                    "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
                    "targets": [
                        {
                            "expr": "100 * (1 - ((node_memory_MemFree_bytes + node_memory_Cached_bytes + node_memory_Buffers_bytes) / node_memory_MemTotal_bytes))",
                            "legendFormat": "Memory Usage"
                        }
                    ]
                }
            ]
        },
        "folderId": 0,
        "overwrite": true
    }' \
    http://localhost:3000/api/dashboards/db

# Create Application Dashboard
curl -X POST \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{
        "dashboard": {
            "title": "Hospital App Monitoring",
            "panels": [
                {
                    "title": "HTTP Request Rate",
                    "type": "graph",
                    "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
                    "targets": [
                        {
                            "expr": "rate(flask_http_request_total[5m])",
                            "legendFormat": "Requests/sec"
                        }
                    ]
                },
                {
                    "title": "Response Time",
                    "type": "graph",
                    "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
                    "targets": [
                        {
                            "expr": "rate(flask_http_request_duration_seconds_sum[5m]) / rate(flask_http_request_duration_seconds_count[5m])",
                            "legendFormat": "Average Response Time"
                        }
                    ]
                }
            ]
        },
        "folderId": 0,
        "overwrite": true
    }' \
    http://localhost:3000/api/dashboards/db

echo "Grafana dashboards setup completed!"
echo "Access your dashboards at http://localhost:3000"
echo "Default login: admin/admin (please change the password)" 
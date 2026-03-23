# Kubernetes-Mcp

An MCP server for Kubernetes observability and diagnostics.

This project exposes LLM-friendly tools for inspecting a Kubernetes cluster through:

- Kubernetes API
- Prometheus
- Jaeger
- Neo4j
- controlled shell execution

It is designed so an MCP client or agent can query cluster topology, logs, metrics, traces, and service dependencies through a single server.

---


## How to run

### 1. Install dependencies

From the project root:
```
poetry install
```
### 2. Create your environment file

Copy the template:
```
cp .env.example .env
```
On Windows PowerShell:
```
Copy-Item .env.example .env
```
Then fill in the values you need in .env, for example:
```
K8S_NAMESPACE=default
PROMETHEUS_URL=http://localhost:9090
JAEGER_URL=http://localhost:16686
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=yourpassword
NEO4J_DATABASE=neo4j
```
### 3. Start the MCP server
```
poetry run python main.py
```
If you added the Poetry script entry, you can also run:
```
poetry run kubernetes-mcp
```
### 4. Run the smoke test
```
poetry run python -m tests.smoke_test
```
This checks:
- backend availability
- Kubernetes topology
- logs
- metrics
- shell execution
- optional trace and graph integration

### 5. Optional local backends

Start Jaeger locally:
```
docker run --rm --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest
```
Start Neo4j locally:
```
docker run --rm --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/testpassword123 \
  neo4j:latest
```
Then set in .env:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=testpassword123
NEO4J_DATABASE=neo4j
```
Prometheus must be reachable at the URL configured in .env, for example:
```
PROMETHEUS_URL=http://localhost:9090
```
If Prometheus is running inside your cluster, you can expose it with kubectl port-forward.


## Features

### Topology
- Cluster overview of pods and services
- Resolve service -> pods
- Resolve pod -> services
- Service dependency queries from Neo4j
- Service neighborhood map from Neo4j
- Combined runtime + graph topology summary

### Metrics
- Pod metrics from Prometheus
- Service metrics aggregated from pod metrics
- Pod time-range metrics
- Service time-range metrics
- Pod triage metrics
- Service triage metrics

### Logs
- Read pod logs
- Read service logs across all selected pods
- Important-line filtering
- Pod log summaries
- Service log summaries

### Traces
- Trace summaries from Jaeger
- Trace details by trace ID
- Error-focused trace inspection

### Shell
- Restricted shell execution
- Restricted kubectl execution
- Safe command policy inspection

---

## Project structure
```text
Kubernetes-Mcp/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── dependencies.py
│   └── server.py
│
├── clients/
│   ├── __init__.py
│   ├── base_k8s_client.py
│   ├── jaeger_client.py
│   ├── neo4j_client.py
│   ├── prometheus_client.py
│   └── shell_client.py
│
├── services/
│   ├── __init__.py
│   ├── logs_service.py
│   ├── metrics_service.py
│   ├── shell_service.py
│   ├── system_service.py
│   ├── topology_service.py
│   └── trace_service.py
│
├── tools/
│   ├── __init__.py
│   ├── logs.py
│   ├── metrics.py
│   ├── shell.py
│   ├── system.py
│   ├── topology.py
│   └── traces.py
│
├── utils/
│   ├── __init__.py
│   └── formatters.py
│
├── tests/
│   ├── __init__.py
│   └── smoke_test.py
│
├── .env.example
├── .gitignore
├── main.py
├── pyproject.toml
├── poetry.lock
└── README.md
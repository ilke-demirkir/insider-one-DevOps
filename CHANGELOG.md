# Changelog

## v0.3.1

- Added Prometheus `ServiceMonitor` and `PrometheusRule` support to the Helm chart.
- Added Grafana dashboard JSON for request rate, latency p95, error ratio, and pod restarts.
- Added architecture diagram documentation for the public URL, Kubernetes, app, and observability flow.
- Verified the public EC2 demo through `http://54.76.70.155:30080/ping`.
- Updated chart metadata to `0.3.1`.
- Added automatic patch version resolution to the CI pipeline while keeping manual release dispatch support.

## v0.1.0

- Added minimal FastAPI service with `/ping`, `/healthz`, and `/version` endpoints.
- Added unit tests for the core HTTP endpoints.
- Added multi-stage Docker image with non-root runtime user and healthcheck.
- Added Docker Compose for local development checks.
- Added GitHub Actions CI for tests, image build, secret scanning, vulnerability scanning, GHCR publishing, and release creation.
- Added Helm chart for Kubernetes deployment with dev/prod values, probes, resources, ingress, rollback testing, and local minikube verification.
- Remediated image scan findings by upgrading FastAPI/Starlette and fixed Debian runtime packages in the Docker image.

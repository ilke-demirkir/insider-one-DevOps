# Changelog

## v0.1.0

- Added minimal FastAPI service with `/ping`, `/healthz`, and `/version` endpoints.
- Added unit tests for the core HTTP endpoints.
- Added multi-stage Docker image with non-root runtime user and healthcheck.
- Added Docker Compose for local development checks.
- Added GitHub Actions CI for tests, image build, secret scanning, vulnerability scanning, GHCR publishing, and release creation.
- Added Helm chart for Kubernetes deployment with dev/prod values, probes, resources, ingress, rollback testing, and local minikube verification.
- Remediated image scan findings by upgrading FastAPI/Starlette and fixed Debian runtime packages in the Docker image.

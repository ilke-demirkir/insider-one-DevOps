# ADR 0002: Use Helm

## Status

Accepted

## Context

The app must be deployed to Kubernetes with clear dev/prod differences and rollback evidence.

## Decision

Use a Helm chart with separate dev and prod values files.

## Consequences

Helm keeps Deployment, Service, Ingress, ConfigMap, and optional HPA definitions reusable. `values-dev.yaml` and `values-prod.yaml` make environment differences explicit. Helm history and rollback commands provide useful operational evidence.

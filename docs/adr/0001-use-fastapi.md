# ADR 0001: Use FastAPI

## Status

Accepted

## Context

The case study needs a small HTTP service with health, version, and metrics endpoints.

## Decision

Use Python FastAPI because it is quick to implement, easy to test, and suitable for a small HTTP API.

## Consequences

FastAPI keeps the app code small and readable. It also gives simple testing through `TestClient`. The main tradeoff is that Python images can be larger than a static Go binary, so the Dockerfile uses a slim base and non-root runtime user.

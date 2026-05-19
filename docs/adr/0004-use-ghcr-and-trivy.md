# ADR 0004: Use GHCR, Gitleaks, and Trivy

## Status

Accepted

## Context

The CI/CD flow needs image publishing and basic supply chain checks.

## Decision

Use GitHub Container Registry for image storage, gitleaks for secret scanning, and Trivy for image vulnerability scanning.

## Consequences

GHCR integrates cleanly with GitHub Actions and the repository permissions model. gitleaks helps catch accidental credential commits. Trivy blocks images with `HIGH` or `CRITICAL` vulnerabilities, which already caught findings that were remediated in the Docker image.

# Security

## Secrets

- Real secrets are not committed to the repository.
- `.env` and Terraform state/tfvars files are ignored.
- `.env.example` and `terraform.tfvars.example` document required values without containing secrets.

## CI checks

- gitleaks scans the repository for committed secrets.
- Trivy scans the built container image.
- The Trivy step fails on `HIGH` and `CRITICAL` findings.

## Container hardening

- The Docker image runs as a non-root user.
- Kubernetes sets `runAsNonRoot`.
- The container security context drops Linux capabilities and disables privilege escalation.
- Runtime Debian packages are upgraded to remediate known image scan findings.

## AWS access

- SSH access is restricted through `ssh_allowed_cidr`.
- The app demo port is exposed separately from SSH.
- AWS credentials are configured locally and are not stored in the repository.

## Rotation notes

If a credential is suspected to be exposed:

1. Revoke or rotate it in AWS/GitHub immediately.
2. Remove it from local files.
3. Run gitleaks.
4. Re-run the CI pipeline.

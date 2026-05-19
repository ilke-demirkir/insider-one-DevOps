# ADR 0003: Use AWS EC2 With Minikube

## Status

Accepted

## Context

The selected track is AWS, but the case study does not require a production-grade managed Kubernetes cluster.

## Decision

Run minikube on a single AWS EC2 instance and expose the app through an Elastic IP.

## Consequences

This keeps the infrastructure small and inexpensive while still showing the full path from image to Kubernetes deployment. AWS provides the host and public network entry point; Kubernetes lifecycle is still handled inside minikube with Helm.

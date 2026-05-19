# Runbook

## Scope

This runbook covers the FastAPI service deployed to minikube with Helm.

## Health checks

```bash
kubectl get pods
kubectl get svc
kubectl rollout status deployment/app-insiderone-devops-app
curl http://<public-url>/ping
curl http://<public-url>/healthz
```

## Logs

Application logs are structured JSON and can be read from the app pods:

```bash
kubectl logs -l app.kubernetes.io/instance=app
```

## Metrics

The app exposes Prometheus metrics on:

```text
/metrics
```

Local check through port-forward:

```bash
kubectl port-forward svc/app-insiderone-devops-app 8080:80
curl http://localhost:8080/metrics
```

## Restart

```bash
kubectl rollout restart deployment/app-insiderone-devops-app
kubectl rollout status deployment/app-insiderone-devops-app
```

## Rollback

```bash
helm history app
helm rollback app <REVISION>
kubectl rollout status deployment/app-insiderone-devops-app
```

## Public exposure

For the AWS minikube demo, the app can be exposed through a host-level port-forward:

```bash
kubectl port-forward --address 0.0.0.0 svc/app-insiderone-devops-app 30080:80
```

Then verify from a laptop:

```bash
curl http://<Elastic-IP>:30080/ping
```

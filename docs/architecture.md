# Architecture

```mermaid
flowchart LR
    user[User / reviewer] --> public[Public URL / Elastic IP]
    public --> pf[Host port-forward or ingress]
    pf --> svc[Kubernetes Service]
    svc --> pod[FastAPI app pod]

    pod --> logs[JSON stdout logs]
    pod --> metrics[/metrics/]

    prom[Prometheus] -->|ServiceMonitor scrape| metrics
    prom --> rules[PrometheusRule alerts]
    grafana[Grafana] -->|Prometheus datasource| prom
    alertmanager[Alertmanager] --> rules

    subgraph minikube[minikube on EC2 or local]
        svc
        pod
        prom
        grafana
        alertmanager
        rules
    end
```

## Notes

- The app is packaged as a Docker image and deployed with the Helm chart in `chart/insiderone-devops-app`.
- Prometheus discovers app metrics through the chart's `ServiceMonitor`.
- Grafana uses the Prometheus datasource installed by `kube-prometheus-stack`.
- The high-error-rate alert is managed as a `PrometheusRule` in the app chart.

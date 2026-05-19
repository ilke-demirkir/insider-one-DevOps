Projenin kod kısmı minimal olduğu için burayı biraz günlük gibi kullanıp, gün gün yaptıklarımı dokümante etmeye karar verdim.
Elbette endpointler ile ilgili ve uygulamanın infrastructure'ı ile bilgileri de bunun sonunda paylaşıyor olacağım.

## Gün 0 -- 15 Mayıs sunumun yapıldığı ve case studylerin atıldığı gün

Daha önce AWS ile deployment deneyimim vardı, dolayısıyla AWS kullanmayı tercih ettim. Benzer şekilde Docker'a da aşina olsam da
kubernetes, helm ve security scanning hala deneyimlemediğim teknolojiler.

Dil olarak python FastAPI en rahat tercihim olucak diye düşünüyorum, özellikle küçük bir app için. O yüzden onu kullanmaya karar verdim.

Sonra adımda minimal FastAPI servisini oluşturdum. Servis üç temel endpoint içeriyor. (Bu kısmı AI ile yaptım, küçük bir app olduğu için fazla sakınca görmedim):

- `GET /ping`: basit canlılık kontrolü için `pong` döner.
- `GET /healthz`: Kubernetes liveness/readiness probe'ları için `{"status": "ok"}` döner.
- `GET /version`: uygulama versiyonu ve build SHA bilgisini döner.

### Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Test

```bash
pytest
```

### Quick checks

```bash
curl http://localhost:8000/ping
curl http://localhost:8000/healthz
curl http://localhost:8000/version
```

### Docker

```bash
docker build -t insiderone-devops-app:local .
docker run --rm -p 8000:8000 -e APP_VERSION=0.1.0 -e GIT_SHA="$(git rev-parse --short HEAD)" insiderone-devops-app:local
```

### Docker Compose

```bash
GIT_SHA="$(git rev-parse --short HEAD)" docker compose up --build
```

Servisi durdurmak için:

```bash
docker compose down
```

## Gün 1 --
Elimde çalışan bir docker image'ı var, artık CI/CD ve kubernetes kısmı gelmeli. Anlaşılan bana bir helm chart lazımmış, eğer doğru anladıysam Docker ve Kubernetes arasında iletişim kuran bir katman gibi çalışıyor. Farklı environmentlar deploylanabiliyor aynı dosya üzerinden.

### CI

İlk CI akışı `.github/workflows/ci.yaml` altında. Pull request ve `main` branch'e push durumunda iki kontrol çalışıyor:

- Python bağımlılıklarını kurup `pytest` çalıştırır.
- Testler başarılı olursa Docker imajını build eder.

Trivy image scan, GHCR push ve release adımları daha sonra bu akışın üzerine eklenecek.

### Helm chart

Kubernetes deploy tanımı `chart/insiderone-devops-app` altında tutuluyor. Chart içinde Deployment, Service, Ingress, ConfigMap,
Secret placeholder, ServiceAccount ve opsiyonel HPA template'leri var.

Dev ortamı için:

```bash
helm upgrade --install app ./chart/insiderone-devops-app \
  -f chart/insiderone-devops-app/values-dev.yaml \
  --rollback-on-failure \
  --timeout 3m
```

Prod benzeri değerlerle:

```bash
helm upgrade --install app ./chart/insiderone-devops-app \
  -f chart/insiderone-devops-app/values-prod.yaml \
  --rollback-on-failure \
  --timeout 3m
```

Kontrol komutları:

```bash
kubectl get pods
kubectl rollout status deployment/app-insiderone-devops-app
helm history app
helm list
```

Rollback:

```bash
helm rollback app <REVISION>
```

Helm 4.2.0 ile `--rollback-on-failure` kullanımı, upgrade sırasında pod'lar sağlıklı hale gelmezse Helm'in önceki başarılı
release'e otomatik dönmesini sağlar. Bu flag aynı zamanda wait davranışını da aktif eder.

## Gün 2 --
Minikube üzerinde ilk Helm deploy denemesini yaptım. Önce local Docker imajını oluşturdum, sonra imajı minikube içine yükledim:

```bash
docker build -t insiderone-devops-app:local .
minikube image load insiderone-devops-app:local
```

Ardından dev values dosyasıyla Helm release'i kurdum:

```bash
helm upgrade --install app ./chart/insiderone-devops-app \
  -f chart/insiderone-devops-app/values-dev.yaml \
  --rollback-on-failure \
  --timeout 3m
```

Deploy çıktısı başarılıydı:

```text
Release "app" does not exist. Installing it now.
NAME: app
NAMESPACE: default
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
```

Helm release durumu:

```text
NAME  NAMESPACE  REVISION  UPDATED                              STATUS    CHART                         APP VERSION
app   default    1         2026-05-16 16:59:40.805202 +0300 +03 deployed  insiderone-devops-app-0.1.0   0.1.0
```

Helm history:

```text
REVISION  UPDATED                  STATUS    CHART                         APP VERSION  DESCRIPTION
1         Sat May 16 16:59:40 2026 deployed  insiderone-devops-app-0.1.0   0.1.0        Install complete
```

Pod durumu:

```text
NAME                                         READY   STATUS    RESTARTS   AGE
app-insiderone-devops-app-75d7b77dc9-6qvdr   1/1     Running   0          10m
```

Service durumu:

```text
NAME                        TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
app-insiderone-devops-app   ClusterIP   10.101.239.47   <none>        80/TCP    10m
kubernetes                  ClusterIP   10.96.0.1       <none>        443/TCP   44m
```

Rollout kontrolü:

```text
deployment "app-insiderone-devops-app" successfully rolled out
```

Bu checkpoint ile Docker imajının minikube üzerinde Helm chart aracılığıyla deploy edilebildiğini, pod'un sağlıklı şekilde ayağa
kalktığını ve Kubernetes Service'in oluştuğunu doğrulamış oldum.

Bu helm ile ilk deniyimim, dolayısıyla AI toollardan yardım aldım templatelar yazılırken. Anladığım kadarıyla bu templatelar kubernetes podu oluşturulurken kullandığımız değişkenler. Farklı dosyalarda olmalarının sebebi bu şekilde daha düzenli olması.
Bu templates klasörü içindeki templateler values.yaml, values-dev.yaml veya values-prod.yaml ile birleşerek bir kubernetes manifestosu oluşturabiliyor. Bu sayede ortak config parametrelerini klasörün içinde, farklı environmentları da bu value yaml dosyalarında tanımlayabiliyoruz. 

Rollback davranışını test etmek için bilerek hatalı bir image tag ile upgrade denedim:

```bash
helm upgrade app ./chart/insiderone-devops-app \
  -f chart/insiderone-devops-app/values-dev.yaml \
  --set image.tag=bad-tag \
  --rollback-on-failure \
  --timeout 1m
```

Beklendiği gibi upgrade başarısız oldu ve Helm önceki başarılı release'e otomatik döndü:

```text
level=WARN msg="upgrade failed" name=app error="resource Deployment/default/app-insiderone-devops-app not ready. status: InProgress, message: Pending termination: 1\ncontext deadline exceeded"
Error: UPGRADE FAILED: release app failed, and has been rolled back due to rollback-on-failure being set: resource Deployment/default/app-insiderone-devops-app not ready. status: InProgress, message: Pending termination: 1
context deadline exceeded
```

Rollback sonrası Helm history:

```text
REVISION  UPDATED                   STATUS      CHART                         APP VERSION  DESCRIPTION
1         Sat May 16 16:59:40 2026  superseded  insiderone-devops-app-0.1.0   0.1.0        Install complete
2         Sat May 16 18:20:31 2026  failed      insiderone-devops-app-0.1.0   0.1.0        Upgrade "app" failed: resource Deployment/default/app-insiderone-devops-app not ready...
3         Sat May 16 18:21:32 2026  deployed    insiderone-devops-app-0.1.0   0.1.0        Rollback to 1
```

Pod rollback sonrasında çalışır durumda kaldı:

```text
NAME                                         READY   STATUS    RESTARTS   AGE
app-insiderone-devops-app-75d7b77dc9-6qvdr   1/1     Running   0          82m
```

Kubernetes Service üzerinden erişimi doğrulamak için local port-forward açtım:

```bash
kubectl port-forward svc/app-insiderone-devops-app 8080:80
```

Başka bir terminalden endpoint kontrolleri:

```bash
curl http://localhost:8080/ping
curl http://localhost:8080/healthz
curl http://localhost:8080/version
```

Çıktı:

```text
"pong"
{"status":"ok"}
{"version":"0.1.0-dev","sha":"local"}
```

Bu adımla app'in sadece pod olarak çalıştığını değil, Kubernetes Service üzerinden de erişilebilir olduğunu doğrulamış oldum.

Ingress erişimini test etmek için minikube ingress addon'unu kullandım. macOS üzerinde Docker driver ile minikube IP'sine doğrudan
erişim her zaman çalışmadığı için ingress-nginx controller servisini local porta forward ettim:

```bash
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8081:80
```

Ingress host routing'i `values-dev.yaml` içinde `dev.insiderone.local` olarak tanımlı olduğu için curl isteğinde Host header'ı verdim:

```bash
curl -H "Host: dev.insiderone.local" http://localhost:8081/ping
curl -H "Host: dev.insiderone.local" http://localhost:8081/healthz
curl -H "Host: dev.insiderone.local" http://localhost:8081/version
```

Çıktı:

```text
"pong"
{"status":"ok"}
{"version":"0.1.0-dev","sha":"local"}
```

Bu test, trafiğin ingress-nginx controller üzerinden Ingress rule'a, oradan Kubernetes Service'e ve son olarak FastAPI pod'una
ulaştığını doğruluyor. Daha önceki `8080` port-forward doğrudan app Service'e gidiyordu; `8081` testinde ise Ingress katmanı da
akışa dahil edildi.

## Gün 3 --
CI/CD akışını supply chain kontrolleriyle genişlettim. `.github/workflows/ci.yaml` artık pull request, `main` push, `v*.*.*`
tag push ve manuel release workflow eventlerinde çalışıyor.

Pull request akışında:

- Python bağımlılıkları kuruluyor ve `pytest` çalışıyor.
- Repo içinde secret taraması için gitleaks çalışıyor.
- Docker image build ediliyor.
- Trivy image scan `HIGH` ve `CRITICAL` bulgularda pipeline'ı kıracak şekilde çalışıyor.

`main` branch'e push edildiğinde ek olarak:

- GHCR login yapılıyor.
- Image `ghcr.io/ilke-demirkir/insiderone-devops-app` altına push ediliyor.
- Image tag'leri Git SHA bazlı ve `latest` olarak üretiliyor.

Release için manuel Git tag komutu yerine GitHub Actions içinden `workflow_dispatch` kullanıyorum. Actions ekranından `CI`
workflow'u seçilip `Run workflow` ile `version` alanına örneğin `v0.1.0` giriliyor.

Bu manuel release akışı:

- Testleri çalıştırır.
- Secret scan ve Trivy image scan adımlarını çalıştırır.
- Image'i GHCR'a SHA tag'i ve release tag'i ile push eder.
- Git tag'i oluşturup remote'a push eder.
- GitHub Release oluşturur.

Tag formatını `vMAJOR.MINOR.PATCH` ile sınırladım; örneğin `v0.1.0`. Dışarıdan elle tag push edilirse de `v*.*.*` tag event'i
aynı release job'ını çalıştırmaya devam eder.

Trivy tarafında özellikle sabit ve güvenli action versiyonu kullanmaya dikkat ettim:

```yaml
uses: aquasecurity/trivy-action@v0.35.0
```

Bunun sebebi, güvenlik taraması yapan aracın kendisinin de supply chain riskinin parçası olabilmesi. Bu yüzden floating branch
ya da eski tag yerine güvenli olduğu belirtilen sabit versiyon kullanıldı.

İlk image scan sonucunda dört adet HIGH seviye bulgu gördüm. Bunları iki seviyede düzelttim:

- Python tarafında FastAPI `0.136.1` ve Starlette `0.49.1` sürümlerine geçildi.
- Docker runtime image içinde Debian paketleri güncellendi: `libcap2`, `libsystemd0`, `libudev1`.

Rebuild sonrasında image içindeki versiyonları doğruladım:

```text
libcap2:arm64      1:2.75-10+deb13u1+b1
libsystemd0:arm64  257.13-1~deb13u1
libudev1:arm64     257.13-1~deb13u1
fastapi==0.136.1
starlette==0.49.1
```

Gün 4'e geçmeden önce AWS Track A tarafı için minimal IaC iskeletini ekledim. `infra/aws` altında Terraform/OpenTofu dosyaları
EC2 instance, Elastic IP ve security group tanımlıyor. Security group iki girişi özellikle ayırıyor:

- SSH sadece benim public IP adresimden gelecek şekilde `ssh_allowed_cidr` ile sınırlandırılıyor.
- Uygulama için Helm prod values içinde tanımlı `30080` NodePort dışarı açılıyor.

Örnek değişken dosyası:

```bash
cp infra/aws/terraform.tfvars.example infra/aws/terraform.tfvars
```

`infra/aws/terraform.tfvars` içinde en az şu iki değeri değiştirmek gerekiyor:

```hcl
ssh_key_name     = "aws-keypair-name"
ssh_allowed_cidr = "x.x.x.x/32"
```

Plan ve apply:

```bash
cd infra/aws
terraform init
terraform plan
terraform apply
```

Terraform apply sonrası EC2 instance ve Elastic IP başarıyla oluştu. Oluşan output'taki SSH komutunu `.pem` dosyam ile kullanarak
instance'a bağlanabildim:

```bash
ssh -i ~/.ssh/<key-file>.pem ubuntu@<Elastic-IP>
```

Bu checkpoint ile AWS tarafında EC2 host, security group, Elastic IP ve SSH erişimi doğrulanmış oldu. Bundan sonraki adım aynı
host üzerinde `user-data.sh` ile kurulan minikube ortamının hazır olduğunu kontrol etmek ve release image'ini Helm prod values ile
deploy etmek.

Terraform/OpenTofu local state dosyaları ve gerçek `terraform.tfvars` dosyası `.gitignore` içine alındı; repo'ya sadece örnek
tfvars dosyası giriyor.

EC2 ilk açıldığında `user-data.sh` Docker, kubectl, minikube ve Helm kurulumlarını yapıyor ve minikube'u Docker driver ile başlatıyor.
Helm özellikle `v4.2.0` olarak kuruluyor; sebebi localde kullandığım `--rollback-on-failure` flag'inin Helm 4 davranışı olması.
Default instance tipi `t3.small` olduğu için bootstrap script'i minikube'u `1800mb` memory ile başlatıyor ve küçük bir swap file
oluşturuyor. Daha yüksek kaynak için `t3.medium` gibi bir instance tipi seçilebilir.

Eğer minikube ayakta görünmüyorsa ilk bakılacak yer cloud-init çıktısı:

```bash
sudo tail -n 100 /var/log/cloud-init-output.log
```

Instance hazır olduktan sonra Terraform output'unda görünen SSH komutuyla bağlanıp repoyu klonlamak gerekiyor:

```bash
git clone https://github.com/ilke-demirkir/insider-one-DevOps.git
cd insider-one-DevOps
```

Sonra release image'i deploy edilebilir:

```bash
helm upgrade --install app ./chart/insiderone-devops-app \
  -f chart/insiderone-devops-app/values-prod.yaml \
  --set image.tag=v0.1.0 \
  --set config.gitSha=<release-sha> \
  --rollback-on-failure \
  --timeout 3m
```

Prod values dosyasında Service tipi `NodePort`, port ise `30080`. Bu yüzden public test URL'i şu formatta olacak:

```text
http://<Elastic-IP>:30080/ping
```

EC2 üzerinde Helm deploy başarılı şekilde çalıştı:

```bash
helm upgrade --install app ./chart/insiderone-devops-app \
  -f chart/insiderone-devops-app/values-prod.yaml \
  --set image.tag=v0.1.0 \
  --set config.gitSha=local \
  --rollback-on-failure \
  --timeout 3m
```

Pod'lar healthy ve rollout başarılıydı:

```text
app-insiderone-devops-app-5574f4cc75-qvwqs   1/1   Running   0
app-insiderone-devops-app-5574f4cc75-tvcgk   1/1   Running   0
deployment "app-insiderone-devops-app" successfully rolled out
```

Minikube node IP üzerinden EC2 içinde test edildiğinde app cevap verdi:

```bash
curl http://$(minikube ip):30080/ping
```

Çıktı:

```text
"pong"
```

Docker driver ile çalışan minikube'da NodePort, EC2 host'un public network interface'inde otomatik olarak dinlemiyor. Bu yüzden
public demo için EC2 üzerinde app Service'i public interface'e port-forward ettim:

```bash
kubectl port-forward --address 0.0.0.0 svc/app-insiderone-devops-app 30080:80
```

Sonrasında laptop üzerinden Elastic IP ile public erişim doğrulandı:

```bash
curl http://<Elastic-IP>:30080/ping
```

Çıktı:

```text
"pong"
```

Bu yöntem terminal açık kaldığı sürece public demo için yeterli. Daha kalıcı bir çözüm gerekirse aynı komut küçük bir `systemd`
servisine taşınabilir veya minikube/Ingress için host-level reverse proxy kurulabilir.

Gün 4 --
Operability tarafı için uygulamaya yapılandırılmış JSON request logları ve Prometheus formatında `/metrics` endpoint'i ekledim.
Her request için `request_id`, method, path, status ve duration bilgisi loglanıyor. `/metrics` tarafında request count ve latency
metrikleri expose ediliyor.

Local test:

```bash
pytest
```

Sonuç:

```text
4 passed
```

Kubernetes tarafında pod annotation'ları Prometheus scrape için eklendi:

```yaml
prometheus.io/scrape: "true"
prometheus.io/path: /metrics
prometheus.io/port: "8000"
```

Operasyon dokümanları da eklendi:

- `RUNBOOK.md`: health check, log bakma, metrics, restart, rollback ve public demo adımları.
- `SECURITY.md`: secret yönetimi, CI security kontrolleri, container hardening ve credential rotation notları.
- `docs/adr`: FastAPI, Helm, AWS EC2/minikube ve supply chain karar kayıtları.

Monitoring stack için `kube-prometheus-stack` Helm chart'ını `monitoring` namespace'i altında kurdum:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

Kurulum sonrası tüm monitoring pod'ları Running durumda:

```text
NAME                                                     READY   STATUS    RESTARTS   AGE
alertmanager-monitoring-kube-prometheus-alertmanager-0   2/2     Running   0          68s
monitoring-grafana-5948d86fbd-66j8r                      3/3     Running   0          73s
monitoring-kube-prometheus-operator-797dd746d4-lvzk7     1/1     Running   0          73s
monitoring-kube-state-metrics-5957bd45bc-rdmld           1/1     Running   0          73s
monitoring-prometheus-node-exporter-wr7zx                1/1     Running   0          73s
prometheus-monitoring-kube-prometheus-prometheus-0       2/2     Running   0          67s
```

Bu checkpoint ile Prometheus, Grafana, Alertmanager, kube-state-metrics ve node-exporter bileşenlerinin minikube üzerinde sağlıklı
şekilde çalıştığını doğrulamış oldum.

Uygulama chart'ına `PrometheusRule` template'i ekledim. Alert kuralı, son 5 dakika içinde 5xx response görülürse uyarı üretmek
üzere tanımlı:

```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) > 0
```

Rule'un Prometheus Operator tarafından alınması için `release: monitoring` label'ı kullanılıyor. Chart render kontrolü:

```bash
helm lint ./chart/insiderone-devops-app
helm template app ./chart/insiderone-devops-app -f chart/insiderone-devops-app/values-prod.yaml
```

Cluster'a uygulamak için app release'i tekrar upgrade edilir:

```bash
helm upgrade --install app ./chart/insiderone-devops-app \
  -f chart/insiderone-devops-app/values-prod.yaml \
  --set image.tag=v0.2.0 \
  --set config.appVersion=0.2.0 \
  --set config.gitSha=<release-sha> \
  --rollback-on-failure \
  --timeout 3m
```

Alert rule doğrulama:

```bash
kubectl get prometheusrule
kubectl describe prometheusrule app-insiderone-devops-app
```

AWS kaynakları ücret yazmaması için test bittikten sonra kapatılmalı:

```bash
cd infra/aws
terraform destroy
```

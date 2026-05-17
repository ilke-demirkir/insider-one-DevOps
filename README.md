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

Gün 2 --
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

Gün 3 --
CI/CD akışını supply chain kontrolleriyle genişlettim. `.github/workflows/ci.yaml` artık pull request, `main` push ve `v*.*.*`
tag push eventlerinde çalışıyor.

Pull request akışında:

- Python bağımlılıkları kuruluyor ve `pytest` çalışıyor.
- Repo içinde secret taraması için gitleaks çalışıyor.
- Docker image build ediliyor.
- Trivy image scan `HIGH` ve `CRITICAL` bulgularda pipeline'ı kıracak şekilde çalışıyor.

`main` branch'e push edildiğinde ek olarak:

- GHCR login yapılıyor.
- Image `ghcr.io/ilke-demirkir/insiderone-devops-app` altına push ediliyor.
- Image tag'leri Git SHA bazlı ve `latest` olarak üretiliyor.

Release için ilk versiyonu manuel tag ile oluşturacağım:

```bash
git tag v0.1.0
git push origin v0.1.0
```

`v0.1.0` tag'i push edildiğinde CI aynı test, secret scan, build ve Trivy scan adımlarını çalıştıracak; ardından image'i GHCR'a
`v0.1.0` ve SHA tag'leriyle push edecek ve GitHub Release oluşturacak.

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

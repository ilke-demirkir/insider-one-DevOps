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

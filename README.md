Projenin kod kısmı minimal olduğu için burayı biraz günlük gibi kullanıp, gün gün yaptıklarımı dokümante etmeye karar verdim.
Elbette endpointler ile ilgili ve uygulamanın infrastructure'ı ile bilgileri de bunun sonunda paylaşıyor olacağım.

Gün 0 -- 15 Mayıs sunumun yapıldığı ve case studylerin atıldığı gün

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

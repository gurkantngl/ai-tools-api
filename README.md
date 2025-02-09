# AI Tool API 🤖

Bu proje, yapay zeka tabanlı araçlar sunan bir REST API servisi ve bu servisi kullanan bir web arayüzüdür.

## 🌟 Özellikler

- 📝 **Döküman İşlemleri**
  - Metin dosyası yükleme (.txt, .pdf, .md, .rst)
  - Vektör tabanlı benzerlik araması
  - Önbellek desteği
- 🔢 **Matematik İşlemleri**
  - Çoklu sayı çarpma işlemi
- 🔑 **Anahtar Kelime Çıkarma**
  - Google Gemini AI ile metin analizi
  - Özelleştirilebilir anahtar kelime sayısı

## 🚀 Başlangıç

### Gereksinimler

- Python 3.11+
- Docker ve Docker Compose
- Google Gemini API Anahtarı

### Kurulum

1. Projeyi klonlayın:
```bash
git clone https://github.com/[kullanıcı-adı]/ai-tool-api.git
cd ai-tool-api
```

2. .env dosyasını oluşturun:
```bash
cp .env.example .env
```

3. .env dosyasını düzenleyin ve Google API anahtarınızı ekleyin:
```
GOOGLE_API_KEY=your_api_key_here
```

4. Docker ile çalıştırın:
```bash
docker-compose up --build
```

### Kullanım

Uygulama başlatıldıktan sonra:
- FastAPI servisi: http://localhost:8000
- Streamlit arayüzü: http://localhost:8501
- API dökümantasyonu: http://localhost:8000/docs

## 🛠️ Teknolojiler

- **Backend**
  - FastAPI
  - ChromaDB (Vektör Veritabanı)
  - Google Gemini AI
  - Redis (Önbellek)
  - Prometheus (Metrik Toplama)

- **Frontend**
  - Streamlit
  - Custom CSS Theming

## 📊 Metrikler ve İzleme

- Prometheus metrikleri: http://localhost:8000/metrics
- Request loglama
- Performans izleme

## 🧪 Testler

Testleri çalıştırmak için:

```bash
pytest tests/
```

## 🔒 Güvenlik

- Non-root Docker kullanıcısı
- API anahtarı yönetimi
- Güvenli dosya işleme

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakınız.

## 👥 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'feat: Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun 
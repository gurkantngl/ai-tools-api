# AI Araçları API 🤖

Bu proje, yapay zeka tabanlı araçlar sunan bir REST API servisi ve kullanıcı dostu bir web arayüzüdür.

## 🌟 Özellikler

### 📝 Döküman İşlemleri
- PDF ve metin dosyası yükleme
- Vektör tabanlı benzerlik araması
- Akıllı metin bölümleme
- Çoklu dil desteği

### 🔢 Matematik İşlemleri
- Temel aritmetik işlemler
- Trigonometrik hesaplamalar
- Logaritmik işlemler
- Karekök hesaplamaları

### 🔑 Anahtar Kelime Çıkarma
- Google Gemini AI destekli analiz
- Özelleştirilebilir anahtar kelime sayısı
- Çoklu dil desteği
- Bağlam tabanlı analiz

## 🚀 Başlangıç

### Gereksinimler
- Python 3.11+
- Google Gemini API Anahtarı

### Kurulum

1. Projeyi klonlayın:
```bash
git clone [repo-url]
cd [proje-klasörü]
```

2. Sanal ortam oluşturun ve aktif edin:
```bash
python -m venv venv
# Windows için
venv\Scripts\activate
# Linux/Mac için
source venv/bin/activate
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. .env dosyasını oluşturun:
```bash
cp .env.example .env
# .env dosyasını düzenleyip Google API anahtarınızı ekleyin
```

### Çalıştırma

1. API'yi başlatın:
```bash
uvicorn app.main:app --reload
```

2. Web arayüzünü başlatın:
```bash
streamlit run app/streamlit_app.py
```

## 📚 API Kullanımı

### Döküman Yükleme
```python
POST /documents/upload
# Multipart form data ile dosya yükleme
```

### Vektör Arama
```python
POST /vector/search
{
    "query": "arama metni",
    "top_k": 5
}
```

### Matematik İşlemleri
```python
POST /math/solve
{
    "operation": "3 * 4 + sqrt(16)"
}
```

### Anahtar Kelime Çıkarma
```python
POST /keywords
{
    "text": "analiz edilecek metin",
    "num_keywords": 5
}
```

## 🛠️ Teknolojiler

### Backend
- FastAPI - Modern web framework
- LangChain - LLM entegrasyonu
- ChromaDB - Vektör veritabanı
- Google Gemini AI - Yapay zeka modeli

### Frontend
- Streamlit - Web arayüzü
- Streamlit Theming - Özelleştirilmiş temalar

## 🔒 Güvenlik
- API anahtarı doğrulama
- Güvenli dosya işleme
- Girdi doğrulama
- Hata yönetimi

## 🧪 Test

Testleri çalıştırmak için:
```bash
pytest tests/
```

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👥 İletişim

Proje ile ilgili sorularınız için:
- GitHub Issues
- E-posta: [e-posta-adresi] 
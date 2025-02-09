FROM python:3.11-slim as builder

# Güvenlik güncellemeleri ve gerekli paketler
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Sanal ortam oluştur
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final imaj
FROM python:3.11-slim

# Güvenlik için non-root kullanıcı
RUN useradd -m -r -u 1001 appuser

# Sanal ortamı kopyala
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Uygulama kodunu kopyala
COPY . .

# Dizin sahipliğini değiştir
RUN chown -R appuser:appuser /app

# Non-root kullanıcıya geç
USER appuser

# Portları aç
EXPOSE 8000
EXPOSE 8501

# Başlangıç komutu
CMD ["sh", "-c", "streamlit run app/streamlit_app.py & uvicorn app.main:app --host 0.0.0.0 --port 8000"] 
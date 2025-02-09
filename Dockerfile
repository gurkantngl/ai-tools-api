FROM python:3.11-slim

# Güvenlik için non-root kullanıcı oluştur
RUN useradd -m -r -u 1001 appuser

WORKDIR /app

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Uygulama dizininin sahipliğini appuser'a ver
RUN chown -R appuser:appuser /app

# Non-root kullanıcıya geç
USER appuser

EXPOSE 8000
EXPOSE 8501

CMD ["sh", "-c", "streamlit run app/streamlit_app.py & uvicorn app.main:app --host 0.0.0.0 --port 8000"] 
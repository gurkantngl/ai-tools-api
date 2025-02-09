import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

def test_upload_text_document():
    """Metin dosyası yükleme testi"""
    # Test dosyası oluştur
    with open("test.txt", "w", encoding="utf-8") as f:
        f.write("Bu bir test metnidir.")
    
    # Dosyayı yükle
    with open("test.txt", "rb") as f:
        response = client.post(
            "/documents/upload",
            files={"file": ("test.txt", f, "text/plain")}
        )
    
    # Dosyayı temizle
    os.remove("test.txt")
    
    assert response.status_code == 201
    assert "message" in response.json()

def test_upload_duplicate_document():
    """Aynı dosyayı tekrar yükleme testi"""
    # Test dosyası oluştur
    with open("test.txt", "w", encoding="utf-8") as f:
        f.write("Bu bir test metnidir.")
    
    # Dosyayı ilk kez yükle
    with open("test.txt", "rb") as f:
        client.post("/documents/upload", files={"file": ("test.txt", f, "text/plain")})
    
    # Aynı dosyayı tekrar yükle
    with open("test.txt", "rb") as f:
        response = client.post(
            "/documents/upload",
            files={"file": ("test.txt", f, "text/plain")}
        )
    
    # Dosyayı temizle
    os.remove("test.txt")
    
    assert response.status_code == 200
    assert "message" in response.json()

def test_vector_search():
    """Vektör arama testi"""
    # Önce test dökümanı yükle
    with open("test.txt", "w", encoding="utf-8") as f:
        f.write("Yapay zeka, bilgisayarların insan gibi düşünmesini sağlayan bir teknolojidir.")
    
    with open("test.txt", "rb") as f:
        client.post("/documents/upload", files={"file": ("test.txt", f, "text/plain")})
    
    # Arama yap
    response = client.post(
        "/vector/search",
        json={"query": "yapay zeka nedir", "top_k": 1}
    )
    
    # Dosyayı temizle
    os.remove("test.txt")
    
    assert response.status_code == 200
    assert "results" in response.json()
    assert len(response.json()["results"]) > 0

def test_solve_math_simple():
    """Basit matematik işlemi testi"""
    response = client.post(
        "/math/solve",
        json={"operation": "3 * 4 + 2"}
    )
    
    assert response.status_code == 200
    assert response.json()["result"] == 14

def test_solve_math_complex():
    """Karmaşık matematik işlemi testi"""
    response = client.post(
        "/math/solve",
        json={"operation": "sqrt(16) + sin(30) + log(100)"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json()["result"], float)

def test_solve_math_invalid():
    """Geçersiz matematik işlemi testi"""
    response = client.post(
        "/math/solve",
        json={"operation": "invalid"}
    )
    
    assert response.status_code == 500

def test_extract_keywords():
    """Anahtar kelime çıkarma testi"""
    response = client.post(
        "/keywords",
        json={
            "text": "Yapay zeka ve makine öğrenmesi, modern teknolojinin önemli alanlarıdır.",
            "num_keywords": 3
        }
    )
    
    assert response.status_code == 200
    assert "keywords" in response.json()
    assert "total_keywords" in response.json()
    assert len(response.json()["keywords"]) == 3

def test_extract_keywords_invalid_input():
    """Geçersiz anahtar kelime çıkarma testi"""
    response = client.post(
        "/keywords",
        json={
            "text": "Kısa",  # Çok kısa metin
            "num_keywords": 3
        }
    )
    
    assert response.status_code == 422

if __name__ == "__main__":
    pytest.main(["-v"]) 
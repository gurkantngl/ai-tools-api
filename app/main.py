from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, constr
from app.tools.math_operations import MathOperations
from typing import List, Dict, Any
import chromadb
from chromadb.db.base import UniqueConstraintError
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import pdfplumber
from io import BytesIO
import re

# .env dosyasını yükle
load_dotenv()

# Response modelleri
class MathResponse(BaseModel):
    result: float = Field(description="İşlemin sonucu")

class VectorSearchResponse(BaseModel):
    results: List[Dict[str, Any]] = Field(description="Arama sonuçları")

class KeywordResponse(BaseModel):
    keywords: List[str] = Field(description="Çıkarılan anahtar kelimeler")
    total_keywords: int = Field(description="Toplam anahtar kelime sayısı")

# Input modelleri
class MathOperation(BaseModel):
    operation: str = Field(
        description="Çözülecek matematik işlemi",
        examples=["3 * 4 + 2", "sqrt(16) + 5", "(15 + 3) * 2"]
    )

class SearchRequest(BaseModel):
    query: str = Field(description="Arama sorgusu")
    top_k: int = Field(default=5, description="Döndürülecek sonuç sayısı")

class KeywordRequest(BaseModel):
    text: constr(min_length=10) = Field(description="Anahtar kelime çıkarılacak metin")
    num_keywords: int = Field(default=5, ge=1, le=10, description="Çıkarılacak anahtar kelime sayısı")

def clean_text(text: str) -> str:
    """Metni temizler ve düzenler."""
    # Gereksiz boşlukları temizle
    text = re.sub(r'\s+', ' ', text)
    
    # Özel karakterleri temizle
    text = re.sub(r'[^\w\s\.,;!?-]', '', text)
    
    # Unicode escape karakterlerini temizle
    text = text.encode('utf-8', 'ignore').decode('utf-8')
    
    return text.strip()

# ChromaDB istemcisini başlat
chroma_client = chromadb.PersistentClient(path="chroma_db")

# Varolan koleksiyonu sil
try:
    chroma_client.delete_collection(name="documents")
except ValueError:
    pass

# Yeni koleksiyon oluştur
collection = chroma_client.create_collection(name="documents")

# LLM modelini başlat
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    convert_system_message_to_human=True
)

def extract_text_from_file(file: UploadFile) -> str:
    """Dosyadan metin çıkarır."""
    content = file.file.read()
    
    if file.filename.lower().endswith('.pdf'):
        # PDF dosyası
        with pdfplumber.open(BytesIO(content)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return clean_text(text)
    else:
        # Metin dosyası
        return clean_text(content.decode('utf-8'))

app = FastAPI(
    title="AI Tool API",
    description="Bu API, LangChain ve Google Gemini AI ile güçlendirilmiş yapay zeka tabanlı araçlar sunan bir REST servisidir.",
    version="1.0.0"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post(
    "/math/solve",
    response_model=MathResponse,
    tags=["Matematik İşlemleri"],
    summary="Matematik işlemini çözer"
)
async def solve_math(data: MathOperation):
    try:
        math_ops = MathOperations()
        result = await math_ops.solve_operation(data.operation)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/documents/upload",
    tags=["Döküman İşlemleri"],
    summary="Döküman yükler"
)
async def upload_document(file: UploadFile = File(...)):
    try:
        # Dosya içeriğini oku
        text_content = extract_text_from_file(file)
        
        # Dosya zaten var mı kontrol et
        existing_docs = collection.get(
            where={"source": file.filename}
        )
        
        if existing_docs and len(existing_docs['ids']) > 0:
            # Varolan döküman için 200 dön
            return JSONResponse(
                status_code=200,
                content={"message": f"{file.filename} zaten yüklü"}
            )
            
        # Metadata hazırla
        metadata = {
            "source": file.filename,
            "type": file.content_type or "text/plain",  # Eğer content_type None ise varsayılan değer kullan
            "size": len(text_content)
        }
            
        # Dökümanı koleksiyona ekle
        collection.add(
            documents=[text_content],
            metadatas=[metadata],
            ids=[f"doc_{len(collection.get()['ids']) + 1}"]
        )
        
        # Yeni döküman için 201 dön
        return JSONResponse(
            status_code=201,
            content={"message": f"{file.filename} başarıyla yüklendi"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/vector/search",
    response_model=VectorSearchResponse,
    tags=["Döküman İşlemleri"],
    summary="Vektör tabanlı benzerlik araması yapar"
)
async def vector_search(request: SearchRequest):
    try:
        # Arama yap
        results = collection.query(
            query_texts=[request.query],
            n_results=request.top_k
        )
        
        # Sonuçları formatla
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                # Benzerlik skorunu hesapla (ChromaDB L2 mesafesini benzerlik skoruna dönüştür)
                distance = float(results['distances'][0][i]) if 'distances' in results else 1.0
                similarity = 1.0 / (1.0 + distance)  # Mesafeyi 0-1 arası benzerlik skoruna dönüştür
                
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity": similarity
                })
        
        return {"results": formatted_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/keywords",
    response_model=KeywordResponse,
    tags=["Metin İşlemleri"],
    summary="Metinden anahtar kelimeler çıkarır"
)
async def extract_keywords(request: KeywordRequest):
    try:
        # LLM'e prompt gönder
        prompt = f"""
        Aşağıdaki metinden tam olarak {request.num_keywords} adet anahtar kelime çıkar.
        Eğer yeterli anahtar kelime bulamazsan, metindeki önemli kelimeleri veya kelime gruplarını kullan.
        Sadece anahtar kelimeleri virgülle ayırarak liste halinde döndür.
        Başka bir şey ekleme.
        Tam olarak {request.num_keywords} adet anahtar kelime döndürmelisin.

        Metin: {request.text}
        """
        
        response = llm.invoke(prompt)
        
        # Yanıtı işle
        keywords = [kw.strip() for kw in response.content.split(",")]
        
        # Eğer istenen sayıda anahtar kelime yoksa, son kelimeyi tekrarla
        while len(keywords) < request.num_keywords:
            keywords.append(keywords[-1])
        
        # Eğer fazla anahtar kelime varsa, ilk N tanesini al
        keywords = keywords[:request.num_keywords]
        
        return {
            "keywords": keywords,
            "total_keywords": len(keywords)
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
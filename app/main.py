from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, constr
from app.tools.math_operations import MathOperations
from typing import List, Dict, Any
import chromadb
from chromadb.db.base import UniqueConstraintError
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import CommaSeparatedListOutputParser
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

# Embedding modeli
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Vektör veritabanı
vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings,
    collection_name="documents"
)

# Text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

# LLM modelini başlat
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    convert_system_message_to_human=True
)

# Anahtar kelime çıkarma için prompt template ve chain
keyword_prompt = PromptTemplate(
    input_variables=["text", "num_keywords"],
    template="""Aşağıdaki metinden tam olarak {num_keywords} adet anahtar kelime çıkar.
    Eğer yeterli anahtar kelime bulamazsan, metindeki önemli kelimeleri veya kelime gruplarını kullan.
    Sadece anahtar kelimeleri virgülle ayırarak liste halinde döndür.
    Başka bir şey ekleme.
    Tam olarak {num_keywords} adet anahtar kelime döndürmelisin.

    Metin: {text}
    """
)

keyword_chain = LLMChain(
    llm=llm,
    prompt=keyword_prompt,
    output_parser=CommaSeparatedListOutputParser()
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
        
        # Metni parçalara ayır
        texts = text_splitter.split_text(text_content)
        
        # Metadata hazırla
        metadata = {
            "source": file.filename,
            "type": file.content_type or "text/plain",
            "size": len(text_content)
        }
        
        # Dökümanları oluştur
        documents = [
            Document(
                page_content=text,
                metadata={**metadata, "chunk": i}
            ) for i, text in enumerate(texts)
        ]
        
        # Vektör veritabanına ekle
        vectorstore.add_documents(documents)
        
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
        # Benzerlik araması yap
        results = vectorstore.similarity_search_with_relevance_scores(
            request.query,
            k=request.top_k
        )
        
        # Sonuçları formatla
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "id": doc.metadata.get("chunk", ""),
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity": score
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
        # LangChain ile anahtar kelimeleri çıkar
        keywords = await keyword_chain.ainvoke({
            "text": request.text,
            "num_keywords": request.num_keywords
        })
        
        # Sonucu formatla
        keywords = keywords["text"][:request.num_keywords]
        
        return {
            "keywords": keywords,
            "total_keywords": len(keywords)
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
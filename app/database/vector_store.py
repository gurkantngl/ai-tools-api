from chromadb import Client
from chromadb.config import Settings

class VectorStore:
    def __init__(self):
        self.client = Client(Settings(persist_directory="./chroma_db"))
        self.collection = self.client.create_collection("documents")
    
    def add_document(self, text, metadata=None):
        # Döküman ekleme fonksiyonu
        pass

    def search_similar(self, query, n_results=5):
        # Benzerlik arama fonksiyonu
        pass 
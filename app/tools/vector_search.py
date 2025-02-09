class VectorSearchTool:
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    def search(self, query):
        return self.vector_store.search_similar(query) 
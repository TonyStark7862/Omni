from typing import List, Dict
from sentence_transformers import SentenceTransformer
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from config import CHUNK_SIZE

class DocumentManager:
    def __init__(self):
        self.documents = {}
        self.database = None
        self.embeddings = SentenceTransformer('all-MiniLM-L6-v2')
        
    def add_document(self, name: str, content: str):
        self.documents[name] = content

    def remove_document(self, name: str):
        if name in self.documents:
            del self.documents[name]

    def list_documents(self) -> List[str]:
        return list(self.documents.keys())

    def create_embeddings_and_database(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = 0, separator: str = " "):
        text_splitter = CharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator=separator
        )
        
        all_docs = []
        for doc_content in self.documents.values():
            docs = text_splitter.split_documents(doc_content)
            all_docs.extend(docs)

        # Convert documents to embeddings using SentenceTransformer
        texts = [doc.page_content for doc in all_docs]
        embeddings = self.embeddings.encode(texts)
        
        # Create FAISS index
        self.database = FAISS.from_texts(texts, embeddings)

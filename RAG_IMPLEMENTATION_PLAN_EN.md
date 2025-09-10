# 🔍 RAG Implementation Plan for AI Agent

## 📊 Current Status
- ❌ **NO RAG implemented**
- ✅ **Structure prepared** for RAG (`search_documents` tool exists)
- ✅ **Modular system** allows easy RAG addition

## 🎯 Suggested Implementation

### **OPTION 1: Simple RAG with ChromaDB** (Recommended to start)

#### 1. Required dependencies:
```bash
pip install chromadb sentence-transformers pypdf2 langchain-text-splitters
```

#### 2. Proposed RAG structure:
```
agents_core/
├── rag/
│   ├── __init__.py
│   ├── vector_store.py      # ChromaDB setup
│   ├── document_loader.py   # Load PDFs, txt, etc
│   ├── embeddings.py        # Sentence transformers
│   └── retriever.py         # Search logic
```

#### 3. Files to create:

**agents_core/rag/vector_store.py:**
```python
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./rag_data/chromadb")
        self.collection = self.client.get_or_create_collection("documents")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def add_documents(self, texts, metadatas, ids):
        embeddings = self.embedding_model.encode(texts).tolist()
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query, n_results=5):
        query_embedding = self.embedding_model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        return results
```

**agents_core/rag/document_loader.py:**
```python
from pathlib import Path
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentLoader:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def load_pdf(self, file_path):
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    def load_txt(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def chunk_text(self, text):
        return self.text_splitter.split_text(text)
```

#### 4. Modify search_documents to use RAG:

**agents_core/tools/advanced_tools.py** (replace mock function):
```python
async def search_documents(input_data: DocumentSearchInput) -> DocumentSearchOutput:
    """Search through company documents and knowledge base using RAG."""
    try:
        from agents_core.rag.vector_store import VectorStore
        
        vector_store = VectorStore()
        search_results = vector_store.search(
            query=input_data.query,
            n_results=input_data.limit
        )
        
        results = []
        for i, (doc, metadata, score) in enumerate(zip(
            search_results['documents'][0],
            search_results['metadatas'][0], 
            search_results['distances'][0]
        )):
            results.append({
                "title": metadata.get('title', f"Document {i+1}"),
                "summary": doc[:200] + "..." if len(doc) > 200 else doc,
                "content": doc,
                "url": metadata.get('url', f"/documents/{metadata.get('source', 'unknown')}"),
                "relevance_score": 1 - score,  # Convert distance to similarity
                "last_updated": metadata.get('last_updated', 'Unknown'),
                "source": metadata.get('source', 'Unknown')
            })
        
        return DocumentSearchOutput(
            results=results,
            total_found=len(results),
            query_time_ms=100  # Placeholder
        )
        
    except ImportError:
        # Fallback to mock if RAG not installed
        return await search_documents_mock(input_data)
    except Exception as e:
        print(f"RAG search error: {e}")
        return await search_documents_mock(input_data)
```

### **OPTION 2: Advanced RAG with Langchain + Pinecone**

#### Dependencies:
```bash
pip install langchain pinecone-client openai langchain-openai
```

#### Features:
- ✅ Cloud vector store (Pinecone)
- ✅ OpenAI embeddings
- ✅ Better performance for large volumes
- ✅ Hybrid search (semantic + keyword)

### **OPTION 3: RAG with Weaviate** (For production)

#### Features:
- ✅ GraphQL API
- ✅ Native hybrid search
- ✅ Complex filters
- ✅ Enterprise scalability

## 🛠️ Step-by-Step Implementation

### **Step 1: Basic setup with ChromaDB**
```bash
# Install dependencies
pip install chromadb sentence-transformers pypdf2

# Create folder structure
mkdir -p agents_core/rag
mkdir -p rag_data/documents
```

### **Step 2: Load initial documents**
```python
# Script to load documents
from agents_core.rag.vector_store import VectorStore
from agents_core.rag.document_loader import DocumentLoader

def setup_rag():
    loader = DocumentLoader()
    vector_store = VectorStore()
    
    # Load example documents
    documents_path = Path("rag_data/documents")
    for file_path in documents_path.glob("*.pdf"):
        text = loader.load_pdf(file_path)
        chunks = loader.chunk_text(text)
        
        ids = [f"{file_path.stem}_{i}" for i in range(len(chunks))]
        metadatas = [{
            "source": file_path.name,
            "title": file_path.stem,
            "chunk_index": i
        } for i in range(len(chunks))]
        
        vector_store.add_documents(chunks, metadatas, ids)
```

### **Step 3: Endpoint to upload documents**
```python
# In apps/api/main.py
@app.post("/rag/upload")
async def upload_document(file: UploadFile):
    # Save file
    # Process with RAG
    # Return status
```

## 📊 RAG Benefits

### **✅ With RAG you would have:**
1. **🧠 Specific knowledge**: The agent knows your documents
2. **📚 Knowledge base**: FAQs, manuals, policies
3. **🔍 Semantic search**: Finds info by context, not just keywords
4. **📈 Improved responses**: Cites real sources
5. **🔄 Updatable**: Add documents dynamically

### **🎯 Use cases:**
- 📋 Employee handbook
- ❓ Product FAQs
- 📖 Technical documentation
- 🏢 Company policies
- 📊 Reports and analysis

## 🚀 Recommendation

**To start:** Implement ChromaDB (Option 1)
- ✅ Easy setup
- ✅ No external services required
- ✅ Perfect for prototypes
- ✅ Easy migration to advanced options

**For production:** Consider Pinecone or Weaviate
- 🚀 Better performance
- 📈 Scalability
- 🛡️ Automatic backups
- 🔧 Advanced features

Would you like me to implement Option 1 (ChromaDB) now?


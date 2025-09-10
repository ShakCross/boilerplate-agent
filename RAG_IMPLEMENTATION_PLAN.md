# 🔍 Plan de Implementación RAG para AI Agent

## 📊 Estado Actual
- ❌ **NO tiene RAG implementado**
- ✅ **Estructura preparada** para RAG (tool `search_documents` existe)
- ✅ **Sistema modular** permite agregar RAG fácilmente

## 🎯 Implementación Sugerida

### **OPCIÓN 1: RAG Simple con ChromaDB** (Recomendado para empezar)

#### 1. Dependencias necesarias:
```bash
pip install chromadb sentence-transformers pypdf2 langchain-text-splitters
```

#### 2. Estructura RAG propuesta:
```
agents_core/
├── rag/
│   ├── __init__.py
│   ├── vector_store.py      # ChromaDB setup
│   ├── document_loader.py   # Cargar PDFs, txt, etc
│   ├── embeddings.py        # Sentence transformers
│   └── retriever.py         # Lógica de búsqueda
```

#### 3. Archivos a crear:

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

#### 4. Modificar search_documents para usar RAG:

**agents_core/tools/advanced_tools.py** (reemplazar función mock):
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

### **OPCIÓN 2: RAG Avanzado con Langchain + Pinecone**

#### Dependencias:
```bash
pip install langchain pinecone-client openai langchain-openai
```

#### Características:
- ✅ Vector store en la nube (Pinecone)
- ✅ Embeddings de OpenAI
- ✅ Mejor performance para grandes volúmenes
- ✅ Búsqueda híbrida (semántica + keyword)

### **OPCIÓN 3: RAG con Weaviate** (Para producción)

#### Características:
- ✅ GraphQL API
- ✅ Búsqueda híbrida nativa
- ✅ Filtros complejos
- ✅ Escalabilidad enterprise

## 🛠️ Implementación Paso a Paso

### **Paso 1: Setup básico con ChromaDB**
```bash
# Instalar dependencias
pip install chromadb sentence-transformers pypdf2

# Crear estructura de carpetas
mkdir -p agents_core/rag
mkdir -p rag_data/documents
```

### **Paso 2: Cargar documentos iniciales**
```python
# Script para cargar documentos
from agents_core.rag.vector_store import VectorStore
from agents_core.rag.document_loader import DocumentLoader

def setup_rag():
    loader = DocumentLoader()
    vector_store = VectorStore()
    
    # Cargar documentos de ejemplo
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

### **Paso 3: Endpoint para cargar documentos**
```python
# En apps/api/main.py
@app.post("/rag/upload")
async def upload_document(file: UploadFile):
    # Guardar archivo
    # Procesar con RAG
    # Retornar status
```

## 📊 Beneficios del RAG

### **✅ Con RAG tendrías:**
1. **🧠 Conocimiento específico**: El agente conoce tus documentos
2. **📚 Base de conocimiento**: FAQs, manuales, políticas
3. **🔍 Búsqueda semántica**: Encuentra info por contexto, no solo keywords
4. **📈 Respuestas mejoradas**: Citas fuentes reales
5. **🔄 Actualizable**: Agregar documentos dinámicamente

### **🎯 Casos de uso:**
- 📋 Manual de empleados
- ❓ FAQs de productos
- 📖 Documentación técnica
- 🏢 Políticas de empresa
- 📊 Reportes y análisis

## 🚀 Recomendación

**Para empezar:** Implementa ChromaDB (Opción 1)
- ✅ Fácil setup
- ✅ No requiere servicios externos
- ✅ Perfecto para prototipos
- ✅ Migración fácil a opciones avanzadas

**Para producción:** Considera Pinecone o Weaviate
- 🚀 Mejor performance
- 📈 Escalabilidad
- 🛡️ Respaldos automáticos
- 🔧 Funciones avanzadas

¿Te interesa que implemente la Opción 1 (ChromaDB) ahora?

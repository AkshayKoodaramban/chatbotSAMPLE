import os, json, datetime
from src.core.config import Config
from typing import List, Dict, Any, Optional
from src.llm.embedding_service import GeminiEmbeddingService
from src.core.document_processor import PDFDocumentProcessor
from src.vectordb.vector_database import ChromaDBVectorDatabase
from src.model.models import Document, TextChunk, VectorEmbedding

class DocumentController:
    """Controller for document operations"""
    def __init__(self):
        self.document_processor = PDFDocumentProcessor()
        self.embedding_service = GeminiEmbeddingService()
        self.vector_database = ChromaDBVectorDatabase()
        self.documents = {}
        self.metadata_file = os.path.join(Config.VECTORDB_PATH, "document_metadata.json")
        os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
        self.load_document_metadata()

    def load_document_metadata(self) -> None:
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    doc_data = json.load(f)
                    for doc_id, doc_info in doc_data.items():
                        document = Document(
                            filename=doc_info['filename'],
                            content=None,
                            metadata=doc_info['metadata']
                        )
                        document.id = doc_id
                        document.created_at = doc_info['created_at']
                        self.documents[doc_id] = document
            except Exception as e:
                print(f"Error loading document metadata: {e}")

    def save_document_metadata(self) -> None:
        try:
            doc_data = {}
            for doc_id, doc in self.documents.items():
                doc_data[doc_id] = {
                    'filename': doc.filename,
                    'metadata': doc.metadata,
                    'created_at': doc.created_at
                }
            with open(self.metadata_file, 'w') as f:
                json.dump(doc_data, f, indent=2)
        except Exception as e:
            print(f"Error saving document metadata: {e}")

    def upload_document(self, file_path: str, filename: str, original_filename: Optional[str] = None) -> bool:
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
            doc_metadata = {
                "source": file_path,
                "created_at": datetime.datetime.now().isoformat(),
                "original_filename": original_filename or filename
            }
            document = Document(
                filename=filename,
                content=content,
                metadata=doc_metadata
            )
            self.documents[document.get_id()] = document
            self.save_document_metadata()
            self.process_document(document)
            return True
        except Exception as e:
            print(f"Error uploading document: {e}")
            return False

    def process_document(self, document: Document) -> List[TextChunk]:
        text = self.document_processor.extract_text(document)
        chunks = self.document_processor.chunk_text(text, document.get_id())
        self.generate_and_store_embeddings(chunks)
        return chunks

    def generate_and_store_embeddings(self, chunks: List[TextChunk]) -> None:
        embeddings = self.embedding_service.generate_chunk_embeddings(chunks)
        for i, embedding in enumerate(embeddings):
            self.vector_database.store(embedding, chunks[i])

    def get_documents(self) -> List[Dict[str, Any]]:
        def strip_id_prefix(filename):
            parts = filename.split('_', 1)
            if len(parts) == 2 and len(parts[0]) == 36:
                return parts[1]
            return filename
        docs = []
        for doc in self.documents.values():
            doc_dict = doc.to_dict()
            original_filename = doc.metadata.get("original_filename")
            display_filename = original_filename or strip_id_prefix(doc.filename)
            doc_dict["display_filename"] = display_filename
            docs.append(doc_dict)
        return docs

    def delete_document_by_id(self, document_id: str) -> bool:
        if document_id not in self.documents:
            print(f"Document with ID {document_id} not found in metadata.")
            return False
        try:
            doc = self.documents[document_id]
            filename = doc.filename
            file_to_delete = os.path.join(Config.UPLOAD_FOLDER, filename)
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete)
            try:
                self.vector_database.delete_document_data(document_id)
            except Exception as e_vec:
                print(f"Error deleting document {document_id} from vector database: {e_vec}")
            del self.documents[document_id]
            self.save_document_metadata()
            return True
        except Exception as e:
            print(f"Error during deletion process for document {document_id}: {e}")
            return False

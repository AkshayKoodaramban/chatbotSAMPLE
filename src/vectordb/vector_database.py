import os, chromadb
from src.core.config import Config
from chromadb.config import Settings
from chromadb.errors import NotFoundError
from typing import List, Dict, Any, Optional
from src.model.models import VectorEmbedding, TextChunk

class VectorDatabase:
    """Interface for vector database operations"""
    def store(self, embedding: VectorEmbedding, text_chunk: TextChunk) -> None:
        raise NotImplementedError("Subclass must implement abstract method")

    def find_similar(self, embedding: VectorEmbedding, limit: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError("Subclass must implement abstract method")

    def get_chunk(self, chunk_id: str) -> Optional[TextChunk]:
        raise NotImplementedError("Subclass must implement abstract method")

    def clear(self) -> None:
        raise NotImplementedError("Subclass must implement abstract method")

    def delete_document_data(self, document_id: str) -> None:
        raise NotImplementedError("Subclass must implement abstract method")

class ChromaDBVectorDatabase(VectorDatabase):
    """ChromaDB implementation of the vector database"""
    def __init__(self):
        os.makedirs(Config.VECTORDB_PATH, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=Config.VECTORDB_PATH,
            settings=Settings(allow_reset=True)
        )
        collection_name = "documents"
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"Connected to collection '{collection_name}'")
        except NotFoundError:
            self.collection = self.client.create_collection(name=collection_name)
            print(f"Collection '{collection_name}' created")

    def store(self, embedding: VectorEmbedding, text_chunk: TextChunk) -> None:
        self.collection.add(
            ids=[embedding.get_id()],
            embeddings=[embedding.get_vector()],
            metadatas=[{
                "chunk_id": text_chunk.get_id(),
                "document_id": text_chunk.get_document_id(),
                "position": int(text_chunk.position)
            }],
            documents=[text_chunk.get_text()]
        )

    def find_similar(self, embedding: VectorEmbedding, limit: int = 5) -> List[Dict[str, Any]]:
        print(f"Searching for similar embeddings with limit: {limit}")
        try:
            collection_count = self.collection.count()
            print(f"Collection contains {collection_count} documents")
            if collection_count == 0:
                print("WARNING: Vector database is empty!")
                return []
        except Exception as e:
            print(f"Error checking collection count: {e}")
        results = self.collection.query(
            query_embeddings=[embedding.get_vector()],
            n_results=limit
        )
        print(f"Raw ChromaDB results: {results}")
        formatted_results = []
        if results and "documents" in results and len(results["documents"]) > 0:
            for i, document in enumerate(results["documents"][0]):
                if document and i < len(results["metadatas"][0]):
                    metadata = results["metadatas"][0][i]
                    document_id = str(metadata.get("document_id", ""))
                    position = int(metadata.get("position", 0))
                    chunk = TextChunk(
                        text=document,
                        document_id=document_id,
                        position=position
                    )
                    score = 0.0
                    if "distances" in results and len(results["distances"]) > 0 and i < len(results["distances"][0]):
                        distance = results["distances"][0][i]
                        score = 1.0 - distance
                        print(f"Document {i}: distance={distance}, similarity_score={score}")
                    formatted_results.append({
                        "chunk": chunk,
                        "score": score
                    })
        print(f"Formatted results count: {len(formatted_results)}")
        return formatted_results

    def get_chunk(self, chunk_id: str) -> Optional[TextChunk]:
        try:
            results = self.collection.get(
                ids=[chunk_id],
                include=["documents", "metadatas"]
            )
            if results and "documents" in results and len(results["documents"]) > 0:
                document = results["documents"][0]
                metadata = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else {}
                if document:
                    document_id = str(metadata.get("document_id", ""))
                    position = int(metadata.get("position", 0))
                    return TextChunk(
                        text=document,
                        document_id=document_id,
                        position=position
                    )
            return None
        except Exception as e:
            print(f"Error fetching chunk {chunk_id}: {e}")
            return None

    def clear(self) -> None:
        try:
            self.client.delete_collection(self.collection.name)
            self.collection = self.client.create_collection(name=self.collection.name)
        except Exception as e:
            print(f"Error clearing collection: {e}")

    def delete_document_data(self, document_id: str) -> None:
        try:
            self.collection.delete(where={"document_id": document_id})
            print(f"Deleted data for document_id: {document_id} from ChromaDB.")
        except Exception as e:
            print(f"Error deleting data for document_id {document_id} from ChromaDB: {e}")

import uuid
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional


class Document:
    """Document representing uploaded files"""
    def __init__(self, filename: str, content: bytes, metadata: Optional[Dict[str, str]] = None):
        self.id = str(uuid.uuid4())
        self.filename = filename
        self.content = content
        self.metadata = metadata or {}
        self.created_at = self.metadata.get('created_at', datetime.now().isoformat())

    def get_id(self) -> str:
        return self.id

    def get_content(self) -> bytes:
        return self.content

    def get_metadata(self) -> Dict[str, str]:
        return self.metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'filename': self.filename,
            'created_at': self.created_at,
            'metadata': self.metadata
        }

class TextChunk:
    """Portion of a document"""
    def __init__(self, text: str, document_id: str, position: int):
        self.id = str(uuid.uuid4())
        self.text = text
        self.document_id = document_id
        self.position = position

    def get_id(self) -> str:
        return self.id

    def get_text(self) -> str:
        return self.text

    def get_document_id(self) -> str:
        return self.document_id

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'text': self.text,
            'document_id': self.document_id,
            'position': self.position
        }

class VectorEmbedding:
    """Vector representation of a text chunk"""
    def __init__(self, chunk_id: str, vector: List[float]):
        self.id = str(uuid.uuid4())
        self.chunk_id = chunk_id
        self.vector = vector

    def get_id(self) -> str:
        return self.id

    def get_chunk_id(self) -> str:
        return self.chunk_id

    def get_vector(self) -> List[float]:
        return self.vector

    def similarity(self, other: 'VectorEmbedding') -> float:
        vec1 = np.array(self.vector)
        vec2 = np.array(other.vector)
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        if norm_a == 0 or norm_b == 0:
            return 0
        return dot_product / (norm_a * norm_b)

class Query:
    """User's question"""
    def __init__(self, text: str, embedding: Optional[VectorEmbedding] = None):
        self.id = str(uuid.uuid4())
        self.text = text
        self.embedding = embedding
        self.timestamp = datetime.now()

    def get_id(self) -> str:
        return self.id

    def get_text(self) -> str:
        return self.text

    def get_embedding(self) -> Optional[VectorEmbedding]:
        return self.embedding

    def set_embedding(self, embedding: VectorEmbedding) -> None:
        self.embedding = embedding

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'text': self.text,
            'timestamp': self.timestamp.isoformat()
        }

class Response:
    """System's answer to a query"""
    def __init__(self, query_id: str, content: str, relevant_chunks: List[TextChunk] = None, confidence: float = 0.0):
        self.id = str(uuid.uuid4())
        self.query_id = query_id
        self.content = content
        self.relevant_chunks = relevant_chunks or []
        self.confidence = confidence
        self.timestamp = datetime.now()

    def get_id(self) -> str:
        return self.id

    def get_content(self) -> str:
        return self.content

    def get_relevant_chunks(self) -> List[TextChunk]:
        return self.relevant_chunks

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'query_id': self.query_id,
            'content': self.content,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'sources': [chunk.to_dict() for chunk in self.relevant_chunks]
        }

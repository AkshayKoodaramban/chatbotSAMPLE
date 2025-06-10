from typing import List
from src.core.config import Config
import google.generativeai as genai
from src.model.models import VectorEmbedding, TextChunk

class EmbeddingService:
    def generate_embedding(self, text: str) -> VectorEmbedding:
        raise NotImplementedError("Subclass must implement abstract method")

    def generate_chunk_embeddings(self, text_chunks: List[TextChunk]) -> List[VectorEmbedding]:
        raise NotImplementedError("Subclass must implement abstract method")

class GeminiEmbeddingService(EmbeddingService):
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = Config.EMBEDDING_MODEL

    def generate_embedding(self, text: str) -> VectorEmbedding:
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_query"
            )
            return VectorEmbedding(chunk_id="query", vector=result["embedding"])
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return VectorEmbedding(chunk_id="query", vector=[0.0] * 768)

    def generate_chunk_embeddings(self, text_chunks: List[TextChunk]) -> List[VectorEmbedding]:
        embeddings = []
        for chunk in text_chunks:
            try:
                result = genai.embed_content(
                    model=self.model,
                    content=chunk.get_text(),
                    task_type="retrieval_document"
                )
                embedding = VectorEmbedding(
                    chunk_id=chunk.get_id(),
                    vector=result["embedding"]
                )
                embeddings.append(embedding)
            except Exception as e:
                print(f"Error generating embedding for chunk {chunk.get_id()}: {e}")
                embedding = VectorEmbedding(
                    chunk_id=chunk.get_id(),
                    vector=[0.0] * 768
                )
                embeddings.append(embedding)
        return embeddings

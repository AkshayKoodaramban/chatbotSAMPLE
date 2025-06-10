from src.core.config import Config
from typing import List, Dict, Any
from src.model.models import Query, TextChunk, Response
from src.llm.embedding_service import GeminiEmbeddingService
from src.vectordb.vector_database import ChromaDBVectorDatabase

class QueryController:
    """Controller for query operations"""
    def __init__(self, response_controller):
        self.embedding_service = GeminiEmbeddingService()
        self.vector_database = ChromaDBVectorDatabase()
        self.response_controller = response_controller

    def process_query(self, query_text: str, query_id: str = None) -> Dict[str, Any]:
        query = Query(query_text)
        query_embedding = self.embedding_service.generate_embedding(query_text)
        query.set_embedding(query_embedding)
        relevant_chunks = self.find_relevant_chunks(query_embedding)
        if relevant_chunks:
            response = self.response_controller.generate_response(query, relevant_chunks)
        else:
            response = self.response_controller.generate_no_info_response(query)
        return response.to_dict()

    def find_relevant_chunks(self, query_embedding) -> List[TextChunk]:
        results = self.vector_database.find_similar(
            query_embedding,
            limit=Config.MAX_RELEVANT_CHUNKS
        )
        chunks = []
        for result in results:
            similarity_score = result["score"]
            if similarity_score > 0.1:
                chunks.append(result["chunk"])
        return chunks

from typing import List
from src.llm.llm_service import GeminiLLMService
from src.model.models import Query, TextChunk, Response

class ResponseController:
    """Controller for response operations"""
    def __init__(self):
        self.llm_service = GeminiLLMService()

    def generate_response(self, query: Query, relevant_chunks: List[TextChunk]) -> Response:
        return self.llm_service.generate_response(query, relevant_chunks)

    def generate_no_info_response(self, query: Query) -> Response:
        return self.llm_service.generate_no_info_response(query)

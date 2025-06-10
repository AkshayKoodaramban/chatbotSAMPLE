from typing import List
from src.core.config import Config
import google.generativeai as genai
from src.model.models import Query, TextChunk, Response

class LLMService:
    def generate_response(self, query: Query, relevant_chunks: List[TextChunk]) -> Response:
        raise NotImplementedError("Subclass must implement abstract method")

    def generate_no_info_response(self, query: Query) -> Response:
        raise NotImplementedError("Subclass must implement abstract method")

class GeminiLLMService(LLMService):
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)

    def generate_response(self, query: Query, relevant_chunks: List[TextChunk]) -> Response:
        print(f"Generating response for query: {query.get_text()}")
        print(f"Using {len(relevant_chunks)} relevant chunks")
        context = "\n\n".join([chunk.get_text() for chunk in relevant_chunks])
        print(f"Context length: {len(context)} characters")
        if len(context.strip()) == 0:
            print("WARNING: Context is empty!")
        else:
            print(f"Context preview: {context[:200]}...")
        prompt = f"""
        You are an Enterprise Q&A system. Your task is to provide accurate answers to questions based on the context provided.

        ## Context:
        {context}

        ## Question:
        {query.get_text()}

        ## Instructions:
        1. Answer the question based only on the context provided.
        2. If the context doesn't contain the information needed to answer the question, say "I don't have enough information to answer that question."
        3. Be concise and to the point.
        4. Use bullet points or numbered lists when appropriate.
        5. Format your answer using markdown when helpful.
        6. Include "Sources:" section at the end if you found relevant information.

        ## Answer:
        """
        try:
            generation_config = {
                "max_output_tokens": Config.MAX_OUTPUT_TOKENS,
                "temperature": 0.2,
                "top_p": 0.95,
                "top_k": 40
            }
            print("Sending request to Gemini...")
            gemini_response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            print(f"Gemini response received: {gemini_response.text[:100]}...")
            confidence = 0.8
            return Response(
                query_id=query.get_id(),
                content=gemini_response.text,
                relevant_chunks=relevant_chunks,
                confidence=confidence
            )
        except Exception as e:
            print(f"Error generating response with Gemini: {e}")
            return Response(
                query_id=query.get_id(),
                content="I'm sorry, I encountered an error while generating a response.",
                relevant_chunks=[],
                confidence=0.0
            )

    def generate_no_info_response(self, query: Query) -> Response:
        content = (
            "I don't have enough information in my knowledge base to answer your question. "
            "Please consider asking a different question or providing more context."
        )
        return Response(
            query_id=query.get_id(),
            content=content,
            relevant_chunks=[],
            confidence=0.0
        )

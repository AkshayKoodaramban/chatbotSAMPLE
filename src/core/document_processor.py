import PyPDF2
from io import BytesIO
from typing import List
from src.core.config import Config
from src.model.models import Document, TextChunk

class DocumentProcessor:
    """Interface for document processing"""
    def extract_text(self, document: Document) -> str:
        """Extract text from a document"""
        raise NotImplementedError("Subclass must implement abstract method")

    def chunk_text(self, text: str, document_id: str) -> List[TextChunk]:
        """Split text into chunks"""
        raise NotImplementedError("Subclass must implement abstract method")

class PDFDocumentProcessor(DocumentProcessor):
    """PDF document processor implementation"""
    def extract_text(self, document: Document) -> str:
        """Extract text from a PDF document"""
        content = document.get_content()
        text = ""
        try:
            # Create a PDF file reader
            pdf_reader = PyPDF2.PdfReader(BytesIO(content))

            # Extract text from each page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"

            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def chunk_text(self, text: str, document_id: str) -> List[TextChunk]:
        """Split text into chunks with overlap"""
        chunk_size = Config.CHUNK_SIZE
        chunk_overlap = Config.CHUNK_OVERLAP

        if not text:
            return []

        chunks = []
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunk_text = text[i:i + chunk_size]
            if chunk_text:  # Only add non-empty chunks
                position = len(chunks)
                chunks.append(TextChunk(chunk_text, document_id, position))

        return chunks

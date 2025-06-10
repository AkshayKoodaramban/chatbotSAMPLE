import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the application"""
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', '')

    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/assets/uploads')
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB

    VECTORDB_PATH = os.getenv('VECTORDB_PATH', os.path.join(os.getcwd(), 'src', 'vectordb'))
    CHROMA_PERSIST_DIRECTORY = os.getenv('CHROMA_PERSIST_DIRECTORY', '/src/vectordb/')

    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))

    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-preview-05-20')
    MAX_OUTPUT_TOKENS = int(os.getenv('MAX_OUTPUT_TOKENS', 1024))
    TOP_K = int(os.getenv('TOP_K', 5))

    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'models/embedding-001')

    MAX_RELEVANT_CHUNKS = int(os.getenv('MAX_RELEVANT_CHUNKS', 5))

    ADMIN_SERIAL_KEY = os.getenv('ADMIN_SERIAL_KEY', 'YOUR-SERIAL-KEY-HERE')
    JWT_SECRET = os.getenv('JWT_SECRET', '')

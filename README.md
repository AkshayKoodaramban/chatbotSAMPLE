# Enterprise Q&A Chatbot with RAG (Retrieval-Augmented Generation)

A sophisticated enterprise-grade chatbot system that combines document retrieval with generative AI to provide accurate, context-aware responses. Built with FastAPI, Flask, and Google's Gemini AI model.

## 🚀 Features

### Core Functionality
- **Document Upload & Processing**: Support for PDF document ingestion and processing
- **Vector Database**: ChromaDB integration for efficient document embedding storage
- **RAG Implementation**: Retrieval-Augmented Generation for context-aware responses
- **AI-Powered Responses**: Integration with Google Gemini 1.5 Flash model
- **Dual API Architecture**: Both REST API (FastAPI) and Web Interface (Flask)

### Security & Authentication
- **JWT-based Authentication**: Secure token-based admin authentication
- **Admin User Management**: Secure admin account creation and management
- **Serial Key Validation**: Additional security layer for admin registration
- **CORS Support**: Cross-origin resource sharing for web applications

### User Interface
- **Web Chat Interface**: User-friendly chat interface for queries
- **Admin Dashboard**: Document management and system administration
- **Real-time Interaction**: Interactive chat experience with instant responses

### Document Management
- **PDF Processing**: Automated PDF document parsing and chunking
- **Vector Storage**: Efficient document embedding and retrieval
- **Document CRUD**: Complete document lifecycle management
- **Metadata Handling**: Rich document metadata support
- **Debug Mode**: Enhanced logging for troubleshooting retrieval issues

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- SQLite (included with Python)
- Internet connection for AI model access

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd RAG
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Copy the example environment file and configure it:
```bash
cp .env.example .env
```

Edit `.env` with your specific configurations:
```bash
# Vector database settings
CHROMA_PERSIST_DIRECTORY=./chroma_db
TOP_K=5

# LLM settings
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=models/gemini-1.5-flash

# Database settings
DATABASE_URL=sqlite:///src/userdb/users.db

# Admin settings
ADMIN_SERIAL_KEY=your-unique-software-serial-key-here
JWT_SECRET=your-secure-jwt-secret-key-here
```

### 5. Initialize Database
The database will be automatically initialized when you first run the application.

## 🚀 Quick Start

### Running the Application
```bash
python app.py
```

This starts both servers:
- **Flask Web Interface**: http://localhost:5000
- **FastAPI REST API**: http://localhost:8000

### First Time Setup
1. Visit http://localhost:5000/admin
2. Create an admin account using your serial key
3. Upload PDF documents through the admin interface
4. Start chatting at http://localhost:5000

## 📖 Configuration Guide

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB storage path | `./chroma_db` | No |
| `TOP_K` | Number of relevant chunks to retrieve | `5` | No |
| `GEMINI_API_KEY` | Google Gemini API key | - | **Yes** |
| `GEMINI_MODEL` | Gemini model to use | `models/gemini-1.5-flash` | No |
| `DATABASE_URL` | SQLite database path | `sqlite:///src/userdb/users.db` | No |
| `ADMIN_SERIAL_KEY` | Admin registration serial key | - | **Yes** |
| `JWT_SECRET` | JWT token secret key | - | **Yes** |

### Getting Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

## 🔗 API Documentation

### User Endpoints

#### Query Processing
```http
POST /api/query
Content-Type: application/json

{
  "text": "Your question here"
}
```

**Response:**
```json
{
  "query_id": "uuid",
  "query_text": "Your question here",
  "response_id": "uuid",
  "response_content": "AI-generated response",
  "has_relevant_info": true,
  "chunks_count": 3
}
```

### Admin Endpoints

#### Authentication
```http
POST /api/admin/register
Content-Type: application/json

{
  "username": "admin",
  "password": "secure_password",
  "email": "admin@company.com",
  "serial_key": "your_serial_key"
}
```

```http
POST /api/admin/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=secure_password
```

#### Document Management
```http
POST /api/admin/documents/upload
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

file: <pdf_file>
```

```http
GET /api/admin/documents
Authorization: Bearer <jwt_token>
```

```http
DELETE /api/admin/documents/{document_id}
Authorization: Bearer <jwt_token>
```

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask Web     │    │   FastAPI       │    │   ChromaDB      │
│   Interface     │────│   REST API      │────│   Vector Store  │
│   (Port 5000)   │    │   (Port 8000)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Templates     │    │   Controllers   │    │   Documents     │
│   & Static      │    │   & Models      │    │   & Embeddings  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Components

- **Document Controller**: Handles PDF processing and vector storage
- **Query Controller**: Manages query processing and RAG implementation
- **User Service**: Handles authentication and user management
- **Vector Database**: ChromaDB for document embeddings
- **AI Integration**: Google Gemini for response generation

### Data Flow

1. **Document Upload**: PDF → Text Extraction → Chunking → Embedding → Vector Storage
2. **Query Processing**: User Query → Vector Search → Context Retrieval → AI Generation → Response
3. **Authentication**: Login → JWT Token → Protected Routes → Admin Functions

## 📁 Project Structure

```
RAG/
├── app.py                      # Main application entry point
├── .env.example               # Environment configuration template
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── src/
│   ├── api/
│   │   └── api.py            # FastAPI routes and endpoints
│   ├── controller/
│   │   ├── document_controller.py  # Document management logic
│   │   └── query_controller.py     # Query processing logic
│   ├── model/
│   │   └── document.py       # Document data model
│   ├── userdb/
│   │   ├── database.py       # Database initialization
│   │   └── user_service.py   # User management service
│   └── core/
│       └── initialization.py # Component initialization
├── templates/
│   ├── index.html           # Main chat interface
│   └── admin.html           # Admin dashboard
├── static/
│   ├── assets/
│   │   ├── uploads/    # Uploaded documents (not in version control)
│   ├── css/                 # Stylesheets
│   └── js/                  # JavaScript files
├── chroma_db/               # Vector database storage
└── data/vectordb/                 # Vector database implementation and storage
```

## 🎯 Usage Examples

### Basic Query
```python
import requests

response = requests.post("http://localhost:8000/api/query", 
                        json={"text": "What is the company policy on remote work?"})
print(response.json())
```

### Admin Authentication
```python
import requests

# Login
login_response = requests.post("http://localhost:8000/api/admin/login", 
                              data={"username": "admin", "password": "password"})
token = login_response.json()["access_token"]

# Upload document
with open("document.pdf", "rb") as f:
    response = requests.post("http://localhost:8000/api/admin/documents/upload",
                           files={"file": f},
                           headers={"Authorization": f"Bearer {token}"})
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Gemini API Errors
```
Error: Invalid API key
```
**Solution**: Verify your `GEMINI_API_KEY` in the `.env` file

#### 2. Database Connection Issues
```
Error: Database not found
```
**Solution**: Ensure the database directory exists and has write permissions

#### 3. Document Upload Failures
```
Error: Only PDF files are supported
```
**Solution**: Ensure you're uploading valid PDF files

#### 4. Authentication Issues
```
Error: Invalid authentication credentials
```
**Solution**: Check JWT token validity and admin account status

### Debug Mode
Enable debug logging by setting Flask debug mode:
```python
app.run(debug=True, port=5000)
```

## 🚀 Deployment

### Production Deployment

#### 1. Security Configuration
- Generate secure JWT secret key
- Use environment-specific API keys
- Configure CORS for specific domains
- Set up HTTPS certificates

#### 2. Database Configuration
```bash
# For production, consider PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/ragdb
```

#### 3. Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000 8000
CMD ["python", "app.py"]
```

#### 4. Scaling Considerations
- Use Redis for session storage
- Implement load balancing for multiple instances
- Consider separate vector database server
- Monitor API rate limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review API documentation

## 🔄 Version History

- **v1.0.0**: Initial release with core RAG functionality
- **Future**: Planned features include multi-model support, advanced analytics, and enhanced UI

---

**Note**: This is an enterprise-grade application. Ensure proper security measures are in place before deploying to production environments.

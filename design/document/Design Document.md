# Enterprise Q&A Chatbot - Design Document

## 1. Introduction

The Enterprise Q&A Chatbot is a sophisticated system designed to provide users with accurate, context-aware answers to their queries by leveraging enterprise documents. It utilizes a Retrieval-Augmented Generation (RAG) architecture, integrating with a Large Language Model (LLM) like Google Gemini. The system features a user-facing chat interface and an admin dashboard for document and user management.

## 2. Requirements

### 2.1. Functional Requirements (FR)

#### FR1: User-Facing Chat Interface
*   **FR1.1:** Users shall be able to send text-based queries to the AI assistant.
*   **FR1.2:** The system shall display AI-generated responses to user queries.
*   **FR1.3:** Users shall be able to view the history of the current chat conversation.
*   **FR1.4:** The system shall display document sources when provided by the AI response.
*   **FR1.5:** Users shall be able to create a new chat session.
*   **FR1.6:** Users shall be able to load and switch between existing chat sessions.
*   **FR1.7:** Users shall be able to rename their chat sessions.
*   **FR1.8:** Users shall be able to delete a single chat session.
*   **FR1.9:** Users shall be able to delete multiple selected chat sessions.

#### FR2: Admin Dashboard & Management
*   **FR2.1: Admin Authentication**
    *   **FR2.1.1:** Admins shall be able to sign up using a username, password, and a system serial key.
    *   **FR2.1.2:** Admins shall be able to log in using their credentials.
    *   **FR2.1.3:** Admins shall be able to log out.
*   **FR2.2: Document Management (PDFs)**
    *   **FR2.2.1:** Admins shall be able to upload PDF documents (single or multiple).
    *   **FR2.2.2:** The system shall support drag & drop and file browse for uploads.
    *   **FR2.2.3:** Admins shall be able to view a list of all uploaded documents (showing filename, upload date).
    *   **FR2.2.4:** Admins shall be able to delete a single uploaded document.
    *   **FR2.2.5:** Admins shall be able to delete multiple selected documents.
*   **FR2.3: Admin User Account Management**
    *   **FR2.3.1:** Admins shall be able to view a list of all admin users.
    *   **FR2.3.2:** Admins shall be able to delete an admin user account (requires confirmation, potentially serial key).
    *   **FR2.3.3:** Admins shall be able to delete multiple selected admin user accounts.

#### FR3: Core Backend Processing
*   **FR3.1: Document Ingestion & Processing**
    *   **FR3.1.1:** The system shall extract text content from uploaded PDF documents.
    *   **FR3.1.2:** The system shall split extracted text into manageable chunks.
    *   **FR3.1.3:** The system shall generate vector embeddings for text chunks.
    *   **FR3.1.4:** The system shall store document metadata and vector embeddings in a vector database (ChromaDB).
*   **FR3.2: Retrieval-Augmented Generation (RAG)**
    *   **FR3.2.1:** The system shall perform semantic search in the vector database to find relevant document chunks based on the user's query.
    *   **FR3.2.2:** The system shall construct a context from the retrieved chunks.
    *   **FR3.2.3:** The system shall use prompt engineering to combine the user query and context for the AI model.
    *   **FR3.2.4:** The system shall integrate with an AI model (Google Gemini) to generate responses.
*   **FR3.3: API Services**
    *   **FR3.3.1:** The system shall provide API endpoints for user chat/query processing.
    *   **FR3.3.2:** The system shall provide API endpoints for admin authentication.
    *   **FR3.3.3:** The system shall provide API endpoints for document CRUD operations.
    *   **FR3.3.4:** The system shall provide API endpoints for admin user management.
    *   **FR3.3.5:** The system shall provide API endpoints for chat session management.

### 2.2. Non-Functional Requirements (NFR)

#### NFR1: Security
*   **NFR1.1:** Admin API endpoints shall be protected by JWT-based authentication.
*   **NFR1.2:** Admin signup and critical admin deletion operations shall require a valid system serial key.
*   **NFR1.3:** Admin passwords shall be stored securely (e.g., hashed).
*   **NFR1.4:** The system shall perform input validation on API requests.
*   **NFR1.5:** File uploads shall be handled securely.
*   **NFR1.6:** CORS shall be configured appropriately for web access.

#### NFR2: Usability
*   **NFR2.1:** The user chat interface shall be intuitive and easy to use.
*   **NFR2.2:** The admin dashboard shall be clear, organized, and provide easy access to management functions.
*   **NFR2.3:** The web interface shall be responsive across common device screen sizes.
*   **NFR2.4:** The system shall provide real-time feedback to users (e.g., "thinking" indicators, success/error messages).
*   **NFR2.5:** Navigation within the application shall be straightforward.

#### NFR3: Performance & Scalability
*   **NFR3.1:** Document retrieval from the vector database shall be efficient (low latency).
*   **NFR3.2:** AI model response times shall be acceptable for an interactive chat experience.
*   **NFR3.3:** The system should be able to handle a reasonable number of concurrent user sessions.
*   **NFR3.4:** Document processing time upon upload should be reasonable.

#### NFR4: Maintainability & Extensibility
*   **NFR4.1:** The codebase shall follow a modular architecture (e.g., separation of concerns).
*   **NFR4.2:** Critical system parameters (API keys, database paths, model names, Top-K) shall be configurable via environment variables or a configuration file.
*   **NFR4.3:** The system shall include logging for debugging and monitoring, especially for RAG processes.

#### NFR5: Reliability & Availability
*   **NFR5.1:** Admin accounts shall be persistently stored (e.g., in SQLite).
*   **NFR5.2:** Chat sessions and messages shall be persistently stored.
*   **NFR5.3:** Document metadata and embeddings shall be persistently stored (ChromaDB).
*   **NFR5.4:** The system shall implement robust error handling.
*   **NFR5.5:** Admin sessions shall have a configurable timeout.

#### NFR6: Configurability
*   **NFR6.1:** The Google Gemini API key and model name shall be configurable.
*   **NFR6.2:** The number of relevant chunks (Top-K) to retrieve for RAG shall be configurable.
*   **NFR6.3:** The admin serial key shall be configurable for system setup.
*   **NFR6.4:** Database paths and upload folders shall be configurable.

## 3. System Architecture

The system is designed with a modular architecture, separating concerns into distinct packages for core configuration, controllers, database interactions, data models, vector storage, and AI integration.

### 3.1. Component Overview (Based on Class Diagram)

*   **Core (`Config`)**:
    *   Manages all system-wide configurations such as API keys, database paths, model parameters, and operational settings (e.g., `DEBUG`, `HOST`, `PORT`).
*   **Controller Package**:
    *   `SystemController`: Handles system initialization and health status checks.
    *   `DocumentController`: Manages document lifecycle including upload, processing (text extraction, chunking), embedding generation, and storage/deletion in the vector database. Interacts with `ChromaDB`.
    *   `QueryController`: Processes user queries. It searches the `ChromaDB` for relevant document chunks, prepares context, interacts with `GeminiAI` for response generation, and manages chat message persistence via `ChatSessionManager`.
*   **Database Package**:
    *   `AdminAuthManager`: Manages admin user accounts, including registration (with serial key validation via `Config`), authentication (password hashing and verification), deletion, and listing of admin users. Persists admin data.
    *   `ChatSessionManager`: Manages user chat sessions. This includes creating, retrieving, renaming, and deleting sessions, as well as adding user and bot messages to a session. Persists chat data.
*   **Model Package**:
    *   `Document`: Represents an uploaded document with attributes like ID, filename, content, creation date, and metadata.
    *   `ChatSession`: Represents a user's conversation, including an ID, name, creation date, a list of messages, and message count.
    *   `ChatMessage`: Represents a single message within a chat session, detailing its ID, session ID, role (user/bot), content, timestamp, and any associated sources.
*   **VectorDB Package (`ChromaDB`)**:
    *   Provides an interface to the ChromaDB vector store. Handles initialization, adding documents (text chunks and embeddings), searching for similar chunks based on a query, deleting documents, and accessing the underlying collection.
*   **AI Package (`GeminiAI`)**:
    *   Interfaces with the Google Gemini AI model. Responsible for generating responses based on a user query and provided context. Includes prompt formatting and extraction of source information from the context.

### 3.2. Key Relationships

*   `SystemController` utilizes `DocumentController`, `QueryController`, and initializes `ChromaDB`.
*   `DocumentController` uses `ChromaDB` for vector storage and manages `Document` model instances.
*   `QueryController` queries `ChromaDB`, uses `GeminiAI` for response generation, and interacts with `ChatSessionManager` to save chat messages.
*   `AdminAuthManager` uses `Config` for the admin serial key.
*   `ChromaDB` stores and retrieves `Document` related data (embeddings and metadata).
*   `ChatSessionManager` manages `ChatSession` and `ChatMessage` model instances.
*   A `ChatSession` contains many `ChatMessage`s.

## 4. Data Model

### 4.1. Admin Database (admin_users.db)

The admin user information is stored in a relational database (e.g., SQLite).

**Entity: `admins`**

| Column          | Type    | Constraints                      | Description                     |
| :-------------- | :------ | :------------------------------- | :------------------------------ |
| `id`            | INTEGER | PRIMARY KEY, AUTOINCREMENT       | Unique identifier for the admin |
| `username`      | TEXT    | UNIQUE, NOT NULL                 | Admin's chosen username         |
| `password_hash` | TEXT    | NOT NULL                         | Hashed password for the admin   |

*(Other data models like `ChatSession` and `ChatMessage` are managed by `ChatSessionManager` and would typically reside in a separate database or the same database in different tables. Document content and embeddings are managed by `ChromaDB`.)*

## 5. Process Flows / Use Cases

### 5.1. User Query Processing

This flow describes how the system handles a query from a user.

1.  **User Input**: The user types a query into the Chat UI ([`static/js/chat.js`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\static\js\chat.js)) and clicks "Send".
2.  **Session Check (UI)**:
    *   If no `currentSessionId` exists in the UI, the `createNewSession()` function is called.
    *   `createNewSession()` sends a POST request to `/api/sessions`.
    *   The API ([`src/api/api.py`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\src\api\api.py)) receives the request.
    *   `ChatSessionManager` creates a new session in the database.
    *   The API returns new session data (ID, initial message).
    *   The Chat UI sets `currentSessionId` and displays an initial bot message. The user may need to resend their original query.
3.  **Send Message (UI)**:
    *   The Chat UI (`sendMessage` function in [`static/js/chat.js`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\static\js\chat.js)) disables the input field and shows a "thinking" indicator.
    *   It sends the query and `currentSessionId` via an AJAX POST request to `/api/query`.
4.  **API Request Handling (`/api/query`)**:
    *   The API endpoint in [`src/api/api.py`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\src\api\api.py) receives the request.
    *   It calls `query_controller.process_chat_message(session_id, query)`.
5.  **QueryController Processing ([`src/controller/query_controller.py`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\src\controller\query_controller.py))**:
    *   The user's message is saved to the ChatSessionDB via `ChatSessionManager`.
    *   The `QueryController` searches `VectorDB (ChromaDB)` for relevant document chunks using the query (`search_similar_chunks`).
    *   If relevant chunks are found, a context is constructed from these chunks. Otherwise, the context may be empty or a default prompt is used.
    *   The `QueryController` calls `GeminiAI.generate_response(query, context)`.
    *   The `GeminiAI` model processes the query and context, returning an AI-generated response and source information.
    *   The AI's response and sources are saved to the ChatSessionDB via `ChatSessionManager`.
    *   A dictionary `{content, sources}` is returned to the API endpoint.
6.  **API Response**:
    *   The API endpoint (`/api/query`) sends a JSON response containing the AI's content and sources back to the Chat UI.
7.  **Display Response (UI)**:
    *   The Chat UI (success callback in `sendMessage` in [`static/js/chat.js`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\static\js\chat.js)) removes the "thinking" indicator.
    *   It calls `addBotMessage()` to display the AI response and its sources.
    *   The input field and send button are re-enabled.
    *   The chat view scrolls to the bottom.

*(This aligns with the "User Query Processing Sequence" diagram.)*

### 5.2. Document Upload and Processing

This flow describes how an admin uploads and processes new PDF documents.

1.  **Admin Navigation**: Admin navigates to the Admin Dashboard (`/admin`). This requires admin login and the page is served by [`app.py`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\app.py) with JavaScript logic in [`static/js/admin.js`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\static\js\admin.js).
2.  **File Selection**: Admin drags & drops PDF file(s) onto the dropzone or uses the "Browse Files" button to select PDF(s).
3.  **Upload Action**: Admin clicks the "Upload Document" button.
4.  **Admin UI Handling (`admin.js`)**:
    *   The `uploadFile` function in `admin.js` creates `FormData` with the selected file(s).
    *   A progress bar is displayed.
    *   File(s) are sent via an AJAX POST request to `/api/upload`.
5.  **API Request Handling (`/api/upload`)**:
    *   The API endpoint in [`src/api/api.py`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\src\api\api.py) receives the request.
    *   It initializes a list to store results for each file.
    *   For each file in the request:
        *   The API calls `document_controller.upload_document(file)`.
6.  **DocumentController Processing (`document_controller.py`)**:
    *   The `upload_document(file_storage_object)` method is called.
    *   The file is validated (e.g., is PDF, checks size).
    *   If validation fails, an error result is recorded for the file.
    *   If validation is OK:
        *   A unique filename is generated.
        *   The original file is saved to `Config.UPLOAD_FOLDER`.
        *   `self.process_document(saved_filepath, original_filename)` is called.
        *   **`process_document` method**:
            *   Text content is extracted from the PDF file.
            *   The extracted text is split into manageable chunks.
            *   For each text chunk, a vector embedding is generated (e.g., using `GeminiAI` or another embedding model).
            *   The document (metadata, text chunks, embeddings) is added to `VectorDB (ChromaDB)`.
            *   A success or error result is recorded based on the outcome of VectorDB storage.
    *   The result for this file is added to the list of results.
7.  **API Response Compilation**:
    *   The `/api/upload` endpoint compiles all results.
    *   The API sends a JSON response (e.g., a list of `{filename, status, message}` objects) to the Admin UI.
8.  **Admin UI Update (`admin.js`)**:
    *   The AJAX callback in `admin.js` updates/hides the progress bar.
    *   Success or error alert message(s) are shown based on the API response.
    *   The file input field/dropzone is reset.
    *   `loadDocuments()` is called to refresh the list of uploaded documents in the UI.

## 6. API Design (Brief Overview)

The system exposes RESTful API endpoints primarily through [`src/api/api.py`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\src\api\api.py). Key endpoint categories include:

*   **User Chat/Query Processing**:
    *   `POST /api/query`: Submits a user query for processing.
    *   `POST /api/sessions`: Creates a new chat session.
    *   `GET /api/sessions`: Retrieves all chat sessions.
    *   `GET /api/sessions/{session_id}`: Retrieves a specific chat session.
    *   `POST /api/sessions/{session_id}/rename`: Renames a chat session.
    *   `DELETE /api/sessions/{session_id}`: Deletes a single chat session.
    *   `POST /api/sessions/delete`: Deletes multiple selected chat sessions.
*   **Admin Authentication**:
    *   Endpoints for admin signup, login, and logout (likely `/api/admin/signup`, `/api/admin/login`, `/api/admin/logout`).
*   **Document CRUD Operations**:
    *   `POST /api/upload` (or similar like `/api/documents/upload`): Uploads new PDF documents.
    *   `GET /api/documents`: Lists uploaded documents.
    *   `DELETE /api/documents/{document_id}`: Deletes a specific document.
    *   (Potentially an endpoint for deleting multiple documents).
*   **Admin User Management**:
    *   Endpoints for listing admin users and deleting admin accounts (e.g., `/api/admin/users`, `/api/admin/users/{user_id}`).

Admin-related API endpoints are protected by JWT-based authentication.

## 7. User Interface (UI) Design (Brief Overview)

The application provides two main web interfaces served by Flask ([`app.py`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\app.py)):

*   **User Chat Interface ([`templates/index.html`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\templates\index.html)):**
    *   Allows users to send queries and view AI responses.
    *   Displays chat history for the current session.
    *   Shows document sources if provided.
    *   Provides controls for creating new sessions, loading, renaming, and deleting sessions (single and multiple).
    *   Features real-time feedback like "thinking" indicators.
    *   JavaScript for interactivity is primarily in [`static/js/chat.js`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\static\js\chat.js).
*   **Admin Dashboard ([`templates/admin.html`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\templates\admin.html)):**
    *   Requires admin login.
    *   Provides functionality for PDF document management:
        *   Upload (drag & drop, file browse).
        *   View list of uploaded documents.
        *   Delete documents (single and multiple).
    *   Provides functionality for admin user account management:
        *   View list of admin users.
        *   Delete admin accounts.
    *   JavaScript for interactivity is primarily in [`static/js/admin.js`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\static\js\admin.js).

Both interfaces aim for intuitiveness, responsiveness, and clear navigation. Styling is managed by CSS, including [`static/css/main.css`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\static\css\main.css).

## 8. Configuration

System configuration is managed through environment variables and the `Config` class ([`src/core/config.py`](d:\DOCUMENTS\WORK DOCUMENTS\DXB WORK DOC\HLB Hamt\Projects\RAG\src\core\config.py)). Key configurable parameters include:

*   `DEBUG`: Debug mode flag.
*   `HOST`, `PORT`: Host and port for the application.
*   `UPLOAD_FOLDER`: Path to store uploaded documents.
*   `VECTORDB_PATH`: Path for ChromaDB persistence.
*   `ADMIN_SERIAL_KEY`: Serial key required for admin signup.
*   `GEMINI_API_KEY`: API key for Google Gemini.
*   `GEMINI_MODEL`: Specific Gemini model to be used.
*   `TOP_K`: Number of relevant chunks to retrieve for RAG.
*   Database paths (e.g., for admin and chat session SQLite databases).
*   `FLASK_SECRET_KEY`: Secret key for Flask session management.
*   JWT secret key for API authentication.

These configurations allow for flexibility in deployment and maintenance.
import os
from typing import Dict, Any
from src.core.config import Config
from src.controller.document_controller import DocumentController
from src.controller.response_controller import ResponseController
from src.controller.query_controller import QueryController
from src.controller.session_controller import SessionController

class SystemController:
    """Main system controller that coordinates all operations"""
    def __init__(self):
        self.response_controller = ResponseController()
        self.document_controller = DocumentController()
        self.query_controller = QueryController(self.response_controller)
        self.session_controller = SessionController()

    def initialize(self) -> None:
        print("System initialized")

    def shutdown(self) -> None:
        print("System shutdown")

    def process_query(self, query_text: str, session_id: str = None) -> Dict[str, Any]:
        if not session_id:
            session_data = self.session_controller.create_session()
            session_id = session_data["id"]
        self.session_controller.add_message_to_session(session_id, "user", query_text)
        response = self.query_controller.process_query(query_text, session_id)
        self.session_controller.add_message_to_session(
            session_id,
            "bot",
            response.get("content", ""),
            response.get("sources", [])
        )
        response["session_id"] = session_id
        return response

    def process_document(self, file_path: str, filename: str, original_filename: str = None) -> bool:
        return self.document_controller.upload_document(file_path, filename, original_filename)

    def get_documents(self) -> list:
        return self.document_controller.get_documents()

    def delete_document(self, document_id: str) -> bool:
        try:
            return self.document_controller.delete_document_by_id(document_id)
        except Exception as e:
            print(f"Error deleting document {document_id}: {e}")
            return False

    def get_session(self, session_id: str) -> Dict[str, Any]:
        return self.session_controller.load_session(session_id)

    def create_session(self, user_id: str = "anonymous") -> Dict[str, Any]:
        return self.session_controller.create_session(user_id)

    def get_user_sessions(self, user_id: str = "anonymous") -> list:
        return self.session_controller.get_user_sessions(user_id)

    def delete_session(self, session_id: str) -> bool:
        return self.session_controller.delete_session(session_id)

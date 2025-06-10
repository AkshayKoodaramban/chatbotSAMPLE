import json, os, uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

class SessionController:
    """Controller for managing chat sessions"""
    def __init__(self, sessions_dir: str = "static/json"):
        self.sessions_dir = sessions_dir
        os.makedirs(self.sessions_dir, exist_ok=True)

    def get_session_file_path(self, session_id: str) -> str:
        return os.path.join(self.sessions_dir, f"{session_id}.json")

    def create_session(self, user_id: str = "anonymous") -> Dict[str, Any]:
        session_id = f"sess-{str(uuid.uuid4())}"
        session_data = {
            "id": session_id,
            "name": "New Chat",
            "user_id": user_id,
            "messages": [
                {
                    "role": "bot",
                    "content": "Hello! I'm your Enterprise Q&A Assistant. How can I help you today?",
                    "time": datetime.now().isoformat(),
                    "sources": []
                }
            ],
            "created_at": datetime.now().isoformat()
        }
        self.save_session(session_data)
        return session_data

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        file_path = self.get_session_file_path(session_id)
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict):
                    data = data[0]
                if not isinstance(data, dict):
                    return None
                return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def save_session(self, session_data: Dict[str, Any]) -> bool:
        session_id = session_data.get("id")
        if not session_id:
            return False
        file_path = self.get_session_file_path(session_id)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving session {session_id}: {e}")
            return False

    def add_message_to_session(self, session_id: str, role: str, content: str, sources: List[Dict] = None) -> bool:
        session_data = self.load_session(session_id)
        if not session_data:
            return False
        message = {
            "role": role,
            "content": content,
            "time": datetime.now().isoformat(),
            "sources": sources or []
        }
        session_data["messages"].append(message)
        if role == "user" and len([m for m in session_data["messages"] if m["role"] == "user"]) == 1:
            words = content.split()[:4]
            session_data["name"] = " ".join(words) if words else "New Chat"
        return self.save_session(session_data)

    def get_user_sessions(self, user_id: str = "anonymous") -> List[Dict[str, Any]]:
        sessions = []
        if not os.path.exists(self.sessions_dir):
            return sessions
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith('.json') and filename.startswith('sess-'):
                session_id = filename[:-5]
                session_data = self.load_session(session_id)
                if session_data and session_data.get("user_id") == user_id:
                    sessions.append({
                        "id": session_data["id"],
                        "name": session_data["name"],
                        "created_at": session_data["created_at"],
                        "message_count": len(session_data.get("messages", []))
                    })
        sessions.sort(key=lambda x: x["created_at"], reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> bool:
        file_path = self.get_session_file_path(session_id)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except OSError as e:
            print(f"Error deleting session {session_id}: {e}")
            return False

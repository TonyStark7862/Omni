import csv
import os
from datetime import datetime
from typing import Dict, List, Optional

class Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.chat_history = []
        self.name = session_id

class PersistentStorage:
    def __init__(self, base_path: str = "./storage/"):
        self.base_path = base_path
        self.sessions_file = os.path.join(base_path, "sessions.csv")
        self.history_file = os.path.join(base_path, "history.csv")
        self.names_file = os.path.join(base_path, "session_names.csv")
        self._init_files()

    def _init_files(self):
        # Initialize sessions file
        if not os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['session_id', 'created_at'])

        # Initialize history file
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['session_id', 'role', 'content', 'timestamp'])

        # Initialize names file
        if not os.path.exists(self.names_file):
            with open(self.names_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['session_id', 'name'])

    def save_chat_message(self, session_id: str, role: str, content: str, name: str):
        # Ensure session exists
        self._ensure_session_exists(session_id)
        
        # Save message to history
        with open(self.history_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                session_id,
                role,
                content,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])

    def save_session_name(self, session_id: str, name: str):
        with open(self.names_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([session_id, name])

    def get_chat_history(self, session_id: str) -> List[Dict]:
        history = []
        with open(self.history_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['session_id'] == session_id:
                    history.append({
                        'role': row['role'],
                        'content': row['content']
                    })
        return history

    def get_all_sessions(self) -> List[str]:
        sessions = []
        with open(self.sessions_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sessions.append(row['session_id'])
        return sessions

    def get_all_sessions_names(self) -> Dict[str, str]:
        names = {}
        with open(self.names_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                names[row['session_id']] = row['name']
        return names

    def delete_session(self, session_id: str):
        # Remove from sessions file
        self._remove_from_file(self.sessions_file, session_id)
        # Remove from history file
        self._remove_from_file(self.history_file, session_id)
        # Remove from names file
        self._remove_from_file(self.names_file, session_id)

    def _remove_from_file(self, file_path: str, session_id: str):
        temp_file = file_path + '.tmp'
        with open(file_path, 'r', newline='') as f_in, \
             open(temp_file, 'w', newline='') as f_out:
            reader = csv.DictReader(f_in)
            writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                if row['session_id'] != session_id:
                    writer.writerow(row)
        os.replace(temp_file, file_path)

    def _ensure_session_exists(self, session_id: str):
        sessions = self.get_all_sessions()
        if session_id not in sessions:
            with open(self.sessions_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    session_id,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ])

    def reset_all_session_names_to_default(self):
        # Clear names file and rewrite with session IDs as names
        with open(self.names_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['session_id', 'name'])
            sessions = self.get_all_sessions()
            for session_id in sessions:
                writer.writerow([session_id, session_id])

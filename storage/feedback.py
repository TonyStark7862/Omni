import csv
import os
from datetime import datetime
from typing import Dict, List

class FeedbackTracker:
    def __init__(self, feedback_file: str = "feedback.csv"):
        self.feedback_file = feedback_file
        self._init_feedback_file()
    
    def _init_feedback_file(self):
        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'session_id', 'question', 'answer', 'tokens_used'])
    
    def log_interaction(self, session_id: str, question: str, answer: str, tokens_used: int = 0):
        with open(self.feedback_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                session_id,
                question,
                answer,
                tokens_used
            ])
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        history = []
        with open(self.feedback_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['session_id'] == session_id:
                    history.append(row)
        return history

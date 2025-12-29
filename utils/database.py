from datetime import datetime
import json
import uuid
import sqlite3

DB="interviews.db"

def init_db():
    conn=sqlite3.connect(DB)
    c=conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            timestamp TEXT,
            feedback_json TEXT
        )
    ''')
    conn.commit()
    conn.close()

def generate_user_id():
    unique_str=str(uuid.uuid4())[:8]
    return f"user_{unique_str}"

def save_interview(user_id,role,feedback_log):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    feedback_str = json.dumps(feedback_log)
    c.execute('''
        INSERT INTO interviews (user_id, role, timestamp, feedback_json)
        VALUES (?, ?, ?, ?)
    ''', (user_id, role, timestamp, feedback_str))
    
    conn.commit()
    conn.close()
def fetch_history(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        SELECT id, role, timestamp 
        FROM interviews 
        WHERE user_id = ? 
        ORDER BY id DESC
    ''', (user_id,))
    
    rows = c.fetchall()
    conn.close()
    return rows

def get_interview_data(interview_db_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    c.execute('SELECT feedback_json FROM interviews WHERE id = ?', (interview_db_id,))
    row = c.fetchone()
    
    conn.close()
    
    if row:
        return json.loads(row[0])
    return None
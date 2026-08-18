import sqlite3
import os
import sys
from pathlib import Path

# Add project root to path to ensure cross-module imports work
sys.path.append(str(Path(__file__).parent.parent))

from security.password_manager import hash_password

DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "securefile.db"

def get_connection():
    """
    Returns a new SQLite connection to ensure thread safety.
    """
    # Ensure data directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Creates necessary tables and seeds initial user and settings.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            failed_logins INTEGER DEFAULT 0,
            lockout_until REAL DEFAULT 0.0
        )
    """)
    
    # 2. Files Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            encrypted_path TEXT UNIQUE NOT NULL,
            original_size INTEGER NOT NULL,
            encrypted_size INTEGER NOT NULL,
            encryption_date TEXT NOT NULL,
            status TEXT DEFAULT 'ENCRYPTED'
        )
    """)
    
    # 3. Activity Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            username TEXT NOT NULL,
            filename TEXT,
            operation TEXT NOT NULL,
            original_size INTEGER,
            result TEXT NOT NULL,
            duration REAL
        )
    """)
    
    # 4. Settings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    # Seed default user if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        admin_hash = hash_password("Admin@123")
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("admin", admin_hash)
        )
    
    # Seed default settings
    default_settings = {
        "theme": "Dark",
        "confirm_delete": "True",
        "auto_clear_temp": "True",
        "default_encrypt_dir": "",
        "default_decrypt_dir": ""
    }
    
    for key, val in default_settings.items():
        cursor.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, val)
        )
        
    conn.commit()
    conn.close()

# Users related operations
def get_user(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_lockout(username: str, failed_logins: int, lockout_until: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET failed_logins = ?, lockout_until = ? WHERE username = ?",
        (failed_logins, lockout_until, username)
    )
    conn.commit()
    conn.close()

def change_user_password(username: str, new_password_hash: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password_hash = ?, failed_logins = 0, lockout_until = 0.0 WHERE username = ?",
        (new_password_hash, username)
    )
    conn.commit()
    conn.close()

# Files related operations
def add_file(filename: str, encrypted_path: str, original_size: int, encrypted_size: int, encryption_date: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT OR REPLACE INTO files 
           (filename, encrypted_path, original_size, encrypted_size, encryption_date, status) 
           VALUES (?, ?, ?, ?, ?, 'ENCRYPTED')""",
        (filename, encrypted_path, original_size, encrypted_size, encryption_date)
    )
    conn.commit()
    conn.close()

def get_all_files():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE status != 'DELETED'")
    files = cursor.fetchall()
    conn.close()
    return [dict(f) for f in files]

def update_file_status(encrypted_path: str, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE files SET status = ? WHERE encrypted_path = ?",
        (status, encrypted_path)
    )
    conn.commit()
    conn.close()

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total files encrypted (excluding deleted files)
    cursor.execute("SELECT COUNT(*) FROM files WHERE status = 'ENCRYPTED'")
    total_encrypted = cursor.fetchone()[0]
    
    # Total files decrypted
    cursor.execute("SELECT COUNT(*) FROM files WHERE status = 'DECRYPTED'")
    total_decrypted = cursor.fetchone()[0]
    
    # Total storage protected (sum of original sizes of currently encrypted files)
    cursor.execute("SELECT SUM(original_size) FROM files WHERE status = 'ENCRYPTED'")
    total_size = cursor.fetchone()[0]
    total_size = total_size if total_size is not None else 0
    
    # Success operations
    cursor.execute("SELECT COUNT(*) FROM activity_logs WHERE result = 'SUCCESS'")
    success_ops = cursor.fetchone()[0]
    
    # Failed operations
    cursor.execute("SELECT COUNT(*) FROM activity_logs WHERE result = 'FAILED'")
    failed_ops = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_encrypted": total_encrypted,
        "total_decrypted": total_decrypted,
        "total_size": total_size,
        "success_ops": success_ops,
        "failed_ops": failed_ops
    }

# Activity logs operations
def log_activity(timestamp: str, username: str, filename: str, operation: str, original_size: int, result: str, duration: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO activity_logs 
           (timestamp, username, filename, operation, original_size, result, duration) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (timestamp, username, filename, operation, original_size, result, duration)
    )
    conn.commit()
    conn.close()

def get_activity_logs(search_query: str = "", operation_filter: str = "All"):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM activity_logs WHERE 1=1"
    params = []
    
    if search_query:
        query += " AND (filename LIKE ? OR username LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    if operation_filter and operation_filter != "All":
        query += " AND operation = ?"
        params.append(operation_filter)
        
    query += " ORDER BY id DESC"
    
    cursor.execute(query, params)
    logs = cursor.fetchall()
    conn.close()
    return [dict(l) for l in logs]

def clear_activity_logs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM activity_logs")
    conn.commit()
    conn.close()

# Settings operations
def get_settings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM settings")
    settings = cursor.fetchall()
    conn.close()
    return {row["key"]: row["value"] for row in settings}

def update_setting(key: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()

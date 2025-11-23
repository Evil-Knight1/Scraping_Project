import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

DB_NAME = "scraper_history.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create crawl_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crawl_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            params TEXT,
            result TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create search_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            params TEXT,
            result TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_cached_crawl(url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Simple cache check: same URL and params
    # In a real-world scenario, you might want to normalize params or have an expiration policy
    params_json = json.dumps(params, sort_keys=True)
    
    cursor.execute(
        "SELECT result FROM crawl_history WHERE url = ? AND params = ? ORDER BY timestamp DESC LIMIT 1",
        (url, params_json)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return json.loads(row['result'])
    return None

def save_crawl_result(url: str, params: Dict[str, Any], result: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    params_json = json.dumps(params, sort_keys=True)
    result_json = json.dumps(result)
    
    cursor.execute(
        "INSERT INTO crawl_history (url, params, result) VALUES (?, ?, ?)",
        (url, params_json, result_json)
    )
    conn.commit()
    conn.close()

def get_cached_search(query: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    params_json = json.dumps(params, sort_keys=True)
    
    cursor.execute(
        "SELECT result FROM search_history WHERE query = ? AND params = ? ORDER BY timestamp DESC LIMIT 1",
        (query, params_json)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return json.loads(row['result'])
    return None

def save_search_result(query: str, params: Dict[str, Any], result: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    params_json = json.dumps(params, sort_keys=True)
    result_json = json.dumps(result)
    
    cursor.execute(
        "INSERT INTO search_history (query, params, result) VALUES (?, ?, ?)",
        (query, params_json, result_json)
    )
    conn.commit()
    conn.close()

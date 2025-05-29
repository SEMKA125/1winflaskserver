from flask import Flask, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Подключаем базу данных SQLite
def get_db_connection():
    conn = sqlite3.connect('1win_registrations.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Инициализация базы данных
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        registration_date TEXT,
        hash_id TEXT,
        source_id TEXT
    )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return "1Win Postback Server is running"

@app.route('/1win_postback', methods=['GET'])
def handle_postback():
    try:
        # Получаем параметры от 1Win
        event_id = request.args.get('event_id')
        date = request.args.get('date')
        hash_id = request.args.get('hash_id')
        source_id = request.args.get('source_id')  # Это должен быть user_id из Telegram

        # Проверяем обязательные параметры
        if not all([event_id, date, hash_id, source_id]):
            return 'Missing parameters', 400

        # Проверяем, что это событие регистрации (event_id=1)
        if event_id == '1':
            try:
                reg_date = datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                return 'Invalid date format', 400

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, registration_date, hash_id, source_id)
            VALUES (?, ?, ?, ?)
            ''', (source_id, reg_date, hash_id, source_id))
            conn.commit()
            conn.close()
            return 'OK', 200
        
        return 'Invalid event', 400

    except Exception as e:
        print(f"Error: {e}")
        return 'Server error', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

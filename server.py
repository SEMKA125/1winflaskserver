from flask import Flask, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Подключаем базу данных SQLite
conn = sqlite3.connect('1win_registrations.db', check_same_thread=False)
cursor = conn.cursor()

# Создаем таблицу для хранения регистраций
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    registration_date TEXT,
    hash_id TEXT,
    source_id TEXT
)
''')
conn.commit()

@app.route('/1win_postback', methods=['GET'])
def handle_postback():
    try:
        # Получаем параметры от 1Win
        event_id = request.args.get('event_id')
        date = request.args.get('date')
        hash_id = request.args.get('hash_id')
        source_id = request.args.get('source_id')  # Это должен быть user_id из Telegram

        # Проверяем, что это событие регистрации (event_id=1)
        if event_id == '1':
            reg_date = datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, registration_date, hash_id, source_id)
            VALUES (?, ?, ?, ?)
            ''', (source_id, reg_date, hash_id, source_id))
            conn.commit()
            return 'OK', 200
        
        return 'Invalid event', 400

    except Exception as e:
        print(f"Error: {e}")
        return 'Server error', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
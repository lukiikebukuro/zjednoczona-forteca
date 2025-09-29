from app import app, socketio, bot, DatabaseManager, start_simulator
from datetime import datetime, timedelta
import sqlite3

# Initialize on module load
with app.app_context():
    print("[WSGI] Initializing application...")
    
    bot.initialize_data()
    DatabaseManager.initialize_database()
    
    # Clear old events
    try:
        conn = sqlite3.connect('dashboard.db')
        cursor = conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('DELETE FROM events WHERE date(timestamp) < ?', (cutoff_date,))
        conn.commit()
        conn.close()
        print("[WSGI] Database cleaned")
    except Exception as e:
        print(f"[WSGI] Database error: {e}")
    
    start_simulator()
    print("[WSGI] Application initialized")

# Export for gunicorn
application = app

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from datetime import timedelta, datetime
from ecommerce_bot import EcommerceBot
import sqlite3
import json
import time
import random
import threading
import os
import requests
import uuid
import csv

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Session configuration
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_PERMANENT'] = False

# Initialize SocketIO for dashboard
socketio = SocketIO(app, 
    cors_allowed_origins="*", 
    async_mode='eventlet',
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)

# Initialize bot
bot = EcommerceBot()

# Lost demand log file
LOST_DEMAND_LOG = 'lost_demand_log.csv'

# Dashboard database configuration
DATABASE_NAME = 'dashboard.db'

# === DASHBOARD CLASSES ===
class TacticalDataSimulator:
    """Symulator danych bojowych dla dashboardu demonstracyjnego"""
    
    def __init__(self):
        self.price_ranges = {
            'klocki': {'standard': 150, 'premium': 300, 'luxury': 450},
            'filtry': {'standard': 75, 'premium': 120, 'luxury': 180},
            'amortyzatory': {'standard': 400, 'premium': 650, 'luxury': 950},
            'świece': {'standard': 45, 'premium': 65, 'luxury': 85},
            'akumulatory': {'standard': 350, 'premium': 450, 'luxury': 600},
            'oleje': {'standard': 120, 'premium': 180, 'luxury': 250},
            'tarcze': {'standard': 200, 'premium': 350, 'luxury': 500},
            'łańcuchy': {'standard': 250, 'premium': 350, 'luxury': 450}
        }
        
        self.battle_scenarios = [
            {'query': 'klocki ferrari', 'decision': 'UTRACONE OKAZJE', 'details': 'Marka Luksusowa', 'category': 'klocki', 'brand_type': 'luxury', 'explanation': 'System rozpoznał markę premium której nie mamy w ofercie'},
            {'query': 'amortyzatory lamborghini', 'decision': 'UTRACONE OKAZJE', 'details': 'Marka Luksusowa', 'category': 'amortyzatory', 'brand_type': 'luxury', 'explanation': 'Wykryto zapytanie o części do supersamochodu'},
            {'query': 'części porsche', 'decision': 'UTRACONE OKAZJE', 'details': 'Marka Premium', 'category': 'klocki', 'brand_type': 'luxury', 'explanation': 'Klient szuka części do marki premium'},
            {'query': 'klocki bmw n123', 'decision': 'UTRACONE OKAZJE', 'details': 'Nieistniejący Kod', 'category': 'klocki', 'brand_type': 'premium', 'explanation': 'Kod produktu nie istnieje w bazie danych'},
            {'query': 'filtr 0986494999', 'decision': 'UTRACONE OKAZJE', 'details': 'Kod OE Nieznaleziony', 'category': 'filtry', 'brand_type': 'standard', 'explanation': 'System nie rozpoznał kodu OE'},
            {'query': 'opony zimowe', 'decision': 'UTRACONE OKAZJE', 'details': 'Brak Kategorii', 'category': 'opony', 'brand_type': 'standard', 'explanation': 'Nie obsługujemy kategorii opon'},
            {'query': 'kloki bosh', 'decision': 'ODFILTROWANE', 'details': 'klocki Bosch', 'category': 'klocki', 'brand_type': 'standard', 'explanation': 'System poprawił błąd pisowni i znalazł produkt'},
            {'query': 'filetr man', 'decision': 'ODFILTROWANE', 'details': 'filtr Mann', 'category': 'filtry', 'brand_type': 'standard', 'explanation': 'Automatyczna korekta literówki'},
            {'query': 'klocki bosch', 'decision': 'ZNALEZIONE PRODUKTY', 'details': 'Znaleziono Produkt', 'category': 'klocki', 'brand_type': 'standard', 'explanation': 'Dokładne dopasowanie marki i kategorii'},
            {'query': 'filtr mann bmw', 'decision': 'ZNALEZIONE PRODUKTY', 'details': 'Dopasowanie Marki+Model', 'category': 'filtry', 'brand_type': 'standard', 'explanation': 'System znalazł filter Mann do BMW'},
            {'query': 'asdasdasd', 'decision': 'ODFILTROWANE', 'details': 'Nonsensowne zapytanie', 'category': 'inne', 'brand_type': 'standard', 'explanation': 'System rozpoznał nonsensowne zapytanie'}
        ]
        
        self.running = False
        self.paused = False
        self.thread = None
        
    def calculate_lost_value(self, category, brand_type):
        if category not in self.price_ranges:
            return random.randint(100, 300)
        base_price = self.price_ranges[category][brand_type]
        variation = random.uniform(0.8, 1.2)
        return int(base_price * variation)
    
    def pause_simulator(self):
        self.paused = True
        print("[SIMULATOR] Paused by user interaction")

    def resume_simulator(self):
        self.paused = False
        print("[SIMULATOR] Resumed by user interaction")

class DatabaseManager:
    """Zarządza bazą danych SQLite dla dashboardu"""
    
    @staticmethod
    def initialize_database():
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                query_text TEXT NOT NULL,
                decision TEXT NOT NULL,
                details TEXT,
                category TEXT,
                brand_type TEXT,
                potential_value INTEGER,
                explanation TEXT
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_decision ON events(decision)')
        
        conn.commit()
        conn.close()
        print("[DATABASE] Events table initialized")
    
    @staticmethod
    def add_event(query_text, decision, details, category, brand_type, potential_value, explanation):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (query_text, decision, details, category, brand_type, potential_value, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (query_text, decision, details, category, brand_type, potential_value, explanation))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return event_id
    
    @staticmethod
    def get_recent_events(limit=10):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, query_text, decision, details, category, 
                   brand_type, potential_value, explanation
            FROM events 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        events = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'timestamp': row[1],
                'query_text': row[2], 
                'decision': row[3],
                'details': row[4],
                'category': row[5],
                'brand_type': row[6],
                'potential_value': row[7],
                'explanation': row[8]
            }
            for row in events
        ]
    
    @staticmethod
    def get_today_statistics():
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT decision, COUNT(*) as count, COALESCE(SUM(potential_value), 0) as total_value
            FROM events 
            WHERE date(timestamp) = ?
            GROUP BY decision
        ''', (today,))
        
        results = cursor.fetchall()
        conn.close()
        
        stats = {
            'UTRACONE OKAZJE': {'count': 0, 'value': 0},
            'ODFILTROWANE': {'count': 0, 'value': 0}, 
            'ZNALEZIONE PRODUKTY': {'count': 0, 'value': 0}
        }
        
        for decision, count, value in results:
            if decision in stats:
                stats[decision]['count'] = count
                stats[decision]['value'] = int(value)
        
        return stats
    
    @staticmethod
    def get_top_missing_products(limit=5):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT category, COUNT(*) as frequency, SUM(potential_value) as total_value
            FROM events 
            WHERE decision = 'UTRACONE OKAZJE' 
            AND date(timestamp) >= ?
            GROUP BY category
            ORDER BY frequency DESC, total_value DESC
            LIMIT ?
        ''', (week_ago, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'category': row[0],
                'frequency': row[1],
                'total_value': int(row[2]) if row[2] else 0
            }
            for row in results
        ]

simulator = TacticalDataSimulator()

# === ROUTES ===
@app.route('/')
def home():
    return render_template('index.html')
    
@app.route('/demo-motobot.html')
def demo_motobot():
    return render_template('demo-motobot.html')

@app.route('/motobot-prototype')
def motobot_index():
    return render_template('demo_page.html')

@app.route('/demo')
def demo_page():
    return render_template('demo_page.html')

@app.route('/motobot-prototype/bot/start', methods=['POST'])
def bot_start():
    try:
        session.permanent = True
        session['cart'] = []
        session['context'] = None
        session['machine_filter'] = None
        
        initial_response = bot.get_initial_greeting()
        
        return jsonify({'reply': initial_response})
    
    except Exception as e:
        print(f"[ERROR] Bot start error: {e}")
        return jsonify({
            'reply': {
                'text_message': f'Wystąpił błąd podczas inicjalizacji: {str(e)}',
                'buttons': [{'text': 'Spróbuj ponownie', 'action': 'restart'}]
            }
        }), 500

@app.route('/motobot-prototype/bot/send', methods=['POST'])
def bot_send():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        button_action = data.get('button_action', '')
        
        if button_action:
            reply = bot.handle_button_action(button_action)
        elif user_message:
            reply = bot.process_message(user_message)
            
            if hasattr(reply, 'get') and reply.get('confidence_level'):
                send_event_to_dashboard_internal(user_message, reply['confidence_level'])
        else:
            return jsonify({'error': 'No message or action provided'}), 400
        
        return jsonify({'reply': reply})
    
    except Exception as e:
        print(f"[ERROR] Bot send error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'reply': {
                'text_message': 'Wystąpił błąd podczas przetwarzania żądania.',
                'buttons': [{'text': 'Powrót do menu', 'action': 'main_menu'}]
            }
        }), 500
@app.route('/motobot-prototype/search-suggestions', methods=['POST'])
def search_suggestions():
    """LEGACY - zachowane dla kompatybilności"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        search_type = data.get('type', 'products')
        
        if len(query) < 2:
            return jsonify({'suggestions': [], 'confidence_level': 'NONE'})
        
        suggestions = []
        confidence_level = 'HIGH'
        ga4_event = None
        
        if search_type == 'faq':
            faq_results = bot.get_fuzzy_faq_matches(query, limit=5)
            for faq, score in faq_results:
                suggestions.append({
                    'id': faq['id'],
                    'text': faq['question'],
                    'type': 'faq',
                    'score': int(score),
                    'category': faq.get('category', 'FAQ'),
                    'question': faq['question'],
                    'answer': faq['answer']
                })
            
            confidence_level = 'HIGH' if suggestions else 'NO_MATCH'
            
        else:
            machine_filter = session.get('machine_filter')
            
            result = bot.get_fuzzy_product_matches(
                query, machine_filter, limit=6, analyze_intent=True
            )
            
            if isinstance(result, tuple) and len(result) == 4:
                products, confidence_level, suggestion_type, analysis = result
                
                send_event_to_dashboard_internal(query, confidence_level)
                
                ga4_event_data = bot.determine_ga4_event(analysis)
                if ga4_event_data:
                    ga4_event = ga4_event_data['event']
                    bot.send_ga4_event(ga4_event_data)
                
                for product, score in products:
                    stock_status = 'available' if product['stock'] > 10 else 'limited' if product['stock'] > 0 else 'out'
                    suggestions.append({
                        'id': product['id'],
                        'text': product['name'],
                        'type': 'product',
                        'score': int(score),
                        'price': f"{product['price']:.2f} zł",
                        'stock': product['stock'],
                        'stock_status': stock_status,
                        'brand': product['brand']
                    })
                
                if confidence_level == 'NO_MATCH':
                    log_lost_demand(query, analysis)
        
        return jsonify({
            'suggestions': suggestions,
            'query': query,
            'confidence_level': confidence_level,
            'ga4_event': ga4_event
        })
    
    except Exception as e:
        print(f"[ERROR] Search suggestions error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'suggestions': [], 'error': str(e)}), 200
    
@app.route('/motobot-prototype/quick-suggestions', methods=['POST'])
def quick_suggestions():
    """FUNKCJA A: Szybkie sugestie + Live Feed (BEZ liczników)"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        search_type = data.get('type', 'products')
        
        if len(query) < 2:
            return jsonify({'suggestions': []})
        
        suggestions = []
        
        if search_type == 'faq':
            faq_results = bot.get_fuzzy_faq_matches(query, limit=5)
            for faq, score in faq_results:
                suggestions.append({
                    'id': faq['id'],
                    'text': faq['question'],
                    'type': 'faq',
                    'score': int(score),
                    'category': faq.get('category', 'FAQ'),
                    'question': faq['question'],
                    'answer': faq['answer']
                })
        else:
            machine_filter = session.get('machine_filter')
            matches = bot.get_fuzzy_product_matches_internal(query, machine_filter)
            
            for product, score in matches[:6]:
                stock_status = 'available' if product['stock'] > 10 else 'limited' if product['stock'] > 0 else 'out'
                suggestions.append({
                    'id': product['id'],
                    'text': product['name'],
                    'type': 'product',
                    'score': int(score),
                    'price': f"{product['price']:.2f} zł",
                    'stock': product['stock'],
                    'stock_status': stock_status,
                    'brand': product['brand']
                })
        
        send_preview_to_dashboard(query, len(suggestions))
        
        return jsonify({
            'suggestions': suggestions,
            'query': query
        })
    
    except Exception as e:
        print(f"[ERROR] Quick suggestions error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'suggestions': [], 'error': str(e)}), 200


@app.route('/motobot-prototype/analyze-and-track', methods=['POST'])
def analyze_and_track():
    """FUNKCJA B: Aktualizacja liczników (BEZ Live Feed)"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        search_type = data.get('type', 'products')
        
        if len(query) < 2:
            return jsonify({'status': 'too_short'})
        
        print(f"[DEEP ANALYSIS] Processing: '{query}'")
        
        machine_filter = session.get('machine_filter')
        
        result = bot.get_fuzzy_product_matches(
            query, machine_filter, limit=6, analyze_intent=True
        )
        
        if isinstance(result, tuple) and len(result) == 4:
            products, confidence_level, suggestion_type, analysis = result
            
            update_dashboard_metrics_only(query, confidence_level)
            
            ga4_event_data = bot.determine_ga4_event(analysis)
            if ga4_event_data:
                bot.send_ga4_event(ga4_event_data)
            
            if confidence_level == 'NO_MATCH':
                log_lost_demand(query, analysis)
            
            print(f"[DEEP ANALYSIS] Result: {confidence_level} for '{query}'")
            
            return jsonify({
                'status': 'analyzed',
                'confidence_level': confidence_level,
                'suggestion_type': suggestion_type,
                'query': query
            })
        else:
            return jsonify({'status': 'no_analysis'})
    
    except Exception as e:
        print(f"[ERROR] Deep analysis error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/initial_data')
def get_initial_data():
    try:
        recent_events = DatabaseManager.get_recent_events(10)
        today_stats = DatabaseManager.get_today_statistics()
        top_missing = DatabaseManager.get_top_missing_products(5)
        
        return jsonify({
            'status': 'success',
            'data': {
                'recent_events': recent_events,
                'today_statistics': today_stats,
                'top_missing_products': top_missing
            }
        })
    except Exception as e:
        print(f"[API ERROR] {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/reset_demo')
def reset_demo():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM events')
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Demo reset successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/receive_event', methods=['POST'])
def receive_real_event():
    try:
        data = request.get_json()
        
        event_id = DatabaseManager.add_event(
            data['query_text'],
            data['decision'],
            data['details'],
            data.get('category', 'unknown'),
            'standard',
            data.get('potential_value', 0),
            f"Prawdziwe zapytanie użytkownika"
        )
        
        event_data = {
            'id': event_id,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'query_text': data['query_text'],
            'decision': data['decision'],
            'details': data['details'],
            'category': data.get('category', 'unknown'),
            'potential_value': data.get('potential_value', 0),
            'explanation': 'Prawdziwe zapytanie użytkownika'
        }
        
        socketio.emit('new_event', event_data)
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/motobot-prototype/report-lost-demand', methods=['POST'])
def report_lost_demand():
    try:
        data = request.get_json()
        query = data.get('query', '')
        email = data.get('email', '')
        notify = data.get('notify', False)
        
        if not os.path.exists(LOST_DEMAND_LOG) or os.path.getsize(LOST_DEMAND_LOG) == 0:
            with open(LOST_DEMAND_LOG, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['timestamp', 'query', 'email', 'notify', 'machine_filter'])
        
        with open(LOST_DEMAND_LOG, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                datetime.now().isoformat(),
                query,
                email,
                notify,
                session.get('machine_filter', 'all')
            ])
        
        ga4_event_data = {
            'event': 'search_lost_demand_confirmed',
            'params': {
                'query': query,
                'email_provided': bool(email),
                'notification_requested': notify,
                'priority': 'CRITICAL'
            }
        }
        bot.send_ga4_event(ga4_event_data)
        
        print(f"[LOST DEMAND] User confirmed: '{query}' | Email: {bool(email)}")
        
        return jsonify({
            'status': 'success',
            'message': 'Dziękujemy! Twoje zgłoszenie pomoże nam ulepszyć ofertę.'
        })
    
    except Exception as e:
        print(f"[ERROR] Report lost demand error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Wystąpił błąd podczas zapisywania zgłoszenia.'
        }), 500

@app.route('/motobot-prototype/track-analytics', methods=['POST'])
def track_analytics():
    try:
        data = request.get_json()
        event_type = data.get('event_type', '')
        event_data = data.get('event_data', {})
        
        ga4_event = {
            'event': event_type,
            'params': event_data
        }
        
        success = bot.send_ga4_event(ga4_event)
        
        return jsonify({
            'status': 'success' if success else 'failed',
            'event_type': event_type
        })
    
    except Exception as e:
        print(f"[ERROR] Track analytics error: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/motobot-prototype/health')
def health_check():
    return jsonify({
        'status': 'OK',
        'service': 'Universal Soldier E-commerce Bot v5.0 FIXED + Dashboard v2',
        'version': '5.0-patient-listener',
        'features': {
            'intent_analysis': True,
            'lost_demand_tracking': True,
            'split_logic': True,
            'live_feed_preview': True,
            'metrics_separation': True
        },
        'session_active': 'cart' in session
    })

# === HELPER FUNCTIONS ===

def send_preview_to_dashboard(query, results_count):
    """Wysyła preview do Live Feed BEZ wpływu na liczniki"""
    try:
        category = extract_category_from_query(query)
        
        event_id = DatabaseManager.add_event(
            query,
            'PREVIEW',
            f'{results_count} sugestii',
            category,
            'standard',
            0,
            'Zapytanie w trakcie pisania'
        )
        
        event_data = {
            'id': event_id,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'query_text': query,
            'decision': 'PREVIEW',
            'details': f'{results_count} sugestii',
            'category': category,
            'potential_value': 0,
            'explanation': 'Zapytanie w trakcie pisania'
        }
        
        socketio.emit('new_event', event_data)
        print(f"[PREVIEW] Sent to Live Feed: {query}")
        
    except Exception as e:
        print(f"[PREVIEW ERROR] {e}")


def update_dashboard_metrics_only(query, confidence_level):
    """Aktualizuje TYLKO liczniki TCD, BEZ Live Feed"""
    try:
        decision_mapping = {
            'HIGH': 'ZNALEZIONE PRODUKTY',
            'MEDIUM': 'ODFILTROWANE', 
            'NO_MATCH': 'UTRACONE OKAZJE',
            'LOW': 'ODFILTROWANE'
        }
        
        decision = decision_mapping.get(confidence_level, 'ZNALEZIONE PRODUKTY')
        category = extract_category_from_query(query)
        potential_value = calculate_lost_value_internal(query) if 'OKAZJE' in decision else 0
        
        metrics_update = {
            'type': 'metrics_update',
            'decision': decision,
            'value': potential_value,
            'query': query
        }
        
        socketio.emit('metrics_update', metrics_update)
        print(f"[METRICS UPDATE] {decision} for '{query}'")
        
    except Exception as e:
        print(f"[METRICS UPDATE ERROR] {e}")


def send_event_to_dashboard_internal(query, confidence_level):
    """LEGACY - zachowane dla kompatybilności"""
    try:
        decision_mapping = {
            'HIGH': 'ZNALEZIONE PRODUKTY',
            'MEDIUM': 'ODFILTROWANE', 
            'NO_MATCH': 'UTRACONE OKAZJE',
            'LOW': 'ODFILTROWANE'
        }
        
        decision = decision_mapping.get(confidence_level, 'ZNALEZIONE PRODUKTY')
        category = extract_category_from_query(query)
        potential_value = calculate_lost_value_internal(query) if 'OKAZJE' in decision else 0
        
        event_id = DatabaseManager.add_event(
            query,
            decision,
            'Integracja z botem',
            category,
            'standard',
            potential_value,
            'Prawdziwe zapytanie z bota'
        )
        
        event_data = {
            'id': event_id,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'query_text': query,
            'decision': decision,
            'details': 'Integracja z botem',
            'category': category,
            'potential_value': potential_value,
            'explanation': 'Prawdziwe zapytanie z bota'
        }
        
        socketio.emit('new_event', event_data)
        print(f"[DASHBOARD INTEGRATION] Sent: {query} -> {decision}")
        
    except Exception as e:
        print(f"[DASHBOARD INTEGRATION ERROR] {e}")

def extract_category_from_query(query):
    query_lower = query.lower()
    categories = ['klocki', 'filtry', 'amortyzatory', 'świece', 'akumulatory', 'oleje', 'tarcze']
    for category in categories:
        if category in query_lower:
            return category
    return 'inne'

def calculate_lost_value_internal(query):
    category = extract_category_from_query(query)
    base_values = {
        'klocki': 200, 'filtry': 80, 'amortyzatory': 450,
        'świece': 50, 'akumulatory': 350, 'oleje': 120
    }
    return base_values.get(category, 150)

def log_lost_demand(query, analysis):
    try:
        if not os.path.exists(LOST_DEMAND_LOG) or os.path.getsize(LOST_DEMAND_LOG) == 0:
            with open(LOST_DEMAND_LOG, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['timestamp', 'query', 'email', 'notify', 'machine_filter'])
        
        with open(LOST_DEMAND_LOG, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                datetime.now().isoformat(),
                query,
                '',
                False,
                session.get('machine_filter', 'all')
            ])
        print(f"[LOST DEMAND AUTO] Logged: '{query}'")
    except Exception as e:
        print(f"[ERROR] Failed to log lost demand: {e}")    
# === WEBSOCKET EVENTS FOR DASHBOARD ===
@socketio.on('connect')
def handle_connect():
    print('[WEBSOCKET] Client connected')
    emit('connection_confirmed', {'message': 'Connected to TCD'})

@socketio.on('disconnect')
def handle_disconnect():
    print('[WEBSOCKET] Client disconnected')

@socketio.on('request_current_stats')
def handle_stats_request():
    try:
        stats = DatabaseManager.get_today_statistics()
        top_missing = DatabaseManager.get_top_missing_products(5)
        
        emit('stats_update', {
            'today_statistics': stats,
            'top_missing_products': top_missing
        })
        
    except Exception as e:
        print(f"[WEBSOCKET ERROR] {e}")
        emit('error', {'message': str(e)})

@socketio.on('pause_simulator')
def handle_pause_simulator():
    simulator.pause_simulator()
    emit('simulator_paused', {'status': 'paused'})

@socketio.on('resume_simulator') 
def handle_resume_simulator():
    simulator.resume_simulator()
    emit('simulator_resumed', {'status': 'resumed'})

# === BATTLE SIMULATOR FUNCTION ===
def battle_simulator():
    print("[SIMULATOR] Battle simulator started")
    
    while simulator.running:
        try:
            time.sleep(random.uniform(6, 8))
            
            if not simulator.running:
                break
            
            if simulator.paused:
                continue
            
            scenario = random.choice(simulator.battle_scenarios)
            
            potential_value = 0
            if scenario['decision'] == 'UTRACONE OKAZJE':
                potential_value = simulator.calculate_lost_value(
                    scenario['category'], 
                    scenario['brand_type']
                )
            
            event_id = DatabaseManager.add_event(
                scenario['query'],
                scenario['decision'],
                scenario['details'],
                scenario['category'],
                scenario['brand_type'],
                potential_value,
                scenario['explanation']
            )
            
            event_data = {
                'id': event_id,
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'query_text': scenario['query'],
                'decision': scenario['decision'],
                'details': scenario['details'],
                'category': scenario['category'],
                'potential_value': potential_value,
                'explanation': scenario['explanation']
            }
            
            socketio.emit('new_event', event_data, namespace='/', broadcast=True)
            
            print(f"[SIMULATOR] Generated: {scenario['query']} -> {scenario['decision']}")
            
        except Exception as e:
            print(f"[SIMULATOR ERROR] {e}")
            time.sleep(1)
    
    print("[SIMULATOR] Battle simulator stopped")

def start_simulator():
    if not simulator.running:
        simulator.running = True
        simulator.thread = threading.Thread(target=battle_simulator, daemon=True)
        simulator.thread.start()

def stop_simulator():
    simulator.running = False
    if simulator.thread and simulator.thread.is_alive():
        simulator.thread.join(timeout=2)

# === MAIN APPLICATION STARTUP ===
if __name__ == '__main__':
    with app.app_context():
        bot.initialize_data()
        DatabaseManager.initialize_database()
        
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            cursor.execute('DELETE FROM events WHERE date(timestamp) < ?', (cutoff_date,))
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            if deleted_count > 0:
                print(f"[DATABASE] Cleared {deleted_count} old events")
        except Exception as e:
            print(f"[DATABASE] Error clearing old events: {e}")
        
        start_simulator()
        
        print("=" * 70)
        print("🎯 STUDIO ADEPT AI - PATIENT LISTENER v2.0")
        print("=" * 70)
        print("🏢 Features:")
        print("   🌐 Wizytówka: /")
        print("   🤖 Motobot: /motobot-prototype")
        print("   📊 Dashboard: /dashboard")
        print("   🎮 Demo: /demo")
        print("=" * 70)
        print("⚡ Quick Search: 100ms → Live Feed")
        print("🎯 Deep Analysis: 800ms → Metrics Only")
        print("=" * 70)
        print("✅ System started!")
        print("=" * 70)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)        
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
    async_mode='eventlet',  # ZMIENIONE z 'threading'
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
            # Średnie ceny według kategorii i marek
            'klocki': {'standard': 150, 'premium': 300, 'luxury': 450},
            'filtry': {'standard': 75, 'premium': 120, 'luxury': 180},
            'amortyzatory': {'standard': 400, 'premium': 650, 'luxury': 950},
            'świece': {'standard': 45, 'premium': 65, 'luxury': 85},
            'akumulatory': {'standard': 350, 'premium': 450, 'luxury': 600},
            'oleje': {'standard': 120, 'premium': 180, 'luxury': 250},
            'tarcze': {'standard': 200, 'premium': 350, 'luxury': 500},
            'łańcuchy': {'standard': 250, 'premium': 350, 'luxury': 450}
        }
        
        # Zapytania demonstracyjne pokazujące przewagę nad no-code
        self.battle_scenarios = [
            # UTRACONY POPYT - Marki luksusowe
            {
                'query': 'klocki ferrari',
                'decision': 'UTRACONE OKAZJE',
                'details': 'Marka Luksusowa',
                'category': 'klocki',
                'brand_type': 'luxury',
                'explanation': 'System rozpoznał markę premium której nie mamy w ofercie'
            },
            {
                'query': 'amortyzatory lamborghini',
                'decision': 'UTRACONE OKAZJE', 
                'details': 'Marka Luksusowa',
                'category': 'amortyzatory',
                'brand_type': 'luxury',
                'explanation': 'Wykryto zapytanie o części do supersamochodu'
            },
            {
                'query': 'części porsche',
                'decision': 'UTRACONE OKAZJE',
                'details': 'Marka Premium',
                'category': 'klocki',
                'brand_type': 'luxury', 
                'explanation': 'Klient szuka części do marki premium'
            },
            
            # UTRACONY POPYT - Nieistniejące kody
            {
                'query': 'klocki bmw n123',
                'decision': 'UTRACONE OKAZJE',
                'details': 'Nieistniejący Kod',
                'category': 'klocki',
                'brand_type': 'premium',
                'explanation': 'Kod produktu nie istnieje w bazie danych'
            },
            {
                'query': 'filtr 0986494999',
                'decision': 'UTRACONE OKAZJE',
                'details': 'Kod OE Nieznaleziony',
                'category': 'filtry',
                'brand_type': 'standard',
                'explanation': 'System nie rozpoznał kodu OE'
            },
            {
                'query': 'amortyzator golf e46',
                'decision': 'UTRACONE OKAZJE',
                'details': 'Model Nieobsługiwany',
                'category': 'amortyzatory',
                'brand_type': 'standard',
                'explanation': 'Kombinacja modelu nie istnieje w ofercie'
            },
            
            # UTRACONY POPYT - Brakujące produkty
            {
                'query': 'opony zimowe',
                'decision': 'UTRACONE OKAZJE',
                'details': 'Brak Kategorii',
                'category': 'opony',
                'brand_type': 'standard',
                'explanation': 'Nie obsługujemy kategorii opon'
            },
            {
                'query': 'felgi aluminiowe',
                'decision': 'UTRACONE OKAZJE',
                'details': 'Kategoria Niedostępna', 
                'category': 'felgi',
                'brand_type': 'standard',
                'explanation': 'Felgi nie są w naszej ofercie'
            },
            
            # KOREKTA LITERÓWKI - Demonstracja inteligencji
            {
                'query': 'kloki bosh',
                'decision': 'ODFILTROWANE',
                'details': 'klocki Bosch',
                'category': 'klocki',
                'brand_type': 'standard',
                'explanation': 'System poprawił błąd pisowni i znalazł produkt'
            },
            {
                'query': 'filetr man',
                'decision': 'ODFILTROWANE',
                'details': 'filtr Mann',
                'category': 'filtry',
                'brand_type': 'standard',
                'explanation': 'Automatyczna korekta literówki'
            },
            {
                'query': 'amortyztor bilsten',
                'decision': 'ODFILTROWANE',
                'details': 'amortyzator Bilstein',
                'category': 'amortyzatory',
                'brand_type': 'premium',
                'explanation': 'Podwójna korekta: kategoria + marka'
            },
            {
                'query': 'swice ngk',
                'decision': 'ODFILTROWANE',
                'details': 'świece NGK',
                'category': 'świece',
                'brand_type': 'standard',
                'explanation': 'Korekta polskich znaków diakrytycznych'
            },
            
            
            # PRECYZYJNE TRAFIENIA - Pokazanie sukcesu
            {
                'query': 'klocki bosch',
                'decision': 'ZNALEZIONE PRODUKTY',
                'details': 'Znaleziono Produkt',
                'category': 'klocki',
                'brand_type': 'standard',
                'explanation': 'Dokładne dopasowanie marki i kategorii'
            },
            {
                'query': 'filtr mann bmw',
                'decision': 'ZNALEZIONE PRODUKTY',
                'details': 'Dopasowanie Marki+Model',
                'category': 'filtry',
                'brand_type': 'standard',
                'explanation': 'System znalazł filter Mann do BMW'
            },
            {
                'query': 'amortyzator bilstein golf',
                'decision': 'ZNALEZIONE PRODUKTY',
                'details': 'Pełne Dopasowanie',
                'category': 'amortyzatory',
                'brand_type': 'premium',
                'explanation': 'Wszystkie parametry znalezione w bazie'
            },
            {
                'query': 'olej castrol 5w30',
                'decision': 'ZNALEZIONE PRODUKTY',
                'details': 'Specyfikacja Techniczna',
                'category': 'oleje',
                'brand_type': 'premium',
                'explanation': 'System rozpoznał dokładną specyfikację oleju'
            },
            {
                'query': 'filtr 0986494104',
                'decision': 'ZNALEZIONE PRODUKTY',
                'details': 'Kod OE Rozpoznany',
                'category': 'filtry',
                'brand_type': 'standard',
                'explanation': 'Znaleziono produkt po kodzie producenta'
            },
            {
                'query': 'klocki yamaha r6',
                'decision': 'ZNALEZIONE PRODUKTY',
                'details': 'Motocykl Sportowy',
                'category': 'klocki',
                'brand_type': 'premium',
                'explanation': 'System rozpoznał części motocyklowe'
            },
            # BŁĘDY WYSZUKIWANIA - Demonstracja inteligencji
{
    'query': 'asdasdasd',
    'decision': 'ODFILTROWANE',
    'details': 'Nonsensowne zapytanie',
    'category': 'inne',
    'brand_type': 'standard',
    'explanation': 'System rozpoznał nonsensowne zapytanie'
},
{
    'query': 'qwerty123',
    'decision': 'ODFILTROWANE',
    'details': 'Wzorzec klawiaturowy',
    'category': 'inne',
    'brand_type': 'standard',
    'explanation': 'Wykryto wzorzec klawiaturowy'
},
{
    'query': 'xyzxyzxyz',
    'decision': 'ODFILTROWANE',
    'details': 'Powtarzający się wzorzec',
    'category': 'inne',
    'brand_type': 'standard',
    'explanation': 'Powtarzające się sekwencje znaków'
},
{
    'query': 'hjklhjkl',
    'decision': 'ODFILTROWANE',
    'details': 'Losowe znaki',
    'category': 'inne',
    'brand_type': 'standard',
    'explanation': 'Brak sensownej struktury językowej'
}
            
            
        ]
        
        self.running = False
        self.paused = False
        self.thread = None
        
    def calculate_lost_value(self, category, brand_type):
        """Oblicza szacowaną wartość utraconego popytu"""
        if category not in self.price_ranges:
            return random.randint(100, 300)
        
        base_price = self.price_ranges[category][brand_type]
        # Dodaj losową wariację ±20%
        variation = random.uniform(0.8, 1.2)
        return int(base_price * variation)
    
    def pause_simulator(self):
        """Pauzuje symulator"""
        self.paused = True
        print("[SIMULATOR] Paused by user interaction")

    def resume_simulator(self):
        """Wznawia symulator"""
        self.paused = False
        print("[SIMULATOR] Resumed by user interaction")

class DatabaseManager:
    """Zarządza bazą danych SQLite dla dashboardu"""
    
    @staticmethod
    def initialize_database():
        """Tworzy tabelę events jeśli nie istnieje"""
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
        
        # Dodaj indeksy dla wydajności
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_decision ON events(decision)')
        
        conn.commit()
        conn.close()
        print("[DATABASE] Events table initialized")
    
    @staticmethod
    def add_event(query_text, decision, details, category, brand_type, potential_value, explanation):
        """Dodaje nowe zdarzenie do bazy"""
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
        """Pobiera ostatnie wydarzenia"""
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
        """Pobiera statystyki z dzisiejszego dnia"""
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Zlicz wydarzenia według typu decyzji
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
        """Pobiera najczęściej poszukiwane brakujące produkty"""
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Ostatnie 7 dni, tylko UTRACONY POPYT
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

# Globalny symulator
simulator = TacticalDataSimulator()

# === KONIEC CZĘŚCI 1 ===
# === CZĘŚĆ 2/3: FLASK ROUTES ===
# (kontynuacja po części 1)

# === WIZYTÓWKA ROUTES ===
@app.route('/')
def home():
    """Main landing page - wizytówka"""
    return render_template('index.html')
    
@app.route('/demo-motobot.html')
def demo_motobot():
    """Demo page with iframe to motobot"""
    return render_template('demo-motobot.html')

# === BOT E-COMMERCE ROUTES ===
@app.route('/motobot-prototype')
def motobot_index():
    """Main page of motobot with bot interface"""
    return render_template('demo_page.html')

@app.route('/demo')
def demo_page():
    """Demo page with bot and dashboard split screen"""
    return render_template('demo_page.html')

@app.route('/motobot-prototype/bot/start', methods=['POST'])
def bot_start():
    """Initialize bot session"""
    try:
        session.permanent = True
        session['cart'] = []
        session['context'] = None
        session['machine_filter'] = None
        
        # Get initial greeting
        initial_response = bot.get_initial_greeting()
        
        return jsonify({'reply': initial_response})
    
    except Exception as e:
        print(f"[ERROR] Bot start error: {e}")
        return jsonify({
            'reply': {
                'text_message': f'Wystąpił błąd podczas inicjalizacji: {str(e)}',
                'buttons': [
                    {'text': 'Spróbuj ponownie', 'action': 'restart'}
                ]
            }
        }), 500

@app.route('/motobot-prototype/bot/send', methods=['POST'])
def bot_send():
    """Handle user messages with intelligent intent analysis + dashboard integration"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        button_action = data.get('button_action', '')
        
        print(f"[DEBUG] Message: {user_message}, Action: {button_action}")
        
        # Process button action or text message
        if button_action:
            reply = bot.handle_button_action(button_action)
        elif user_message:
            # NOWA INTEGRACJA - dodaj dane do dashboardu
            reply = bot.process_message(user_message)
            
            # Wyślij event do dashboardu jeśli bot ma confidence_level
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
                'buttons': [
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }
        }), 500

@app.route('/motobot-prototype/search-suggestions', methods=['POST'])
def search_suggestions():
    """Real-time search suggestions with intelligent analysis + dashboard integration"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        search_type = data.get('type', 'products')
        
        # Minimum 2 characters to search
        if len(query) < 2:
            return jsonify({'suggestions': [], 'confidence_level': 'NONE'})
        
        suggestions = []
        confidence_level = 'HIGH'
        ga4_event = None
        
        if search_type == 'faq':
            # FAQ search
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
            # Search products with intent analysis
            machine_filter = session.get('machine_filter')
            
            result = bot.get_fuzzy_product_matches(
                query, machine_filter, limit=6, analyze_intent=True
            )
            
            if isinstance(result, tuple) and len(result) == 4:
                # New format with analysis
                products, confidence_level, suggestion_type, analysis = result
                
                # NOWA INTEGRACJA - Wyślij do dashboardu
                send_event_to_dashboard_internal(query, confidence_level)
                
                # Determine GA4 event
                ga4_event_data = bot.determine_ga4_event(analysis)
                if ga4_event_data:
                    ga4_event = ga4_event_data['event']
                    bot.send_ga4_event(ga4_event_data)
                
                # Prepare suggestions
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
                
                # Log lost demand if needed
                if confidence_level == 'NO_MATCH':
                    log_lost_demand(query, analysis)
        
        print(f"[SUGGESTIONS] Query: '{query}' | Type: {search_type} | Confidence: {confidence_level} | GA4: {ga4_event}")
        
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

# === DASHBOARD API ROUTES ===
@app.route('/dashboard')
def dashboard():
    """Główna strona dashboardu"""
    return render_template('dashboard.html')

@app.route('/api/initial_data')
def get_initial_data():
    """API endpoint zwracający dane inicjalne dla dashboardu"""
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
    """Resetuje demo - czyści bazę i restartuje symulację"""
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
    """Odbiera prawdziwe eventy z bota (dla integracji)"""
    try:
        data = request.get_json()
        
        # Dodaj do bazy
        event_id = DatabaseManager.add_event(
            data['query_text'],
            data['decision'],
            data['details'],
            data.get('category', 'unknown'),
            'standard',  # brand_type
            data.get('potential_value', 0),
            f"Prawdziwe zapytanie użytkownika"
        )
        
        # Wyślij przez WebSocket
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

# === POZOSTAŁE ROUTES Z ORYGINALNEGO APP.PY ===
@app.route('/motobot-prototype/report-lost-demand', methods=['POST'])
def report_lost_demand():
    """Endpoint to collect and save lost demand reports"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        email = data.get('email', '')
        notify = data.get('notify', False)
        
        # Initialize CSV with headers if needed
        if not os.path.exists(LOST_DEMAND_LOG) or os.path.getsize(LOST_DEMAND_LOG) == 0:
            with open(LOST_DEMAND_LOG, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['timestamp', 'query', 'email', 'notify', 'machine_filter'])
        
        # Log to CSV file
        with open(LOST_DEMAND_LOG, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                datetime.now().isoformat(),
                query,
                email,
                notify,
                session.get('machine_filter', 'all')
            ])
        
        # Send special GA4 event
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
    """Universal endpoint for tracking various analytics events"""
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
    """Health check endpoint with system status"""
    return jsonify({
        'status': 'OK',
        'service': 'Universal Soldier E-commerce Bot v5.0 FIXED + Dashboard',
        'version': '5.0-fixed-dashboard',
        'features': {
            'intent_analysis': True,
            'lost_demand_tracking': True,
            'typo_correction': True,
            'confidence_scoring': True,
            'luxury_brand_detection': True,
            'precision_reward': True,
            'dashboard_integration': True,
            'real_time_websocket': True
        },
        'session_active': 'cart' in session
    })

# === HELPER FUNCTIONS ===
def send_event_to_dashboard_internal(query, confidence_level):
    """Wewnętrzna funkcja wysyłania eventów do dashboardu"""
    try:
        # NAPRAWIONE MAPOWANIE - nowe 3 kategorie
        decision_mapping = {
            'HIGH': 'ZNALEZIONE PRODUKTY',
            'MEDIUM': 'ODFILTROWANE', 
            'NO_MATCH': 'UTRACONE OKAZJE',
            'LOW': 'ODFILTROWANE'
        }
        
        decision = decision_mapping.get(confidence_level, 'ZNALEZIONE PRODUKTY')
        category = extract_category_from_query(query)
        potential_value = calculate_lost_value_internal(query) if 'OKAZJE' in decision else 0
        
        # Dodaj do bazy danych
        event_id = DatabaseManager.add_event(
            query,
            decision,
            'Integracja z botem',
            category,
            'standard',
            potential_value,
            'Prawdziwe zapytanie z bota'
        )
        
        # Wyślij przez WebSocket
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
    """Wyciąga kategorię z zapytania"""
    query_lower = query.lower()
    categories = ['klocki', 'filtry', 'amortyzatory', 'świece', 'akumulatory', 'oleje', 'tarcze']
    for category in categories:
        if category in query_lower:
            return category
    return 'inne'

def calculate_lost_value_internal(query):
    """Szacuje wartość utraconego popytu"""
    category = extract_category_from_query(query)
    base_values = {
        'klocki': 200, 'filtry': 80, 'amortyzatory': 450,
        'świece': 50, 'akumulatory': 350, 'oleje': 120
    }
    return base_values.get(category, 150)

def log_lost_demand(query, analysis):
    """Helper function to log lost demand"""
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

# === KONIEC CZĘŚCI 2 ===

# === CZĘŚĆ 3/3: WEBSOCKET EVENTS + SYMULATOR + MAIN ===
# (kontynuacja po części 2)

# === DEBUG ROUTES (only for development) ===
@app.route('/motobot-prototype/debug/test-intent-analysis')
def test_intent_analysis():
    """Debug endpoint for testing intent analysis"""
    if app.debug:
        test_queries = [
            "klocki golf",
            "kloki glof", 
            "klocki xyzz",
            "xyza123",
            "opony zimowe",
            "amortyzator ferrari",
            "filtr mann bmw",
            "amortyztor bilsten"
        ]
        
        results = {}
        for query in test_queries:
            analysis = bot.analyze_query_intent(query)
            results[query] = {
                'confidence_level': analysis['confidence_level'],
                'suggestion_type': analysis['suggestion_type'],
                'token_validity': analysis['token_validity'],
                'best_match_score': analysis['best_match_score'],
                'ga4_event': analysis['ga4_event'],
                'has_luxury': analysis.get('has_luxury_brand', False)
            }
        
        return jsonify({
            'test': 'Intent Analysis Test - FIXED VERSION + Dashboard',
            'results': results,
            'interpretation': {
                'HIGH': 'Show normal results',
                'MEDIUM': 'Show "Did you mean..." (typo)',
                'LOW': 'Show "We don\'t understand" (nonsense)',
                'NO_MATCH': 'Show "Product not in catalog" (LOST DEMAND!)'
            }
        })
    return jsonify({'error': 'Available only in debug mode'}), 403

@app.route('/motobot-prototype/debug/lost-demand-report')
def lost_demand_report():
    """Debug endpoint to view lost demand log"""
    if app.debug:
        try:
            lost_demands = []
            if os.path.exists(LOST_DEMAND_LOG):
                with open(LOST_DEMAND_LOG, 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader, None)
                    for row in reader:
                        if len(row) >= 5:
                            lost_demands.append({
                                'timestamp': row[0],
                                'query': row[1],
                                'email': row[2],
                                'notify': row[3],
                                'machine_filter': row[4]
                            })
            
            # Group by query for summary
            query_counts = {}
            for demand in lost_demands:
                query = demand['query'].lower()
                query_counts[query] = query_counts.get(query, 0) + 1
            
            top_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return jsonify({
                'total_lost_demands': len(lost_demands),
                'unique_queries': len(query_counts),
                'recent_demands': lost_demands[-10:] if lost_demands else [],
                'top_missing_products': top_queries
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Available only in debug mode'}), 403

# === WEBSOCKET EVENTS FOR DASHBOARD ===
@socketio.on('connect')
def handle_connect():
    """Klient podłączył się do WebSocket"""
    print('[WEBSOCKET] Client connected')
    emit('connection_confirmed', {'message': 'Connected to TCD'})

@socketio.on('disconnect')
def handle_disconnect():
    """Klient rozłączył się z WebSocket""" 
    print('[WEBSOCKET] Client disconnected')

@socketio.on('request_current_stats')
def handle_stats_request():
    """Klient prosi o aktualne statystyki"""
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
    """Pauzuje symulator na żądanie klienta"""
    simulator.pause_simulator()
    emit('simulator_paused', {'status': 'paused'})

@socketio.on('resume_simulator') 
def handle_resume_simulator():
    """Wznawia symulator na żądanie klienta"""
    simulator.resume_simulator()
    emit('simulator_resumed', {'status': 'resumed'})

# === BATTLE SIMULATOR FUNCTION ===
def battle_simulator():
    """Główna pętla symulatora - działa w osobnym wątku"""
    print("[SIMULATOR] Battle simulator started")
    
    while simulator.running:
        try:
            # Losowy interwał 2-5 sekund
            time.sleep(random.uniform(6, 8))
            
            if not simulator.running:
                break
            
            # Sprawdź czy symulator jest wstrzymany
            if simulator.paused:
                continue
            
            # Wybierz losowe zdarzenie
            scenario = random.choice(simulator.battle_scenarios)
            
            # Oblicz wartość jeśli to utracony popyt
            potential_value = 0
            if scenario['decision'] == 'UTRACONE OKAZJE':
                potential_value = simulator.calculate_lost_value(
                    scenario['category'], 
                    scenario['brand_type']
                )
            
            # Dodaj do bazy danych
            event_id = DatabaseManager.add_event(
                scenario['query'],
                scenario['decision'],
                scenario['details'],
                scenario['category'],
                scenario['brand_type'],
                potential_value,
                scenario['explanation']
            )
            
            # Przygotuj dane dla WebSocket
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
            
            # Wyślij przez WebSocket do wszystkich klientów
            socketio.emit('new_event', event_data, namespace='/', broadcast=True)
            
            print(f"[SIMULATOR] Generated: {scenario['query']} -> {scenario['decision']}")
            
        except Exception as e:
            print(f"[SIMULATOR ERROR] {e}")
            time.sleep(1)
    
    print("[SIMULATOR] Battle simulator stopped")

def start_simulator():
    """Uruchamia symulator w osobnym wątku"""
    if not simulator.running:
        simulator.running = True
        simulator.thread = threading.Thread(target=battle_simulator, daemon=True)
        simulator.thread.start()

def stop_simulator():
    """Zatrzymuje symulator"""
    simulator.running = False
    if simulator.thread and simulator.thread.is_alive():
        simulator.thread.join(timeout=2)

# === MAIN APPLICATION STARTUP ===

    with app.app_context():
        # Initialize bot data
        bot.initialize_data()
        
        # Initialize dashboard database
        DatabaseManager.initialize_database()
        
        # Clear old events (older than 30 days)
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
        
        # Start battle simulator
        start_simulator()
        
        print("=" * 70)
        print("🎯 STUDIO ADEPT AI - UNIFIED APPLICATION + DASHBOARD")
        print("=" * 70)
        print("🏢 Features enabled:")
        print("   🌐 Wizytówka: /")
        print("   🤖 Motobot: /motobot-prototype")
        print("   📊 Dashboard: /dashboard")
        print("   🎮 Demo (Bot + Dashboard): /demo")
        print("=" * 70)
        print("✅ Unified system started!")
        print("=" * 70)
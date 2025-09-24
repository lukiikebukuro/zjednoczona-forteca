from flask import Flask, render_template, request, jsonify, session
from datetime import timedelta
from ecommerce_bot import EcommerceBot
import os
import requests
import uuid
import json
import csv
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'universal_soldier_kramp_2024_v2')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Session configuration
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_PERMANENT'] = False

# Initialize bot
bot = EcommerceBot()

# Lost demand log file
LOST_DEMAND_LOG = 'lost_demand_log.csv'

@app.route('/')
def index():
    """Main page with bot interface"""
    return render_template('index.html')

@app.route('/bot/start', methods=['POST'])
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

@app.route('/bot/send', methods=['POST'])
def bot_send():
    """Handle user messages with intelligent intent analysis"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        button_action = data.get('button_action', '')
        
        print(f"[DEBUG] Message: {user_message}, Action: {button_action}")
        
        # Process button action or text message
        if button_action:
            reply = bot.handle_button_action(button_action)
        elif user_message:
            reply = bot.process_message(user_message)
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

@app.route('/search-suggestions', methods=['POST'])
def search_suggestions():
    """NAPRAWIONE - Real-time search suggestions with intelligent analysis"""
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
            # NAPRAWIONE FAQ - poprawne pola
            faq_results = bot.get_fuzzy_faq_matches(query, limit=5)
            for faq, score in faq_results:
                suggestions.append({
                    'id': faq['id'],
                    'text': faq['question'],  # WAŻNE: pole 'text' używane w JS
                    'type': 'faq',
                    'score': int(score),
                    'category': faq.get('category', 'FAQ'),
                    'question': faq['question'],  # Dodatkowe pole dla kompatybilności
                    'answer': faq['answer']
                })
            
            # FAQ nie wymaga analizy intencji
            confidence_level = 'HIGH' if suggestions else 'NO_MATCH'
            
        else:
            # Search products with intent analysis
            machine_filter = session.get('machine_filter')
            
            # Use new function with intent analysis
            result = bot.get_fuzzy_product_matches(
                query, machine_filter, limit=6, analyze_intent=True
            )
            
            if isinstance(result, tuple) and len(result) == 4:
                # New format with analysis
                products, confidence_level, suggestion_type, analysis = result
                
                # Determine GA4 event
                ga4_event_data = bot.determine_ga4_event(analysis)
                if ga4_event_data:
                    ga4_event = ga4_event_data['event']
                    # Send GA4 event
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
            
            else:
                # Old format for backward compatibility
                for product, score in result[:6]:
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
        
        # Debugging output
        print(f"[SUGGESTIONS] Query: '{query}' | Type: {search_type} | Confidence: {confidence_level} | GA4: {ga4_event}")
        if search_type == 'faq' and suggestions:
            print(f"  FAQ found: {len(suggestions)} results")
        
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

@app.route('/report-lost-demand', methods=['POST'])
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
        
        # Send special GA4 event for user-confirmed lost demand
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

@app.route('/track-analytics', methods=['POST'])
def track_analytics():
    """Universal endpoint for tracking various analytics events"""
    try:
        data = request.get_json()
        event_type = data.get('event_type', '')
        event_data = data.get('event_data', {})
        
        # Prepare GA4 event
        ga4_event = {
            'event': event_type,
            'params': event_data
        }
        
        # Send to GA4
        success = bot.send_ga4_event(ga4_event)
        
        return jsonify({
            'status': 'success' if success else 'failed',
            'event_type': event_type
        })
    
    except Exception as e:
        print(f"[ERROR] Track analytics error: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint with system status"""
    return jsonify({
        'status': 'OK',
        'service': 'Universal Soldier E-commerce Bot v5.0 FIXED',
        'version': '5.0-fixed',
        'features': {
            'intent_analysis': True,
            'lost_demand_tracking': True,
            'typo_correction': True,
            'confidence_scoring': True,
            'luxury_brand_detection': True,
            'precision_reward': True
        },
        'session_active': 'cart' in session
    })

@app.route('/debug/test-intent-analysis')
def test_intent_analysis():
    """Debug endpoint for testing intent analysis"""
    if app.debug:
        test_queries = [
            "klocki golf",           # High confidence - correct
            "kloki glof",           # Medium confidence - typo
            "klocki xyzz",          # NO_MATCH - sensowne słowo + nonsens
            "xyza123",              # Low confidence - pure nonsense
            "opony zimowe",         # NO_MATCH - missing product
            "amortyzator ferrari",  # NO_MATCH - luxury brand missing
            "filtr mann bmw",       # High confidence
            "amortyztor bilsten"    # Medium confidence - typo
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
            'test': 'Intent Analysis Test - FIXED VERSION',
            'results': results,
            'interpretation': {
                'HIGH': 'Show normal results',
                'MEDIUM': 'Show "Did you mean..." (typo)',
                'LOW': 'Show "We don\'t understand" (nonsense)',
                'NO_MATCH': 'Show "Product not in catalog" (LOST DEMAND!)'
            }
        })
    return jsonify({'error': 'Available only in debug mode'}), 403

@app.route('/debug/lost-demand-report')
def lost_demand_report():
    """Debug endpoint to view lost demand log"""
    if app.debug:
        try:
            lost_demands = []
            if os.path.exists(LOST_DEMAND_LOG):
                with open(LOST_DEMAND_LOG, 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader, None)  # Skip header if exists
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
                if query in query_counts:
                    query_counts[query] += 1
                else:
                    query_counts[query] = 1
            
            # Sort by frequency
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

def log_lost_demand(query, analysis):
    """Helper function to log lost demand"""
    try:
        # Initialize CSV with headers if needed
        if not os.path.exists(LOST_DEMAND_LOG) or os.path.getsize(LOST_DEMAND_LOG) == 0:
            with open(LOST_DEMAND_LOG, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['timestamp', 'query', 'email', 'notify', 'machine_filter'])
        
        with open(LOST_DEMAND_LOG, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                datetime.now().isoformat(),
                query,
                '',  # No email at this point
                False,  # No notification request yet
                session.get('machine_filter', 'all')
            ])
        print(f"[LOST DEMAND AUTO] Logged: '{query}'")
    except Exception as e:
        print(f"[ERROR] Failed to log lost demand: {e}")

if __name__ == '__main__':
    with app.app_context():
        # Initialize bot data
        bot.initialize_data()
        print("=" * 60)
        print("🛒 UNIVERSAL SOLDIER E-COMMERCE BOT v5.0 FIXED")
        print("🎯 Intelligent Intent Analysis System - CALIBRATED")
        print("📊 Lost Demand Tracking - PRECISION MODE")
        print("🔍 Confidence Scoring - FIXED THRESHOLDS")
        print("🏎️ Luxury Brand Detection - ACTIVE")
        print("✨ Precision Reward System - ENABLED")
        print("=" * 60)
        print("✅ System uruchomiony!")
        print("📍 Dostępny pod: http://localhost:5000")
        print("🔧 Debug - Intent Analysis: http://localhost:5000/debug/test-intent-analysis")
        print("📈 Debug - Lost Demand: http://localhost:5000/debug/lost-demand-report")
        print("=" * 60)
    
    app.run(debug=True, port=5000)
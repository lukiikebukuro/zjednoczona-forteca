from flask import Flask, render_template, request, jsonify, session
from datetime import timedelta
from ecommerce_bot import EcommerceBot
import os
import requests
import uuid

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
    """Handle user messages"""
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
    """Real-time search suggestions with fuzzy matching"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        search_type = data.get('type', 'products')  # 'products' or 'faq'
        
        # Minimum 2 characters to search
        if len(query) < 2:
            return jsonify({'suggestions': []})
        
        suggestions = []
        
        if search_type == 'faq':
            # Search FAQ with fuzzy matching
            faq_results = bot.get_fuzzy_faq_matches(query, limit=5)
            for faq, score in faq_results:
                suggestions.append({
                    'id': faq['id'],
                    'text': faq['question'],
                    'type': 'faq',
                    'score': score,
                    'category': faq.get('category', 'FAQ')
                })
        else:
            # Search products with fuzzy matching
            machine_filter = session.get('machine_filter')
            product_results = bot.get_fuzzy_product_matches(query, machine_filter, limit=6)
            for product, score in product_results:
                stock_status = 'available' if product['stock'] > 10 else 'limited' if product['stock'] > 0 else 'out'
                suggestions.append({
                    'id': product['id'],
                    'text': product['name'],
                    'type': 'product',
                    'score': score,
                    'price': f"{product['price']:.2f} zł",
                    'stock': product['stock'],
                    'stock_status': stock_status,
                    'brand': product['brand']
                })
        
        return jsonify({
            'suggestions': suggestions,
            'query': query
        })
    
    except Exception as e:
        print(f"[ERROR] Search suggestions error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'suggestions': [], 'error': str(e)}), 200


@app.route('/track-no-results', methods=['POST'])
def track_no_results():
    """Send no results event to GA4 Measurement Protocol"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        search_type = data.get('search_type', 'products')
        
        # Only track if query length > 2
        if len(query.strip()) <= 2:
            return jsonify({'status': 'skipped', 'reason': 'query too short'}), 200
        
        # Send to GA4 Measurement Protocol
        ga4_success = bot.send_ga4_no_results_event(query, search_type)
        
        return jsonify({
            'status': 'success' if ga4_success else 'partial_success',
            'ga4_sent': ga4_success,
            'query': query,
            'search_type': search_type
        })
    
    except Exception as e:
        print(f"[ERROR] Track no results error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'service': 'Universal Soldier E-commerce Bot v2.0',
        'version': '2.0',
        'company': 'Kramp Demo',
        'session_active': 'cart' in session
    })

@app.route('/debug/session')
def debug_session():
    """Debug endpoint for session data"""
    if app.debug:
        return jsonify({
            'session_data': dict(session),
            'cart': session.get('cart', []),
            'context': session.get('context', None),
            'machine_filter': session.get('machine_filter', None)
        })
    return jsonify({'error': 'Available only in debug mode'}), 403

if __name__ == '__main__':
    with app.app_context():
        # Initialize bot data
        bot.initialize_data()
        print("=" * 60)
        print("🛒 UNIVERSAL SOLDIER E-COMMERCE BOT v2.0")
        print("🚜 Kramp - Inteligentny Asystent Części Zamiennych")
        print("=" * 60)
        print("✅ System uruchomiony!")
        print("📍 Dostępny pod: http://localhost:5000")
        print("🔧 Debug: http://localhost:5000/debug/session")
        print("=" * 60)
    
    app.run(debug=True, port=5000)
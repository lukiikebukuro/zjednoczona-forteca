"""
Uniwersalny Żołnierz - Silnik bota e-commerce v3.0
Prototyp dla branży motoryzacyjnej z inteligentnym wyszukiwaniem i fuzzy matching
"""
import json
import os
from flask import session
from datetime import datetime
import random
import re
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz, process


class EcommerceBot:
    def __init__(self):
        self.product_database = {}
        self.faq_database = {}
        self.orders_database = {}
        self.current_context = None
        self.initialize_data()
    
    def initialize_data(self):
        """Inicjalizuje bazę danych dla branży motoryzacyjnej"""
        
        # Baza produktów motoryzacyjnych
        self.product_database = {
            'products': [
                # Klocki hamulcowe
                {'id': 'KH001', 'name': 'Klocki hamulcowe przód Bosch BMW E90', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'Bosch', 'model': '0986494104', 'price': 189.00, 'stock': 45},
                {'id': 'KH002', 'name': 'Klocki hamulcowe tył ATE Mercedes W204', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'ATE', 'model': '13.0460-7218', 'price': 156.00, 'stock': 38},
                {'id': 'KH003', 'name': 'Klocki hamulcowe Ferodo Audi A4 B8', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'Ferodo', 'model': 'FDB4050', 'price': 245.00, 'stock': 22},
                
                # Tarcze hamulcowe
                {'id': 'TH001', 'name': 'Tarcza hamulcowa przednia Brembo 320mm', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'Brembo', 'model': '09.9772.11', 'price': 420.00, 'stock': 18},
                {'id': 'TH002', 'name': 'Tarcza hamulcowa tylna ATE 300mm', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'ATE', 'model': '24.0330-0184', 'price': 285.00, 'stock': 25},
                
                # Filtry
                {'id': 'FO001', 'name': 'Filtr oleju Mann HU719/7x BMW', 'category': 'filtry', 'machine': 'osobowy', 'brand': 'Mann', 'model': 'HU719/7x', 'price': 62.00, 'stock': 120},
                {'id': 'FP001', 'name': 'Filtr paliwa Bosch diesel PSA', 'category': 'filtry', 'machine': 'osobowy', 'brand': 'Bosch', 'model': 'F026402836', 'price': 89.00, 'stock': 85},
                {'id': 'FA001', 'name': 'Filtr powietrza K&N sportowy uniwersalny', 'category': 'filtry', 'machine': 'uniwersalny', 'brand': 'K&N', 'model': '33-2990', 'price': 285.00, 'stock': 35},
                {'id': 'FK001', 'name': 'Filtr kabinowy węglowy Mann CUK2939', 'category': 'filtry', 'machine': 'osobowy', 'brand': 'Mann', 'model': 'CUK2939', 'price': 95.00, 'stock': 68},
                
                # Amortyzatory
                {'id': 'AM001', 'name': 'Amortyzator przód Bilstein B4 VW Golf VII', 'category': 'zawieszenie', 'machine': 'osobowy', 'brand': 'Bilstein', 'model': '22-266767', 'price': 520.00, 'stock': 15},
                {'id': 'AM002', 'name': 'Amortyzator tył KYB Excel-G Ford Focus MK3', 'category': 'zawieszenie', 'machine': 'osobowy', 'brand': 'KYB', 'model': '349034', 'price': 385.00, 'stock': 24},
                {'id': 'AM003', 'name': 'Amortyzator przód Sachs Opel Astra J', 'category': 'zawieszenie', 'machine': 'osobowy', 'brand': 'Sachs', 'model': '314896', 'price': 425.00, 'stock': 19},
                
                # Świece zapłonowe
                {'id': 'SZ001', 'name': 'Świeca zapłonowa NGK Laser Iridium', 'category': 'zapłon', 'machine': 'osobowy', 'brand': 'NGK', 'model': 'ILZKR7B11', 'price': 45.00, 'stock': 280},
                {'id': 'SZ002', 'name': 'Świeca zapłonowa Bosch Platinum Plus', 'category': 'zapłon', 'machine': 'osobowy', 'brand': 'Bosch', 'model': 'FR7DPP33', 'price': 38.00, 'stock': 320},
                {'id': 'SZ003', 'name': 'Świeca żarowa Beru PSG diesel', 'category': 'zapłon', 'machine': 'osobowy', 'brand': 'Beru', 'model': 'PSG006', 'price': 78.00, 'stock': 145},
                
                # Akumulatory
                {'id': 'AK001', 'name': 'Akumulator Varta Blue 74Ah 680A', 'category': 'elektryka', 'machine': 'osobowy', 'brand': 'Varta', 'model': 'E12', 'price': 420.00, 'stock': 38},
                {'id': 'AK002', 'name': 'Akumulator Bosch S4 60Ah 540A', 'category': 'elektryka', 'machine': 'osobowy', 'brand': 'Bosch', 'model': 'S4005', 'price': 350.00, 'stock': 45},
                
                # Oleje silnikowe
                {'id': 'OL001', 'name': 'Olej silnikowy Castrol Edge 5W30 5L', 'category': 'oleje', 'machine': 'osobowy', 'brand': 'Castrol', 'model': 'Edge 5W30', 'price': 165.00, 'stock': 92},
                {'id': 'OL002', 'name': 'Olej silnikowy Mobil 1 0W40 4L', 'category': 'oleje', 'machine': 'osobowy', 'brand': 'Mobil', 'model': 'ESP 0W40', 'price': 189.00, 'stock': 78},
                {'id': 'OL003', 'name': 'Olej silnikowy Shell Helix Ultra 5W40 5L', 'category': 'oleje', 'machine': 'osobowy', 'brand': 'Shell', 'model': 'Helix Ultra', 'price': 145.00, 'stock': 110}
            ],
            'categories': {
                'hamulce': '🔧 Układ hamulcowy',
                'filtry': '🔍 Filtry',
                'zawieszenie': '🚗 Zawieszenie',
                'zapłon': '⚡ Układ zapłonowy',
                'elektryka': '🔋 Elektryka',
                'oleje': '🛢️ Oleje i płyny'
            },
            'machines': {
                'osobowy': '🚗 Samochód osobowy',
                'dostawczy': '🚐 Samochód dostawczy',
                'ciężarowy': '🚚 Samochód ciężarowy',
                'motocykl': '🏍️ Motocykl',
                'uniwersalny': '🔧 Uniwersalne'
            }
        }
        
        # FAQ dla branży motoryzacyjnej
        self.faq_database = [
            {
                'id': 'FAQ001',
                'keywords': ['dostawa', 'wysyłka', 'kiedy', 'czas dostawy', 'przesyłka', 'kurier', 'odbiór'],
                'question': 'Jaki jest czas dostawy części samochodowych?',
                'answer': '🚚 **Opcje dostawy:**\n\n• **Dostawa kurierem:** 24h dla produktów na stanie\n• **Odbiór osobisty:** tego samego dnia do godz. 18:00\n• **Dostawa ekspresowa:** do 4h w wybranych miastach (+49 zł)\n• **Części na zamówienie:** 2-5 dni roboczych\n\n✅ Darmowa dostawa od 299 zł!',
                'category': 'dostawa'
            },
            {
                'id': 'FAQ002',
                'keywords': ['zwrot', 'reklamacja', 'wymiana', 'gwarancja', 'wadliwa część'],
                'question': 'Jak zwrócić lub wymienić część?',
                'answer': '↩️ **Zwroty i reklamacje:**\n\n• **14 dni** na zwrot bez montażu\n• **24 miesiące** gwarancji na wszystkie części\n• **Darmowa wymiana** przy wadzie fabrycznej\n• **Zwrot kosztów montażu** przy wadliwej części\n\n📝 Wypełnij formularz online i otrzymasz etykietę zwrotową',
                'category': 'zwroty'
            },
            {
                'id': 'FAQ003',
                'keywords': ['montaż', 'warsztat', 'mechanik', 'instalacja', 'wymiana'],
                'question': 'Czy oferujecie montaż części?',
                'answer': '🔧 **Usługi montażu:**\n\n• **Sieć 200+ warsztatów partnerskich** w całej Polsce\n• **Rabat 15%** na montaż przy zakupie u nas\n• **Gwarancja na montaż:** 12 miesięcy\n• **Umów montaż online** przy składaniu zamówienia\n\n📞 Pomoc w doborze warsztatu: 800-MONTAZ',
                'category': 'montaż'
            },
            {
                'id': 'FAQ004',
                'keywords': ['pasuje', 'kompatybilność', 'VIN', 'model', 'rocznik', 'dopasowanie'],
                'question': 'Jak sprawdzić czy część pasuje do mojego auta?',
                'answer': '🔍 **Sprawdzanie kompatybilności:**\n\n• **Wyszukiwarka po VIN** - 100% pewności\n• **Katalog TecDoc** - wybierz markę/model/rocznik\n• **Czat z ekspertem** - pomoc w doborze\n• **Numer OE części** - znajdziemy zamiennik\n\n💡 W razie wątpliwości wyślij nam zdjęcie tabliczki znamionowej',
                'category': 'dobór'
            }
        ]
        
        # Przykładowe zamówienia
        self.orders_database = {
            'MOT-2024001': {
                'status': '🚚 W drodze',
                'details': 'Przesyłka nadana dziś o 14:30. Dostawa jutro do 12:00',
                'tracking': 'DPD: 0123456789',
                'items': ['Klocki hamulcowe Bosch BMW E90', 'Filtr oleju Mann HU719/7x']
            },
            'MOT-2024002': {
                'status': '✅ Dostarczone',
                'details': 'Dostarczone wczoraj o 16:45. Podpis: J.Kowalski',
                'tracking': 'InPost: 670000123456',
                'items': ['Amortyzator Bilstein B4 (2 szt.)', 'Olej Castrol Edge 5W30']
            }
        }
    
    def normalize_query(self, query):
        """Normalizacja zapytania - obsługa literówek typowych dla motoryzacji"""
        query = query.lower().strip()
        
        # Korekta popularnych literówek w motoryzacji
        typo_corrections = {
            'kloki': 'klocki',
            'klocek': 'klocki',
            'hamulec': 'hamulce',
            'amortyztor': 'amortyzator',
            'amortyzaor': 'amortyzator',
            'filtr': 'filtr',
            'filetr': 'filtr',
            'swica': 'świeca',
            'swieca': 'świeca',
            'akumulator': 'akumulator',
            'akumlator': 'akumulator',
            'bateria': 'akumulator',
            'bosch': 'bosch',
            'bosh': 'bosch',
            'mann': 'mann',
            'man': 'mann',
            'brembo': 'brembo',
            'brebo': 'brembo'
        }
        
        for typo, correction in typo_corrections.items():
            query = query.replace(typo, correction)
        
        # Liczba mnoga/pojedyncza
        plural_singular = {
            'klocki': 'klocki',
            'klocków': 'klocki',
            'tarcze': 'tarcza',
            'tarcz': 'tarcza',
            'filtry': 'filtr',
            'filtrów': 'filtr',
            'świece': 'świeca',
            'świec': 'świeca',
            'amortyzatory': 'amortyzator',
            'amortyzatorów': 'amortyzator',
            'oleje': 'olej',
            'olejów': 'olej'
        }
        
        for plural, singular in plural_singular.items():
            query = query.replace(plural, singular)
        
        query = ' '.join(query.split())
        return query
    
    def get_fuzzy_product_matches(self, query, machine_filter=None, limit=6):
        """Inteligentne dopasowanie produktów z fuzzy matching"""
        query = self.normalize_query(query)
        matches = []
        
        for product in self.product_database['products']:
            if machine_filter and product['machine'] != machine_filter and product['machine'] != 'uniwersalny':
                continue
            
            search_text = f"{product['name']} {product['category']} {product['brand']} {product['model']} {product['id']}"
            
            scores = [
                fuzz.ratio(query, search_text.lower()),
                fuzz.partial_ratio(query, search_text.lower()),
                fuzz.token_sort_ratio(query, search_text.lower()),
                fuzz.token_set_ratio(query, search_text.lower())
            ]
            
            brand_score = fuzz.ratio(query, product['brand'].lower())
            model_score = fuzz.ratio(query, product['model'].lower())
            
            max_score = max(scores)
            
            if brand_score > 80:
                max_score = min(100, max_score + 15)
            if model_score > 80:
                max_score = min(100, max_score + 15)
            
            query_words = query.split()
            search_words = search_text.lower().split()
            for q_word in query_words:
                for s_word in search_words:
                    if q_word in s_word or s_word in q_word:
                        max_score = min(100, max_score + 10)
                        break
            
            if max_score >= 40:
                matches.append((product, max_score))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:limit]
    
    def get_fuzzy_faq_matches(self, query, limit=5):
        """Dopasowanie FAQ z fuzzy matching"""
        query = self.normalize_query(query)
        matches = []
        
        for faq in self.faq_database:
            search_text = f"{faq['question']} {' '.join(faq['keywords'])}"
            
            scores = [
                fuzz.ratio(query, search_text.lower()),
                fuzz.partial_ratio(query, search_text.lower()),
                fuzz.token_sort_ratio(query, search_text.lower()),
                fuzz.token_set_ratio(query, search_text.lower())
            ]
            
            max_score = max(scores)
            
            for keyword in faq['keywords']:
                if fuzz.partial_ratio(query, keyword) > 75:
                    max_score = min(100, max_score + 10)
            
            if max_score >= 35:
                matches.append((faq, max_score))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:limit]
    
    def search_products(self, query, machine_filter=None):
        """Wyszukiwanie produktów"""
        results = self.get_fuzzy_product_matches(query, machine_filter, limit=20)
        return [product for product, score in results]
    
    def search_faq(self, query):
        """Wyszukiwanie FAQ"""
        results = self.get_fuzzy_faq_matches(query, limit=10)
        return [faq for faq, score in results]
    
    def get_initial_greeting(self):
        """Powitanie dostosowane do branży motoryzacyjnej"""
        return {
            'text_message': """🚗 **Witaj w Auto Parts Pro**

Jestem Twoim ekspertem od części samochodowych. Pomogę Ci znaleźć idealną część lub odpowiem na pytania.

Co Cię interesuje?""",
            'buttons': [
                {'text': '🔧 Znajdź część', 'action': 'search_product'},
                {'text': '📦 Status zamówienia', 'action': 'order_status'},
                {'text': '❓ Mam pytanie', 'action': 'faq_search'},
                {'text': '🚚 Dostawa i koszty', 'action': 'faq_delivery'},
                {'text': '↩️ Zwroty i gwarancja', 'action': 'faq_returns'},
                {'text': '📞 Kontakt', 'action': 'contact'}
            ]
        }
    
    def handle_button_action(self, action):
        """Obsługa akcji przycisków"""
        session['context'] = action
        
        if action == 'search_product':
            return {
                'text_message': """🔧 **Wyszukiwarka części**

Wybierz typ pojazdu:""",
                'buttons': [
                    {'text': '🚗 Samochód osobowy', 'action': 'machine_osobowy'},
                    {'text': '🚐 Dostawczy', 'action': 'machine_dostawczy'},
                    {'text': '🏍️ Motocykl', 'action': 'machine_motocykl'},
                    {'text': '🔧 Części uniwersalne', 'action': 'machine_uniwersalny'},
                    {'text': '↩️ Powrót', 'action': 'main_menu'}
                ]
            }
        
        elif action.startswith('machine_'):
            machine_type = action.replace('machine_', '')
            session['machine_filter'] = machine_type
            
            machine_names = {
                'osobowy': 'Samochód osobowy',
                'dostawczy': 'Samochód dostawczy',
                'motocykl': 'Motocykl',
                'uniwersalny': 'Części uniwersalne'
            }
            
            return {
                'text_message': f"""✅ **{machine_names.get(machine_type, 'Pojazd')}**

Wpisz czego szukasz (nazwę części, markę, numer OE):""",
                'enable_input': True,
                'input_placeholder': 'np. klocki bosch, filtr mann, amortyzator...',
                'search_mode': True
            }
        
        elif action == 'faq_search':
            return {
                'text_message': """❓ **Centrum pomocy**

Wpisz swoje pytanie:""",
                'enable_input': True,
                'input_placeholder': 'np. jak sprawdzić czy część pasuje...',
                'faq_mode': True
            }
        
        elif action == 'order_status':
            return {
                'text_message': """📦 **Status zamówienia**

Wpisz numer (format: MOT-XXXXXXX):""",
                'enable_input': True,
                'input_placeholder': 'np. MOT-2024001'
            }
        
        elif action.startswith('faq_'):
            return self.handle_faq(action)
        
        elif action == 'contact':
            return {
                'text_message': """📞 **Kontakt**

**Infolinia:** 800 AUTO PARTS (bezpłatna)
**WhatsApp:** +48 500 100 200
**Email:** pomoc@autoparts.pl

⏰ Pon-Pt 8:00-20:00, Sob 9:00-16:00""",
                'buttons': [
                    {'text': '💬 Zadaj pytanie', 'action': 'faq_search'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        elif action == 'main_menu':
            return self.get_initial_greeting()
        
        elif action.startswith('add_to_cart_'):
            product_id = action.replace('add_to_cart_', '')
            return self.add_to_cart(product_id)
        
        elif action.startswith('product_details_'):
            product_id = action.replace('product_details_', '')
            return self.show_product_details(product_id)
        
        return {
            'text_message': 'Wybierz opcję:',
            'buttons': [{'text': '↩️ Menu główne', 'action': 'main_menu'}]
        }
    
    def handle_faq(self, action):
        """Obsługa FAQ"""
        faq_mapping = {
            'faq_delivery': 'FAQ001',
            'faq_returns': 'FAQ002'
        }
        
        faq_id = faq_mapping.get(action)
        if faq_id:
            faq = next((f for f in self.faq_database if f['id'] == faq_id), None)
            if faq:
                return {
                    'text_message': f"**{faq['question']}**\n\n{faq['answer']}",
                    'buttons': [
                        {'text': '❓ Inne pytanie', 'action': 'faq_search'},
                        {'text': '↩️ Menu główne', 'action': 'main_menu'}
                    ]
                }
        
        return {
            'text_message': 'Nie znaleziono odpowiedzi.',
            'buttons': [
                {'text': '📞 Kontakt', 'action': 'contact'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ]
        }
    
    def process_message(self, message):
        """Przetwarzanie wiadomości"""
        context = session.get('context', '')
        
        if context == 'faq_search':
            faq_results = self.search_faq(message)
            
            if faq_results:
                best_match = faq_results[0]
                response = f"**{best_match['question']}**\n\n{best_match['answer']}"
                
                if len(faq_results) > 1:
                    response += "\n\n**Zobacz też:**"
                    for faq in faq_results[1:3]:
                        response += f"\n• {faq['question']}"
                
                return {
                    'text_message': response,
                    'buttons': [
                        {'text': '❓ Zadaj inne pytanie', 'action': 'faq_search'},
                        {'text': '↩️ Menu główne', 'action': 'main_menu'}
                    ]
                }
            else:
                return {
                    'text_message': """Nie znalazłem odpowiedzi.

📞 Zadzwoń: 800 AUTO PARTS
📧 Email: pomoc@autoparts.pl""",
                    'buttons': [
                        {'text': '❓ Spróbuj ponownie', 'action': 'faq_search'},
                        {'text': '↩️ Menu główne', 'action': 'main_menu'}
                    ]
                }
        
        elif context == 'order_status' or message.upper().startswith('MOT-'):
            order_num = message.upper()
            if order_num in self.orders_database:
                order = self.orders_database[order_num]
                items_list = '\n'.join([f"• {item}" for item in order['items']])
                
                return {
                    'text_message': f"""📦 **Zamówienie {order_num}**

**Status:** {order['status']}
**Szczegóły:** {order['details']}
**Tracking:** {order['tracking']}

**Produkty:**
{items_list}""",
                    'buttons': [
                        {'text': '📦 Sprawdź inne', 'action': 'order_status'},
                        {'text': '↩️ Menu główne', 'action': 'main_menu'}
                    ]
                }
            else:
                return {
                    'text_message': f"""❌ Nie znaleziono zamówienia {order_num}""",
                    'buttons': [
                        {'text': '🔄 Spróbuj ponownie', 'action': 'order_status'},
                        {'text': '↩️ Menu główne', 'action': 'main_menu'}
                    ]
                }
        
        elif session.get('machine_filter'):
            machine_filter = session.get('machine_filter')
            results = self.search_products(message, machine_filter)
            
            if not results:
                results = self.search_products(message)
                
                if results:
                    return {
                        'text_message': f"""⚠️ Nie znaleziono dla wybranego typu, ale mamy inne:

{self.format_product_results(results[:3])}""",
                        'buttons': self.create_product_buttons(results[:3])
                    }
                else:
                    return {
                        'text_message': """❌ Nie znaleziono produktów.

System automatycznie poprawia błędy. Spróbuj inaczej.""",
                        'buttons': [
                            {'text': '🔄 Szukaj ponownie', 'action': 'search_product'},
                            {'text': '↩️ Menu główne', 'action': 'main_menu'}
                        ]
                    }
            
            elif len(results) == 1:
                product = results[0]
                return self.show_product_details(product['id'])
            
            elif len(results) <= 5:
                return {
                    'text_message': f"""✅ Znaleziono {len(results)} produktów:

{self.format_product_results(results)}""",
                    'buttons': self.create_product_buttons(results)
                }
            
            else:
                return {
                    'text_message': f"""🔍 Znaleziono {len(results)} produktów. Top 5:

{self.format_product_results(results[:5])}""",
                    'buttons': self.create_product_buttons(results[:5])
                }
        
        return {
            'text_message': 'Wybierz opcję:',
            'buttons': [
                {'text': '🔧 Szukaj części', 'action': 'search_product'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ]
        }
    
    def format_product_results(self, products):
        """Formatowanie wyników"""
        result = ""
        for product in products:
            stock_icon = "✅" if product['stock'] > 10 else "⚠️" if product['stock'] > 0 else "❌"
            result += f"""
**{product['name']}**
{product['id']} | {stock_icon} {product['stock']} szt. | {product['price']:.2f} zł
"""
        return result
    
    def create_product_buttons(self, products):
        """Przyciski produktów"""
        buttons = []
        for product in products[:4]:
            buttons.append({
                'text': f"🛒 {product['name'][:30]}... ({product['price']:.0f} zł)",
                'action': f"product_details_{product['id']}"
            })
        
        buttons.extend([
            {'text': '🔄 Szukaj ponownie', 'action': 'search_product'},
            {'text': '↩️ Menu główne', 'action': 'main_menu'}
        ])
        
        return buttons
    
    def show_product_details(self, product_id):
        """Szczegóły produktu"""
        product = None
        for p in self.product_database['products']:
            if p['id'] == product_id:
                product = p
                break
        
        if not product:
            return {
                'text_message': 'Produkt nie znaleziony.',
                'buttons': [{'text': '↩️ Menu główne', 'action': 'main_menu'}]
            }
        
        stock_status = "✅ Dostępny" if product['stock'] > 10 else "⚠️ Ostatnie sztuki" if product['stock'] > 0 else "❌ Na zamówienie"
        
        return {
            'text_message': f"""🔧 **{product['name']}**

📋 **Dane techniczne:**
• Kod: {product['id']}
• Producent: {product['brand']}
• Model: {product['model']}
• Kategoria: {self.product_database['categories'].get(product['category'], product['category'])}

💰 **Cena:** {product['price']:.2f} zł netto
💵 **Cena brutto:** {product['price'] * 1.23:.2f} zł

📦 **Dostępność:** {stock_status} ({product['stock']} szt.)
🚚 **Wysyłka:** 24h""",
            'buttons': [
                {'text': f"🛒 Dodaj do koszyka", 'action': f"add_to_cart_{product['id']}"},
                {'text': '🔍 Szukaj dalej', 'action': 'search_product'},
                {'text': '🏠 Menu główne', 'action': 'main_menu'}
            ]
        }
    
    def add_to_cart(self, product_id):
        """Dodanie do koszyka"""
        product = None
        for p in self.product_database['products']:
            if p['id'] == product_id:
                product = p
                break
        
        if not product:
            return {
                'text_message': 'Błąd dodawania do koszyka.',
                'buttons': [{'text': '↩️ Powrót', 'action': 'main_menu'}]
            }
        
        if 'cart' not in session:
            session['cart'] = []
        
        session['cart'].append({
            'id': product['id'],
            'name': product['name'],
            'price': product['price']
        })
        session.modified = True
        
        cart_total = sum(item['price'] * 1.23 for item in session['cart'])
        
        return {
            'text_message': f"""✅ **Dodano do koszyka!**

🛒 {product['name']}
💰 {product['price'] * 1.23:.2f} zł brutto

**Koszyk ({len(session['cart'])} szt.):** {cart_total:.2f} zł

{'🎉 Darmowa dostawa!' if cart_total >= 299 else f'Do darmowej dostawy brakuje: {299 - cart_total:.2f} zł'}""",
            'cart_updated': True,
            'buttons': [
                {'text': '✅ Przejdź do kasy', 'action': 'checkout'},
                {'text': '🔍 Kontynuuj zakupy', 'action': 'search_product'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ]
        }
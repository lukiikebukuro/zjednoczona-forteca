"""
Uniwersalny Żołnierz - Silnik bota e-commerce v3.0
Prototyp dla Kramp z inteligentnym wyszukiwaniem i fuzzy matching
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
        """Inicjalizuje rozbudowaną bazę danych demo"""
        
        # Bogata baza produktów - 20 przykładów
        self.product_database = {
            'products': [
                # Pompy hydrauliczne
                {'id': 'PH001', 'name': 'Pompa hydrauliczna Ursus C-360', 'category': 'hydraulika', 'machine': 'traktor', 'brand': 'Ursus', 'model': 'C-360', 'price': 1250.00, 'stock': 15},
                {'id': 'PH002', 'name': 'Pompa hydrauliczna Zetor 7245', 'category': 'hydraulika', 'machine': 'traktor', 'brand': 'Zetor', 'model': '7245', 'price': 1450.00, 'stock': 8},
                {'id': 'PH003', 'name': 'Pompa hydrauliczna John Deere 6130R', 'category': 'hydraulika', 'machine': 'traktor', 'brand': 'John Deere', 'model': '6130R', 'price': 3200.00, 'stock': 5},
                
                # Filtry
                {'id': 'FO001', 'name': 'Filtr oleju MANN W940/25', 'category': 'filtry', 'machine': 'uniwersalny', 'brand': 'MANN', 'model': 'W940/25', 'price': 45.00, 'stock': 250},
                {'id': 'FO002', 'name': 'Filtr oleju Donaldson P502067', 'category': 'filtry', 'machine': 'uniwersalny', 'brand': 'Donaldson', 'model': 'P502067', 'price': 52.00, 'stock': 180},
                {'id': 'FP001', 'name': 'Filtr paliwa MANN WK8020', 'category': 'filtry', 'machine': 'uniwersalny', 'brand': 'MANN', 'model': 'WK8020', 'price': 38.00, 'stock': 320},
                {'id': 'FA001', 'name': 'Filtr powietrza John Deere AL78223', 'category': 'filtry', 'machine': 'traktor', 'brand': 'John Deere', 'model': 'AL78223', 'price': 125.00, 'stock': 95},
                
                # Paski klinowe
                {'id': 'PK001', 'name': 'Pasek klinowy 13x1000', 'category': 'paski', 'machine': 'uniwersalny', 'brand': 'Gates', 'model': '13x1000', 'price': 25.00, 'stock': 500},
                {'id': 'PK002', 'name': 'Pasek klinowy 13x1250', 'category': 'paski', 'machine': 'uniwersalny', 'brand': 'Gates', 'model': '13x1250', 'price': 28.00, 'stock': 450},
                {'id': 'PK003', 'name': 'Pasek klinowy SPZ 1500', 'category': 'paski', 'machine': 'uniwersalny', 'brand': 'Optibelt', 'model': 'SPZ 1500', 'price': 42.00, 'stock': 200},
                
                # Łożyska
                {'id': 'LO001', 'name': 'Łożysko 6205 2RS', 'category': 'łożyska', 'machine': 'uniwersalny', 'brand': 'SKF', 'model': '6205-2RS', 'price': 35.00, 'stock': 380},
                {'id': 'LO002', 'name': 'Łożysko 6207 2RS', 'category': 'łożyska', 'machine': 'uniwersalny', 'brand': 'SKF', 'model': '6207-2RS', 'price': 48.00, 'stock': 290},
                {'id': 'LO003', 'name': 'Łożysko stożkowe 32008', 'category': 'łożyska', 'machine': 'uniwersalny', 'brand': 'FAG', 'model': '32008', 'price': 85.00, 'stock': 120},
                
                # Części do kombajnów
                {'id': 'KO001', 'name': 'Nóż kosiarki Claas Lexion', 'category': 'żniwa', 'machine': 'kombajn', 'brand': 'Claas', 'model': 'Lexion', 'price': 320.00, 'stock': 45},
                {'id': 'KO002', 'name': 'Palce podbieracza John Deere', 'category': 'żniwa', 'machine': 'kombajn', 'brand': 'John Deere', 'model': 'Universal', 'price': 18.00, 'stock': 800},
                {'id': 'KO003', 'name': 'Sito żaluzjowe Bizon Z056', 'category': 'żniwa', 'machine': 'kombajn', 'brand': 'Bizon', 'model': 'Z056', 'price': 890.00, 'stock': 12},
                
                # Oleje i smary
                {'id': 'OL001', 'name': 'Olej silnikowy 15W40 20L', 'category': 'oleje', 'machine': 'uniwersalny', 'brand': 'Shell', 'model': 'Rimula R4', 'price': 380.00, 'stock': 150},
                {'id': 'OL002', 'name': 'Olej hydrauliczny HLP 46 20L', 'category': 'oleje', 'machine': 'uniwersalny', 'brand': 'Mobil', 'model': 'DTE 25', 'price': 340.00, 'stock': 180},
                {'id': 'SM001', 'name': 'Smar grafitowy 400g', 'category': 'smary', 'machine': 'uniwersalny', 'brand': 'Liqui Moly', 'model': 'Graphit', 'price': 28.00, 'stock': 420},
                
                # Części elektryczne
                {'id': 'EL001', 'name': 'Rozrusznik Ursus C-360', 'category': 'elektryka', 'machine': 'traktor', 'brand': 'Iskra', 'model': 'AZF4562', 'price': 680.00, 'stock': 25}
            ],
            'categories': {
                'hydraulika': 'Hydraulika siłowa',
                'filtry': 'Filtry',
                'paski': 'Paski napędowe',
                'łożyska': 'Łożyska',
                'żniwa': 'Części żniwne',
                'oleje': 'Oleje',
                'smary': 'Smary',
                'elektryka': 'Części elektryczne'
            },
            'machines': {
                'traktor': '🚜 Traktor',
                'kombajn': '🌾 Kombajn',
                'przyczepa': '🚛 Przyczepa',
                'maszyny_zielonkowe': '🌱 Maszyny zielonkowe',
                'uniwersalny': '🔧 Uniwersalne'
            }
        }
        
        # Rozbudowana baza FAQ - pełne odpowiedzi na kluczowe pytania
        self.faq_database = [
            {
                'id': 'FAQ001',
                'keywords': ['dostawa', 'wysyłka', 'kiedy', 'czas dostawy', 'przesyłka', 'kurier'],
                'question': 'Jaki jest czas dostawy?',
                'answer': '📦 **Opcje dostawy:**\n\n• **Dostawa standardowa:** 24-48h (19,99 zł)\n• **Dostawa ekspresowa:** następny dzień roboczy do 12:00 (39,99 zł)\n• **Odbiór osobisty:** tego samego dnia do godz. 17:00 (bezpłatnie)\n• **Dostawa paletowa:** 2-3 dni robocze (od 99 zł)\n\n🆓 **Darmowa dostawa od 200 zł!**',
                'category': 'dostawa'
            },
            {
                'id': 'FAQ002',
                'keywords': ['zwrot', 'reklamacja', 'wymiana', 'oddać', 'wadliwy', 'zepsuty'],
                'question': 'Jak mogę zwrócić lub reklamować produkt?',
                'answer': '↩️ **Polityka zwrotów:**\n\n• **30 dni** na zwrot bez podania przyczyny\n• **Darmowa etykieta zwrotowa** w paczce\n• **Zwrot pieniędzy w 7 dni** od otrzymania produktu\n\n📝 **Proces reklamacji:**\n1. Wypełnij formularz online\n2. Wydrukuj etykietę\n3. Nadaj paczkę\n4. Otrzymaj decyzję w 14 dni',
                'category': 'zwroty'
            },
            {
                'id': 'FAQ003',
                'keywords': ['płatność', 'zapłacić', 'metody płatności', 'przelew', 'karta', 'blik'],
                'question': 'Jakie są metody płatności?',
                'answer': '💳 **Akceptujemy:**\n\n• Karty kredytowe/debetowe (Visa, Mastercard)\n• BLIK\n• Przelewy24\n• PayPal\n• Przelew tradycyjny\n• Płatność przy odbiorze (+5 zł)\n• **Odroczony termin płatności** (dla stałych klientów)',
                'category': 'płatności'
            },
            {
                'id': 'FAQ004',
                'keywords': ['gwarancja', 'rękojmia', 'serwis', 'naprawa'],
                'question': 'Jaka jest gwarancja na produkty?',
                'answer': '✅ **Gwarancja:**\n\n• **24 miesiące** gwarancji producenta\n• **Darmowa naprawa** lub wymiana\n• **Door-to-door** - odbieramy i dostarczamy naprawiony produkt\n• **Produkt zastępczy** na czas naprawy (dla wybranych produktów)\n• **Wsparcie techniczne 24/7** pod nr 800-009-009',
                'category': 'gwarancja'
            },
            {
                'id': 'FAQ005',
                'keywords': ['rabat', 'zniżka', 'promocja', 'taniej', 'kod rabatowy'],
                'question': 'Jak otrzymać rabat?',
                'answer': '💰 **Aktualne rabaty:**\n\n• **-5%** na pierwsze zamówienie (kod: NOWY5)\n• **-10%** przy zamówieniu powyżej 1000 zł\n• **-15%** w programie lojalnościowym KRAMP PLUS\n• **Newsletter** = ekskluzywne kody co tydzień\n• **Rabaty ilościowe** przy zakupie hurtowym',
                'category': 'promocje'
            },
            {
                'id': 'FAQ006',
                'keywords': ['faktura', 'vat', 'firma', 'nip', 'księgowość'],
                'question': 'Czy wystawiacie faktury VAT?',
                'answer': '📄 **Faktury VAT:**\n\n• Automatyczna faktura VAT dla firm\n• Faktura elektroniczna na email\n• Możliwość pobrania z panelu klienta\n• **Split payment** obsługiwany\n• **Zakupy na firmę** z odroczonym terminem płatności (do 60 dni)',
                'category': 'faktury'
            },
            {
                'id': 'FAQ007',
                'keywords': ['kontakt', 'telefon', 'email', 'pomoc', 'wsparcie', 'konsultant'],
                'question': 'Jak się skontaktować z Kramp?',
                'answer': '📞 **Kontakt:**\n\n• **Infolinia:** 800-009-009 (bezpłatna)\n• **WhatsApp:** +48 500 600 700\n• **Email:** pomoc@kramp.com\n• **Czat online:** 7:00-20:00\n• **20 oddziałów** w całej Polsce\n• **Doradca techniczny:** ekspert@kramp.com',
                'category': 'kontakt'
            }
        ]
        
        # Przykładowe zamówienia
        self.orders_database = {
            'KRP-123456': {
                'status': '🚚 W drodze',
                'details': 'Przesyłka została nadana. Przewidywana dostawa: jutro do 16:00',
                'tracking': 'DPD: 1234567890',
                'items': ['Pompa hydrauliczna Ursus C-360', 'Filtr oleju MANN W940/25']
            },
            'KRP-789012': {
                'status': '✅ Dostarczone',
                'details': 'Zamówienie dostarczone 15.03.2024 o 14:30',
                'tracking': 'UPS: 9876543210',
                'items': ['Pasek klinowy 13x1000 (5 szt.)', 'Łożysko 6205 2RS (2 szt.)']
            }
        }
    
    def get_fuzzy_product_matches(self, query, machine_filter=None, limit=6):
        """
        Get products using fuzzy matching with scores
        Returns list of tuples (product, score)
        """
        query = self.normalize_query(query)
        matches = []
        
        for product in self.product_database['products']:
            # Skip if machine filter doesn't match
            if machine_filter and product['machine'] != machine_filter and product['machine'] != 'uniwersalny':
                continue
            
            # Create searchable text combining all product fields
            search_text = f"{product['name']} {product['category']} {product['brand']} {product['model']} {product['id']}"
            
            # Calculate multiple fuzzy scores
            scores = [
                fuzz.ratio(query, search_text.lower()),
                fuzz.partial_ratio(query, search_text.lower()),
                fuzz.token_sort_ratio(query, search_text.lower()),
                fuzz.token_set_ratio(query, search_text.lower())
            ]
            
            # Check individual important fields for bonus points
            brand_score = fuzz.ratio(query, product['brand'].lower())
            model_score = fuzz.ratio(query, product['model'].lower())
            id_score = fuzz.ratio(query, product['id'].lower())
            
            # Calculate final score with weights
            max_score = max(scores)
            
            # Bonus for exact field matches
            if brand_score > 80:
                max_score = min(100, max_score + 15)
            if model_score > 80:
                max_score = min(100, max_score + 15)
            if id_score > 90:
                max_score = min(100, max_score + 20)
            
            # Check for partial matches at word boundaries
            query_words = query.split()
            search_words = search_text.lower().split()
            for q_word in query_words:
                for s_word in search_words:
                    if q_word in s_word or s_word in q_word:
                        max_score = min(100, max_score + 10)
                        break
            
            # Only include if score is above threshold
            if max_score >= 40:  # Lower threshold for partial matches
                matches.append((product, max_score))
        
        # Sort by score descending and return top results
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:limit]
    
    def get_fuzzy_faq_matches(self, query, limit=5):
        """
        Get FAQ entries using fuzzy matching with scores
        Returns list of tuples (faq, score)
        """
        query = self.normalize_query(query)
        matches = []
        
        for faq in self.faq_database:
            # Create searchable text from question and keywords
            search_text = f"{faq['question']} {' '.join(faq['keywords'])}"
            
            # Calculate fuzzy scores
            scores = [
                fuzz.ratio(query, search_text.lower()),
                fuzz.partial_ratio(query, search_text.lower()),
                fuzz.token_sort_ratio(query, search_text.lower()),
                fuzz.token_set_ratio(query, search_text.lower())
            ]
            
            max_score = max(scores)
            
            # Bonus points for keyword matches
            for keyword in faq['keywords']:
                if fuzz.partial_ratio(query, keyword) > 75:
                    max_score = min(100, max_score + 10)
            
            # Check category match
            if 'category' in faq and fuzz.partial_ratio(query, faq['category']) > 70:
                max_score = min(100, max_score + 10)
            
            if max_score >= 35:  # Lower threshold for FAQ
                matches.append((faq, max_score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:limit]
    
    def normalize_query(self, query):
        """Normalizacja zapytania - obsługa liczby mnogiej, spacji, literówek"""
        query = query.lower().strip()
        
        # Automatyczna korekta popularnych literówek
        typo_corrections = {
            'usrus': 'ursus',
            'ursuz': 'ursus',
            'zetr': 'zetor',
            'zetro': 'zetor',
            'jon dir': 'john deere',
            'johndeer': 'john deere',
            'john deer': 'john deere',
            'man': 'mann',
            'skf': 'skf',
            'lożysko': 'łożysko',
            'lozysko': 'łożysko',
            'filtr': 'filtr',
            'filetr': 'filtr',
            'pompa': 'pompa',
            'ponpa': 'pompa',
            'pasek': 'pasek',
            'pasek': 'pasek'
        }
        
        for typo, correction in typo_corrections.items():
            query = query.replace(typo, correction)
        
        # Automatyczna obsługa liczby mnogiej/pojedynczej
        plural_singular = {
            'filtry': 'filtr',
            'filtrów': 'filtr',
            'pompy': 'pompa',
            'pomp': 'pompa',
            'paski': 'pasek',
            'pasków': 'pasek',
            'łożyska': 'łożysko',
            'łożysk': 'łożysko',
            'oleje': 'olej',
            'olejów': 'olej',
            'smary': 'smar',
            'smarów': 'smar'
        }
        
        for plural, singular in plural_singular.items():
            query = query.replace(plural, singular)
        
        # Usuń podwójne spacje
        query = ' '.join(query.split())
        
        return query
    
    def search_products(self, query, machine_filter=None):
        """Inteligentne wyszukiwanie produktów z fuzzy matching"""
        query = self.normalize_query(query)
        results = []
        scores = []
        
        for product in self.product_database['products']:
            # Filtr po typie maszyny
            if machine_filter and product['machine'] != machine_filter and product['machine'] != 'uniwersalny':
                continue
            
            # Przygotuj tekst do przeszukania
            searchable_text = f"{product['name']} {product['category']} {product['brand']} {product['model']} {product['id']}".lower()
            
            # Użyj fuzzy matching
            score = fuzz.token_set_ratio(query, searchable_text)
            
            # Dodatkowe punkty za dokładne dopasowanie marki lub modelu
            if query in product['brand'].lower():
                score += 20
            if query in product['model'].lower():
                score += 20
            
            if score >= 60:  # Próg dopasowania
                results.append(product)
                scores.append(score)
        
        # Sortuj wyniki według dopasowania
        if results:
            sorted_results = [x for _, x in sorted(zip(scores, results), key=lambda pair: pair[0], reverse=True)]
            return sorted_results
        
        return []
    
    def search_faq(self, query):
        """Inteligentne wyszukiwanie w FAQ z fuzzy matching"""
        query = self.normalize_query(query)
        results = []
        scores = []
        
        for faq in self.faq_database:
            # Przygotuj tekst do przeszukania
            searchable_text = f"{faq['question']} {' '.join(faq['keywords'])}".lower()
            
            # Użyj fuzzy matching
            score = fuzz.token_set_ratio(query, searchable_text)
            
            # Dodatkowe punkty za dopasowanie słów kluczowych
            for keyword in faq['keywords']:
                if keyword in query:
                    score += 15
            
            if score >= 50:  # Niższy próg dla FAQ
                results.append(faq)
                scores.append(score)
        
        # Sortuj wyniki według dopasowania
        if results:
            sorted_results = [x for _, x in sorted(zip(scores, results), key=lambda pair: pair[0], reverse=True)]
            return sorted_results
        
        return []
    
    def get_initial_greeting(self):
        """Powitanie z menu głównym"""
        return {
            'text_message': """🚜 **Witaj w Kramp - Ekspert Części Zamiennych**

Jestem Twoim inteligentnym asystentem. Pomogę Ci znaleźć idealną część zamienną lub odpowiem na pytania.

Wybierz, w czym mogę pomóc:""",
            'buttons': [
                {'text': '🔧 Znajdź Część / Produkt', 'action': 'search_product'},
                {'text': '📦 Status Zamówienia', 'action': 'order_status'},
                {'text': '❓ Mam pytanie (FAQ)', 'action': 'faq_search'},
                {'text': '🚚 Dostawa i Koszty', 'action': 'faq_delivery'},
                {'text': '↩️ Zwroty i Reklamacje', 'action': 'faq_returns'},
                {'text': '📞 Kontakt', 'action': 'contact'}
            ]
        }
    
    def handle_button_action(self, action):
        """Obsługa akcji przycisków"""
        session['context'] = action
        
        if action == 'search_product':
            return {
                'text_message': """🔧 **Wyszukiwarka Części - Krok 1**

Wybierz typ maszyny:""",
                'buttons': [
                    {'text': '🚜 Traktor', 'action': 'machine_traktor'},
                    {'text': '🌾 Kombajn', 'action': 'machine_kombajn'},
                    {'text': '🚛 Przyczepa', 'action': 'machine_przyczepa'},
                    {'text': '🌱 Maszyny zielonkowe', 'action': 'machine_zielonkowe'},
                    {'text': '🔧 Części uniwersalne', 'action': 'machine_uniwersalny'},
                    {'text': '↩️ Powrót', 'action': 'main_menu'}
                ]
            }
        
        elif action.startswith('machine_'):
            machine_type = action.replace('machine_', '')
            session['machine_filter'] = machine_type
            
            machine_names = {
                'traktor': 'Traktor',
                'kombajn': 'Kombajn',
                'przyczepa': 'Przyczepa',
                'zielonkowe': 'Maszyny zielonkowe',
                'uniwersalny': 'Części uniwersalne'
            }
            
            return {
                'text_message': f"""✅ **Wybrano: {machine_names.get(machine_type, 'Maszyna')}**

Wpisz czego szukasz. Nie martw się literówkami - system automatycznie je poprawi!

Możesz wpisać:
• Nazwę części
• Numer katalogowy
• Markę lub model""",
                'enable_input': True,
                'input_placeholder': 'np. pompa ursus, filtr mann, łożysko 6205...',
                'search_mode': True
            }
        
        elif action == 'faq_search':
            return {
                'text_message': """❓ **Centrum Pomocy - FAQ**

O co chcesz zapytać? Wpisz swoje pytanie, a znajdę odpowiedź.

Popularne tematy:
• Dostawa i koszty wysyłki
• Zwroty i reklamacje
• Metody płatności
• Gwarancja i serwis
• Rabaty i promocje""",
                'enable_input': True,
                'input_placeholder': 'Wpisz pytanie, np. "jak zwrócić produkt"...',
                'faq_mode': True
            }
        
        elif action == 'order_status':
            return {
                'text_message': """📦 **Sprawdzanie Statusu Zamówienia**

Wpisz numer zamówienia (format: KRP-XXXXXX)

Przykładowe numery:
• KRP-123456 (w drodze)
• KRP-789012 (dostarczone)""",
                'enable_input': True,
                'input_placeholder': 'Wpisz numer zamówienia...'
            }
        
        elif action.startswith('faq_'):
            return self.handle_faq(action)
        
        elif action == 'contact':
            return {
                'text_message': """📞 **Kontakt z Kramp**

**Infolinia:** 800 009 009 (bezpłatna)
**WhatsApp:** +48 500 600 700
**Email:** pomoc@kramp.com

⏰ Dostępni: Pon-Pt 7:00-18:00, Sob 8:00-14:00

Preferujesz czat? Jestem tu, aby pomóc!""",
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
            'text_message': 'Wybierz opcję z menu:',
            'buttons': [{'text': '↩️ Menu główne', 'action': 'main_menu'}]
        }
    
    def handle_faq(self, action):
        """Obsługa FAQ"""
        faq_mapping = {
            'faq_delivery': 'FAQ001',
            'faq_returns': 'FAQ002',
            'faq_payments': 'FAQ003'
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
        """Przetwarzanie wiadomości tekstowej"""
        context = session.get('context', '')
        
        # FAQ search mode
        if context == 'faq_search':
            faq_results = self.search_faq(message)
            
            if faq_results:
                # Pokaż najlepsze dopasowanie
                best_match = faq_results[0]
                response = f"**{best_match['question']}**\n\n{best_match['answer']}"
                
                # Dodaj inne pytania jeśli są
                if len(faq_results) > 1:
                    response += "\n\n**Może też interesuje Cię:**"
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
                    'text_message': """Nie znalazłem dokładnej odpowiedzi na Twoje pytanie.

Skontaktuj się z nami bezpośrednio:
📞 800 009 009
📧 pomoc@kramp.com""",
                    'buttons': [
                        {'text': '❓ Spróbuj innego pytania', 'action': 'faq_search'},
                        {'text': '📞 Kontakt', 'action': 'contact'},
                        {'text': '↩️ Menu główne', 'action': 'main_menu'}
                    ]
                }
        
        # Order status checking
        elif context == 'order_status' or message.upper().startswith('KRP-'):
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
                        {'text': '📞 Kontakt', 'action': 'contact'},
                        {'text': '↩️ Menu główne', 'action': 'main_menu'}
                    ]
                }
        
        # Product search with machine filter
        elif session.get('machine_filter'):
            machine_filter = session.get('machine_filter')
            results = self.search_products(message, machine_filter)
            
            if not results:
                # Try without machine filter
                results = self.search_products(message)
                
                if results:
                    return {
                        'text_message': f"""⚠️ Nie znaleziono części dla wybranej maszyny, ale mamy inne pasujące produkty:

{self.format_product_results(results[:3])}""",
                        'buttons': self.create_product_buttons(results[:3])
                    }
                else:
                    return {
                        'text_message': f"""❌ Nie znaleziono produktów dla "{message}"

Ale nie martw się! Nasz system automatycznie poprawia literówki. Spróbuj innego zapytania.""",
                        'buttons': [
                            {'text': '🔄 Szukaj ponownie', 'action': 'search_product'},
                            {'text': '📞 Kontakt z ekspertem', 'action': 'contact'},
                            {'text': '↩️ Menu główne', 'action': 'main_menu'}
                        ]
                    }
            
            elif len(results) == 1:
                # Single result - show details
                product = results[0]
                return self.show_product_details(product['id'])
            
            elif len(results) <= 5:
                # Few results
                return {
                    'text_message': f"""✅ Znaleziono {len(results)} produktów:

{self.format_product_results(results)}""",
                    'buttons': self.create_product_buttons(results)
                }
            
            else:
                # Too many results
                return {
                    'text_message': f"""🔍 Znaleziono {len(results)} produktów. Pokazuję pierwsze 5:

{self.format_product_results(results[:5])}""",
                    'buttons': self.create_product_buttons(results[:5])
                }
        
        # Default response
        return {
            'text_message': f"""Nie rozumiem polecenia "{message}"

Wybierz jedną z opcji:""",
            'buttons': [
                {'text': '🔧 Szukaj części', 'action': 'search_product'},
                {'text': '❓ Zadaj pytanie', 'action': 'faq_search'},
                {'text': '📦 Status zamówienia', 'action': 'order_status'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ]
        }
    
    def format_product_results(self, products):
        """Formatowanie wyników wyszukiwania"""
        result = ""
        for product in products:
            stock_icon = "✅" if product['stock'] > 10 else "⚠️" if product['stock'] > 0 else "❌"
            result += f"""
**{product['name']}**
📦 {product['id']} | {stock_icon} {product['stock']} szt.
💰 {product['price']:.2f} zł netto
"""
        return result
    
    def create_product_buttons(self, products):
        """Tworzy przyciski dla produktów"""
        buttons = []
        for product in products[:4]:  # Max 4 products
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
        """Pokazuje szczegóły produktu"""
        product = None
        for p in self.product_database['products']:
            if p['id'] == product_id:
                product = p
                break
        
        if not product:
            return {
                'text_message': 'Produkt nie został znaleziony.',
                'buttons': [{'text': '↩️ Menu główne', 'action': 'main_menu'}]
            }
        
        stock_status = "✅ Dostępny od ręki" if product['stock'] > 10 else "⚠️ Ostatnie sztuki" if product['stock'] > 0 else "❌ Na zamówienie"
        
        return {
            'text_message': f"""🔧 **{product['name']}**

📋 **Informacje:**
• Kod: {product['id']}
• Marka: {product['brand']}
• Model: {product['model']}

💰 **Cena:** {product['price']:.2f} zł netto
💵 **Cena brutto:** {product['price'] * 1.23:.2f} zł (VAT 23%)

📦 **Dostępność:** {stock_status}
🚚 **Dostawa:** 24-48h""",
            'buttons': [
                {'text': f"🛒 Dodaj do koszyka", 'action': f"add_to_cart_{product['id']}"},
                {'text': '🔍 Szukaj inne', 'action': 'search_product'},
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
                'text_message': 'Nie można dodać produktu do koszyka.',
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
            'text_message': f"""✅ **Produkt dodany do koszyka!**

🛒 {product['name']}
💰 {product['price'] * 1.23:.2f} zł brutto

**Koszyk ({len(session['cart'])} produkt(ów)):**
Wartość: {cart_total:.2f} zł""",
            'cart_updated': True,
            'buttons': [
                {'text': '✅ Przejdź do kasy', 'action': 'checkout'},
                {'text': '🔍 Kontynuuj zakupy', 'action': 'search_product'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ]
        }
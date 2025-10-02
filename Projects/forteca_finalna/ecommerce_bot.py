
"""
Uniwersalny Żołnierz - Silnik bota e-commerce v5.1 SURGERY FIXED
System Inteligentnego Śledzenia Utraconego Popytu - NAPRAWIONA KALIBRACJA
CZĘŚĆ 1/3 - Import i inicjalizacja
"""
import json
import os
import re
import time
import hashlib
import random
import requests
import uuid
from datetime import datetime
from flask import session
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz, process
from typing import Tuple, List, Dict, Optional


class EcommerceBot:
    def __init__(self):
        self.product_database = {}
        self.faq_database = {}
        self.orders_database = {}
        self.current_context = None
        self.search_cache = {}
        
        # === ROZSZERZONE SŁOWNIKI DOMENOWE ===
        self.AUTOMOTIVE_DICTIONARY = {
            'brands': [
                'bosch', 'mann', 'brembo', 'ate', 'ferodo', 'trw', 'textar',
                'bilstein', 'kyb', 'sachs', 'monroe', 'ngk', 'denso', 'champion',
                'varta', 'exide', 'yuasa', 'castrol', 'mobil', 'shell', 'total',
                'motul', 'liqui moly', 'mahle', 'continental', 'zimmermann',
                'ebc', 'hiflo', 'kn', 'bmc', 'did', 'rk', 'regina', 'galfer',
                'delphi', 'beru', 'lucas', 'hella', 'valeo', 'luk', 'schaeffler',
                'bmw'
            ],
            'luxury_brands': [
                'ferrari', 'lamborghini', 'porsche', 'bentley', 'rolls-royce',
                'maserati', 'aston martin', 'mclaren', 'bugatti', 'pagani',
                'koenigsegg', 'lotus', 'alpine', 'alfa romeo'
            ],
            'categories': [
                'klocki', 'klocek', 'tarcza', 'tarczy', 'filtr', 'filtry', 
                'amortyzator', 'amortyzatory', 'świeca', 'świece', 'akumulator', 
                'akumulatory', 'olej', 'oleje', 'hamulce', 'hamulcowe', 
                'zawieszenie', 'zapłon', 'zapłonowa', 'elektryka', 'łańcuch', 
                'napęd', 'napędowy', 'sprzęgło', 'rozrząd', 'pasek', 'chłodzenie',
                'wydech', 'tłumik', 'katalizator', 'wahacz', 'łożysko', 'piasta',
                'opony', 'opona', 'felgi', 'felga', 'koła', 'koło'
            ],
            'car_models': [
                'golf', 'passat', 'polo', 'tiguan', 'touran', 'caddy', 'transporter',
                'corolla', 'yaris', 'avensis', 'rav4', 'hilux', 'camry', 'auris',
                'focus', 'fiesta', 'mondeo', 'kuga', 'transit', 'ranger', 'mustang',
                'astra', 'corsa', 'insignia', 'mokka', 'zafira', 'vectra', 'meriva',
                'clio', 'megane', 'scenic', 'captur', 'kadjar', 'trafic', 'master',
                '308', '208', '3008', '5008', 'partner', 'boxer', 'expert',
                'civic', 'accord', 'crv', 'jazz', 'hrv', 'odyssey', 'pilot',
                'octavia', 'fabia', 'superb', 'kodiaq', 'karoq', 'scala', 'kamiq',
                'mazda3', 'mazda6', 'cx5', 'cx3', 'mx5', 'cx30', 'cx9',
                'i30', 'i20', 'tucson', 'santa', 'kona', 'ioniq', 'genesis'
            ],
            'model_codes': [
                r'^[A-Z0-9]{2,}\d{3,}',  # np. E90, W204
                r'^\d{3,4}[A-Z]{1,3}',   # np. 320i, 200CDI
                r'^[A-Z]{1,3}\d{1,3}$'   # np. A4, C200
            ],
            'common_terms': [
                'przód', 'tył', 'przedni', 'tylny', 'lewy', 'prawy',
                'diesel', 'benzyna', 'tdi', 'tsi', 'cdi', 'hdi', 'tdci',
                'sport', 'racing', 'premium', 'heavy', 'duty', 'performance',
                'komplet', 'zestaw', 'para', 'sztuka', 'szt', 'oryginał',
                'zamiennik', 'oe', 'oem', 'aftermarket', 'tuning',
                'zimowe', 'letnie', 'całoroczne', 'wielosezonowe'
            ],
            'motorcycle_terms': [
                'yamaha', 'honda', 'suzuki', 'kawasaki', 'ducati', 'bmw',
                'harley', 'davidson', 'triumph', 'aprilia', 'ktm', 'husqvarna',
                'cbr', 'gsx', 'ninja', 'panigale', 'sportster', 'street',
                'r1', 'r6', 'r3', 'mt07', 'mt09', 'mt10', 'fz6', 'fz1'
            ]
        }
        
        # Rozszerzony słownik polski
        self.POLISH_DICTIONARY = {
            'część', 'części', 'samochód', 'auto', 'pojazd', 'silnik',
            'skrzynia', 'bieg', 'koło', 'koła', 'opona', 'opony',
            'szyba', 'lusterko', 'drzwi', 'maska', 'bagażnik',
            'kierownica', 'deska', 'rozdzielcza', 'fotel', 'siedzenie',
            'zderzak', 'błotnik', 'reflektor', 'lampa', 'światło',
            'wycieraczka', 'pióro', 'klapa', 'próg', 'słupek',
            'zimowe', 'letnie', 'całoroczne', 'wielosezonowe',
            'sportowe', 'terenowe', 'miejskie', 'szosowe'
        }
        
        self.initialize_data()
    
    def initialize_data(self):
        """Inicjalizuje kompletną bazę danych dla branży motoryzacyjnej"""
        
        # Rozszerzona baza 70+ produktów
        self.product_database = {
            'products': [
                # === SAMOCHODY OSOBOWE - KLOCKI HAMULCOWE ===
                {'id': 'KH001', 'name': 'Klocki hamulcowe przód Bosch BMW E90 320i', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'Bosch', 'model': '0986494104', 'price': 189.00, 'stock': 45},
                {'id': 'KH002', 'name': 'Klocki hamulcowe tył ATE Mercedes W204 C200', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'ATE', 'model': '13.0460-7218', 'price': 156.00, 'stock': 38},
                {'id': 'KH003', 'name': 'Klocki hamulcowe Ferodo Audi A4 B8 2.0 TDI', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'Ferodo', 'model': 'FDB4050', 'price': 245.00, 'stock': 22},
                {'id': 'KH004', 'name': 'Klocki hamulcowe TRW VW Golf VII 1.4 TSI', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'TRW', 'model': 'GDB1748', 'price': 135.00, 'stock': 67},
                {'id': 'KH005', 'name': 'Klocki hamulcowe Brembo Toyota Corolla E12', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'Brembo', 'model': 'P83052', 'price': 156.00, 'stock': 73},
                {'id': 'KH006', 'name': 'Klocki hamulcowe przód Textar Ford Focus MK3', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'Textar', 'model': '2456701', 'price': 178.00, 'stock': 41},
                {'id': 'KH007', 'name': 'Klocki hamulcowe ceramiczne ATE BMW M3 E92', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'ATE', 'model': '13.0470-7241', 'price': 845.00, 'stock': 8},
                
                # TARCZE HAMULCOWE
                {'id': 'TH001', 'name': 'Tarcza hamulcowa przednia Brembo BMW E90 320mm', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'Brembo', 'model': '09.9772.11', 'price': 420.00, 'stock': 18},
                {'id': 'TH002', 'name': 'Tarcza hamulcowa tylna ATE Mercedes W204 300mm', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'ATE', 'model': '24.0330-0184', 'price': 285.00, 'stock': 25},
                {'id': 'TH003', 'name': 'Tarcza hamulcowa Zimmermann VW Golf VII przód 312mm', 'category': 'hamulce', 'machine': 'osobowy', 'brand': 'Zimmermann', 'model': '100.3234.20', 'price': 198.00, 'stock': 34},
                
                # FILTRY
                {'id': 'FO001', 'name': 'Filtr oleju Mann HU719/7x BMW N47 N57 diesel', 'category': 'filtry', 'machine': 'osobowy', 'brand': 'Mann', 'model': 'HU719/7x', 'price': 62.00, 'stock': 120},
                {'id': 'FO002', 'name': 'Filtr oleju Mahle OX371D Mercedes OM651 2.2 CDI', 'category': 'filtry', 'machine': 'osobowy', 'brand': 'Mahle', 'model': 'OX371D', 'price': 45.00, 'stock': 89},
                {'id': 'FO003', 'name': 'Filtr oleju Bosch F026407022 VW 1.9 2.0 TDI', 'category': 'filtry', 'machine': 'osobowy', 'brand': 'Bosch', 'model': 'F026407022', 'price': 38.00, 'stock': 156},
                {'id': 'FP001', 'name': 'Filtr paliwa Bosch F026402836 PSA 1.6 2.0 HDI', 'category': 'filtry', 'machine': 'osobowy', 'brand': 'Bosch', 'model': 'F026402836', 'price': 89.00, 'stock': 85},
                {'id': 'FA001', 'name': 'Filtr powietrza K&N 33-2990 sportowy uniwersalny', 'category': 'filtry', 'machine': 'uniwersalny', 'brand': 'K&N', 'model': '33-2990', 'price': 285.00, 'stock': 35},
                {'id': 'FA002', 'name': 'Filtr powietrza Mann C2774/1 BMW E90 E91 E92', 'category': 'filtry', 'machine': 'osobowy', 'brand': 'Mann', 'model': 'C2774/1', 'price': 67.00, 'stock': 89},
                {'id': 'FK001', 'name': 'Filtr kabinowy węglowy Mann CUK2939 Audi A4 A6', 'category': 'filtry', 'machine': 'osobowy', 'brand': 'Mann', 'model': 'CUK2939', 'price': 95.00, 'stock': 68},
                
                # AMORTYZATORY
                {'id': 'AM001', 'name': 'Amortyzator przód Bilstein B4 VW Golf VII 1.4 TSI', 'category': 'zawieszenie', 'machine': 'osobowy', 'brand': 'Bilstein', 'model': '22-266767', 'price': 520.00, 'stock': 15},
                {'id': 'AM002', 'name': 'Amortyzator tył KYB Excel-G Ford Focus MK3 1.6', 'category': 'zawieszenie', 'machine': 'osobowy', 'brand': 'KYB', 'model': '349034', 'price': 385.00, 'stock': 24},
                {'id': 'AM003', 'name': 'Amortyzator przód Sachs Opel Astra J 1.7 CDTI', 'category': 'zawieszenie', 'machine': 'osobowy', 'brand': 'Sachs', 'model': '314896', 'price': 425.00, 'stock': 19},
                
                # ŚWIECE
                {'id': 'SZ001', 'name': 'Świeca zapłonowa NGK Laser Iridium ILZKR7B11', 'category': 'zapłon', 'machine': 'osobowy', 'brand': 'NGK', 'model': 'ILZKR7B11', 'price': 45.00, 'stock': 280},
                {'id': 'SZ002', 'name': 'Świeca zapłonowa Bosch Platinum Plus FR7DPP33', 'category': 'zapłon', 'machine': 'osobowy', 'brand': 'Bosch', 'model': 'FR7DPP33', 'price': 38.00, 'stock': 320},
                {'id': 'SZ003', 'name': 'Świeca żarowa Beru PSG006 Mercedes 2.2 CDI', 'category': 'zapłon', 'machine': 'osobowy', 'brand': 'Beru', 'model': 'PSG006', 'price': 78.00, 'stock': 145},
                
                # AKUMULATORY
                {'id': 'AK001', 'name': 'Akumulator Varta Blue Dynamic 74Ah 680A E12', 'category': 'elektryka', 'machine': 'osobowy', 'brand': 'Varta', 'model': 'E12', 'price': 420.00, 'stock': 38},
                {'id': 'AK002', 'name': 'Akumulator Bosch S4 Silver 60Ah 540A S4005', 'category': 'elektryka', 'machine': 'osobowy', 'brand': 'Bosch', 'model': 'S4005', 'price': 350.00, 'stock': 45},
                
                # OLEJE
                {'id': 'OL001', 'name': 'Olej silnikowy Castrol Edge 5W30 Titanium FST 5L', 'category': 'oleje', 'machine': 'osobowy', 'brand': 'Castrol', 'model': 'Edge 5W30', 'price': 165.00, 'stock': 92},
                {'id': 'OL002', 'name': 'Olej silnikowy Mobil 1 ESP 0W40 syntetyczny 4L', 'category': 'oleje', 'machine': 'osobowy', 'brand': 'Mobil', 'model': 'ESP 0W40', 'price': 189.00, 'stock': 78},
                {'id': 'OL003', 'name': 'Olej silnikowy Shell Helix Ultra 5W40 API SN 5L', 'category': 'oleje', 'machine': 'osobowy', 'brand': 'Shell', 'model': 'Helix Ultra', 'price': 145.00, 'stock': 110},
                
                # === MOTOCYKLE ===
                {'id': 'MKH001', 'name': 'Klocki hamulcowe EBC Yamaha R6 2003-2016 przód', 'category': 'hamulce', 'machine': 'motocykl', 'brand': 'EBC', 'model': 'FA252HH', 'price': 145.00, 'stock': 32},
                {'id': 'MLN001', 'name': 'Łańcuch napędowy DID 520VX3 Yamaha R6 gold', 'category': 'napęd', 'machine': 'motocykl', 'brand': 'DID', 'model': '520VX3-114', 'price': 345.00, 'stock': 38},
                
                # === SAMOCHODY DOSTAWCZE ===
                {'id': 'DKH001', 'name': 'Klocki hamulcowe Textar Mercedes Sprinter 906 przód', 'category': 'hamulce', 'machine': 'dostawczy', 'brand': 'Textar', 'model': '2430801', 'price': 267.00, 'stock': 34},
                {'id': 'DFO001', 'name': 'Filtr oleju Mann W712/94 Sprinter Vito 2.2 CDI', 'category': 'filtry', 'machine': 'dostawczy', 'brand': 'Mann', 'model': 'W712/94', 'price': 78.00, 'stock': 89}
            ],
            'categories': {
                'hamulce': '🔧 Układ hamulcowy',
                'filtry': '🔍 Filtry',
                'zawieszenie': '🚗 Zawieszenie',
                'zapłon': '⚡ Układ zapłonowy',
                'elektryka': '🔋 Elektryka',
                'oleje': '🛢️ Oleje i płyny',
                'napęd': '⛓️ Układ napędowy'
            },
            'machines': {
                'osobowy': '🚗 Samochód osobowy',
                'dostawczy': '🚐 Samochód dostawczy',
                'motocykl': '🏍️ Motocykl',
                'uniwersalny': '🔧 Uniwersalne'
            }
        }
        
        # Kompletna baza FAQ
        self.faq_database = [
            # DOSTAWA
            {
                'id': 'FAQ001',
                'keywords': ['dostawa', 'wysyłka', 'kiedy', 'czas dostawy', 'kurier', 'paczka'],
                'question': 'Jaki jest czas dostawy części samochodowych?',
                'answer': '🚚 Dostawa kurierem: 24h dla produktów na stanie\n📦 Paczkomaty: 1-2 dni robocze\n🌍 Dostawa zagraniczna: 3-5 dni',
                'category': 'dostawa'
            },
            {
                'id': 'FAQ002',
                'keywords': ['koszt dostawy', 'ile kosztuje', 'darmowa', 'przesyłka'],
                'question': 'Ile kosztuje dostawa?',
                'answer': '💰 Standardowa dostawa: 15 zł\n🎁 Darmowa dostawa od 300 zł\n📦 Paczkomaty: 12 zł',
                'category': 'dostawa'
            },
            
            # ZWROTY
            {
                'id': 'FAQ003',
                'keywords': ['zwrot', 'reklamacja', 'wymiana', 'gwarancja'],
                'question': 'Jak zwrócić lub wymienić część?',
                'answer': '↩️ 14 dni na zwrot bez podania przyczyny\n🔄 Darmowa wymiana na inną część\n📝 24 miesiące gwarancji producenta',
                'category': 'zwroty'
            },
            {
                'id': 'FAQ004',
                'keywords': ['uszkodzony', 'wadliwy', 'nie działa', 'zepsuty'],
                'question': 'Co zrobić gdy część jest uszkodzona?',
                'answer': '📞 Zgłoś w ciągu 24h od otrzymania\n📸 Wyślij zdjęcia uszkodzenia\n🚚 Odbierzemy i wyślemy nową część gratis',
                'category': 'zwroty'
            }
        ]
        
        # Przykładowe zamówienia
        self.orders_database = {
            'MOT-2024001': {
                'status': '🚚 W drodze',
                'details': 'Dostawa jutro do 12:00',
                'tracking': 'DPD: 0123456789',
                'items': ['Klocki hamulcowe Bosch BMW E90']
            }
        }
    def calculate_token_validity(self, query_tokens: List[str]) -> float:
        """ZOPTYMALIZOWANA funkcja - oblicza wskaźnik poprawności tokenów (0-100) z lepszą obsługą literówek"""
        if not query_tokens:
            return 0
        
        validity_scores = []
        
        for token in query_tokens:
            token_lower = token.lower()
            score = 0
            
            # Sprawdź w słowniku marek zwykłych (waga 100)
            if token_lower in self.AUTOMOTIVE_DICTIONARY['brands']:
                score = 100
            # Sprawdź marki luksusowe (waga 95)
            elif token_lower in self.AUTOMOTIVE_DICTIONARY['luxury_brands']:
                score = 95
            # Sprawdź w słowniku kategorii (waga 90)
            elif token_lower in self.AUTOMOTIVE_DICTIONARY['categories']:
                score = 90
            # Sprawdź modele samochodów (waga 85)
            elif token_lower in self.AUTOMOTIVE_DICTIONARY['car_models']:
                score = 85
            # Sprawdź terminy motocyklowe (waga 80)
            elif token_lower in self.AUTOMOTIVE_DICTIONARY['motorcycle_terms']:
                score = 80
            # Sprawdź w common terms (waga 70)
            elif token_lower in self.AUTOMOTIVE_DICTIONARY['common_terms']:
                score = 70
            # Sprawdź czy pasuje do wzorca modelu (waga 60)
            elif any(re.match(pattern, token.upper()) for pattern in self.AUTOMOTIVE_DICTIONARY['model_codes']):
                score = 60
            # Sprawdź czy to prawidłowe polskie słowo (waga 50)
            elif token_lower in self.POLISH_DICTIONARY:
                score = 50
            # ULEPSZONE: Sprawdź literówki w markach i kategoriach
            else:
                # Prioritet dla marek i kategorii (najważniejsze)
                priority_words = (
                    self.AUTOMOTIVE_DICTIONARY['brands'] +
                    self.AUTOMOTIVE_DICTIONARY['luxury_brands'] +
                    self.AUTOMOTIVE_DICTIONARY['categories']
                )
                
                min_distance = float('inf')
                best_match_type = None
                
                # Sprawdź literówki w priorytetowych słowach
                for known_word in priority_words:
                    distance = self.levenshtein_distance(token_lower, known_word)
                    if distance < min_distance:
                        min_distance = distance
                        if known_word in self.AUTOMOTIVE_DICTIONARY['brands'] + self.AUTOMOTIVE_DICTIONARY['luxury_brands']:
                            best_match_type = 'brand'
                        else:
                            best_match_type = 'category'
                
                # Jeśli nie znaleziono dobrej literówki w priorytetowych, sprawdź resztę
                if min_distance > 2:
                    other_words = (
                        self.AUTOMOTIVE_DICTIONARY['car_models'] +
                        self.AUTOMOTIVE_DICTIONARY['common_terms'] +
                        list(self.POLISH_DICTIONARY)
                    )
                    
                    for known_word in other_words:
                        distance = self.levenshtein_distance(token_lower, known_word)
                        if distance < min_distance:
                            min_distance = distance
                            best_match_type = 'other'
                
                # Przyznaj punkty na podstawie odległości i typu
                if min_distance <= 1:
                    if best_match_type == 'brand':
                        score = 85  # Literówka w marce
                    elif best_match_type == 'category':
                        score = 75  # Literówka w kategorii
                    else:
                        score = 60  # Literówka w innym słowie
                elif min_distance <= 2:
                    if best_match_type == 'brand':
                        score = 70  # Większa literówka w marce
                    elif best_match_type == 'category':
                        score = 60  # Większa literówka w kategorii
                    else:
                        score = 40  # Większa literówka w innym słowie
                elif min_distance <= 3:
                    if best_match_type in ['brand', 'category']:
                        score = 30  # Bardzo duża literówka ale w ważnym słowie
                    else:
                        score = 20
                else:
                    score = 0
            
            validity_scores.append(score)
        
        return sum(validity_scores) / len(validity_scores)
    
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """Oblicza odległość Levenshteina między dwoma stringami"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def is_structural_query(self, tokens: List[str]) -> bool:
        """NAPRAWIONA FUNKCJA - Wykrywa strukturalne zapytania (kategoria + nieznana marka)"""
        has_category = False
        has_unknown_brand = False
        
        print(f"[STRUCTURAL DEBUG] Tokens: {tokens}")
        
        # Sprawdź czy zawiera znaną kategorię
        for token in tokens:
            if token.lower() in self.AUTOMOTIVE_DICTIONARY['categories']:
                has_category = True
                print(f"[STRUCTURAL DEBUG] Found category: {token}")
                break
        
        # Sprawdź czy zawiera nieznane słowo (potencjalna marka)
        for token in tokens:
            token_lower = token.lower()
            print(f"[STRUCTURAL DEBUG] Checking token: {token_lower}")
            
            # Skip znane słowa
            if (token_lower in self.AUTOMOTIVE_DICTIONARY['brands'] or
                token_lower in self.AUTOMOTIVE_DICTIONARY['luxury_brands'] or
                token_lower in self.AUTOMOTIVE_DICTIONARY['categories'] or
                token_lower in self.AUTOMOTIVE_DICTIONARY['common_terms'] or
                token_lower in self.POLISH_DICTIONARY):
                print(f"[STRUCTURAL DEBUG] Skipping known word: {token_lower}")
                continue
            
            # NAPRAWKA: Skip model codes - nie traktuj ich jako nieznane marki
            if any(re.match(pattern, token.upper()) for pattern in self.AUTOMOTIVE_DICTIONARY['model_codes']):
                print(f"[STRUCTURAL DEBUG] Skipping model code: {token_lower}")
                continue
                
            # Jeśli słowo wygląda sensownie (bez cyfr, przyzwoita długość)
            if (len(token) >= 3 and len(token) <= 15 and 
                token.isalpha() and
                not any(pattern in token_lower for pattern in ['qwer', 'asdf', 'zxcv'])):
                print(f"[STRUCTURAL DEBUG] Found unknown brand: {token_lower}")
                has_unknown_brand = True
                break
        
        result = has_category and has_unknown_brand
        print(f"[STRUCTURAL DEBUG] Result: category={has_category}, unknown={has_unknown_brand}, structural={result}")
        return result
    
    def is_obvious_nonsense(self, tokens: List[str], token_validity: float) -> bool:
        """NAPRAWIONA - Wykrywa oczywisty nonsens ale NIGDY nie blokuje zapytań z wartościowymi tokenami biznesowymi"""
        
        # === NOWY FILTR - BRAK TERMINÓW PRODUKTOWYCH ===
        has_product_term = any(
            token.lower() in self.AUTOMOTIVE_DICTIONARY['brands'] or
            token.lower() in self.AUTOMOTIVE_DICTIONARY['categories'] or
            token.lower() in self.AUTOMOTIVE_DICTIONARY['car_models']
            for token in tokens
        )
        
        if not has_product_term:
            return True  # Brak terminów produktowych = odfiltrowane
        
        # === PANCERNA OCHRONA PRZED FAŁSZYWYMI ALARMAMI ===
        # Jeśli zapytanie zawiera JAKIKOLWIEK wartościowy token biznesowy - NIE JEST nonsensem
        business_value_tokens = 0
        
        for token in tokens:
            token_lower = token.lower()
            
            # Znane marki automotive
            if (token_lower in self.AUTOMOTIVE_DICTIONARY['brands'] or
                token_lower in self.AUTOMOTIVE_DICTIONARY['luxury_brands']):
                business_value_tokens += 2  # Marki = wysoka wartość
                
            # Znane kategorie produktów
            elif token_lower in self.AUTOMOTIVE_DICTIONARY['categories']:
                business_value_tokens += 2  # Kategorie = wysoka wartość
                
            # Polskie słowa branżowe
            elif token_lower in self.POLISH_DICTIONARY:
                business_value_tokens += 1
                
            # Kody produktów (cyfry + litery)
            elif (len(token) >= 3 and 
                  any(c.isdigit() for c in token) and 
                  any(c.isalpha() for c in token)):
                business_value_tokens += 1
                
            # Sensowne literówki znanych marek (odległość <= 2)
            else:
                all_known_brands = (
                    self.AUTOMOTIVE_DICTIONARY['brands'] +
                    self.AUTOMOTIVE_DICTIONARY['luxury_brands'] +
                    self.AUTOMOTIVE_DICTIONARY['categories']
                )
                
                for known_brand in all_known_brands:
                    if self.levenshtein_distance(token_lower, known_brand) <= 2:
                        business_value_tokens += 1
                        break
        
        # PANCERNA ZASADA: Jeśli są wartościowe tokeny - NIGDY nonsens
        if business_value_tokens >= 1:
            print(f"[NONSENSE] OCHRONA: {business_value_tokens} wartościowych tokenów - NIE nonsens")
            return False
        
        # === STARA LOGIKA DLA RZECZYWISTEGO NONSENSU ===
        # Tylko jeśli NIE MA żadnych wartościowych tokenów
        
        # Wielosłowne zapytania rzadko są nonsensem
        if len(tokens) > 1:
            return False  # Wielosłowne = daj szansę
        
        # Dla pojedynczych tokenów
        if len(tokens) == 1:
            token = tokens[0].lower()
            
            # Podstawowe filtry długości
            if len(token) < 2 or len(token) > 25:
                return True
            
            # Oczywiste wzorce klawiaturowe
            keyboard_patterns = ['qwerty', 'qwertyui', 'asdf', 'asdfgh', 'qwe', 'asd', 'zxc']
            if any(pattern in token for pattern in keyboard_patterns):
                return True
            
            # Powtarzające się sekwencje (asdasd, abcabc)
            if len(token) >= 6:
                for i in range(2, len(token)//2 + 1):
                    pattern = token[:i]
                    if token == pattern * (len(token)//i) and len(token) >= i*2:
                        return True
            
            # Bardzo mała różnorodność znaków w długim słowie
            unique_chars = len(set(token))
            if len(token) > 6 and unique_chars <= 3:
                return True
                
            # Brak samogłosek w długich słowach
            polish_vowels = set('aeiouąęy')
            if len(token) > 6 and not any(c in polish_vowels for c in token):
                return True
            
            # Kombinacja niskiej entropii i niskiej valid
            unique_ratio = unique_chars / len(token) if len(token) > 0 else 0
            if unique_ratio < 0.3 and token_validity < 15:  # Bardzo restrykcyjne progi
                return True
                    
        return False

    def get_fuzzy_product_matches_internal(self, query: str, machine_filter: Optional[str] = None) -> List[Tuple]:
        """NAPRAWIONA - Algorytm który WYKLUCZA metadane i poprawnie matchuje"""
        matches = []
        query_tokens = query.lower().split()
        
        for product in self.product_database['products']:
            if machine_filter and product['machine'] != machine_filter and product['machine'] != 'uniwersalny':
                continue
            
            # KLUCZOWA NAPRAWA: Tylko istotne pola dla matchowania
            # WYKLUCZA: stock, price, id (metadane)
            product_text = f"{product['name']} {product['brand']} {product['model']} {product['category']}"
            product_tokens = product_text.lower().split()
            
            # NOWY ALGORYTM - Precyzyjne dopasowanie per token
            token_scores = []
            
            for q_token in query_tokens:
                best_token_match = 0
                
                # NAPRAWKA: Wykluczenie matchowania liczb do stock/price
                if q_token.isdigit() and len(q_token) <= 3:
                    # Krótkie liczby (jak "89") mogą być przypadkowe
                    # Sprawdź czy to prawdopodobnie część kodu produktu
                    has_letters_context = any(
                        not token.isdigit() and len(token) > 1 
                        for token in query_tokens
                    )
                    if not has_letters_context:
                        # Sama liczba bez kontekstu - skip
                        continue
                
                # Sprawdź każdy token produktu
                for p_token in product_tokens:
                    # NAPRAWKA: Nie dopasowuj prostych liczb do stocku
                    if q_token.isdigit() and p_token.isdigit() and len(q_token) <= 3:
                        continue  # Skip przypadkowe dopasowania liczb
                    
                    if q_token == p_token:
                        # Dokładne dopasowanie = 100%
                        best_token_match = 100
                        break
                    elif p_token.startswith(q_token) and len(q_token) >= 2:
                        # Prefix match (np. "gol" -> "golf")
                        match_ratio = len(q_token) / len(p_token)
                        best_token_match = max(best_token_match, 95 * match_ratio)
                    elif q_token.startswith(p_token) and len(p_token) >= 2:
                        # Suffix match
                        match_ratio = len(p_token) / len(q_token)
                        best_token_match = max(best_token_match, 90 * match_ratio)
                    else:
                        # Fuzzy match - tylko dla sensownych podobieństw
                        similarity = fuzz.ratio(q_token, p_token)
                        if similarity > 85:  # Podwyższony próg
                            best_token_match = max(best_token_match, similarity * 0.95)
                        elif similarity > 75:
                            best_token_match = max(best_token_match, similarity * 0.85)
                
                token_scores.append(best_token_match)
            
            # Oblicz wynik końcowy tylko jeśli są sensowne dopasowania
            if not token_scores or all(score == 0 for score in token_scores):
                continue
                
            # Średnia ważona
            base_score = sum(token_scores) / len(token_scores)
            
            # Bonus za precyzję - bez zmian
            if len(query_tokens) > 1:
                if all(score > 70 for score in token_scores):
                    base_score *= 1.3
                elif all(score > 60 for score in token_scores):
                    base_score *= 1.2
                elif all(score > 50 for score in token_scores):
                    base_score *= 1.1
                elif any(score < 20 for score in token_scores):
                    base_score *= 0.8
            
            # Dodatkowe bonusy kontekstowe - bez zmian
            bonus = 0
            brand_lower = product['brand'].lower()
            if brand_lower in query or query in brand_lower:
                bonus += 15
            
            model_lower = product['model'].lower()
            for q_token in query_tokens:
                if len(q_token) > 2 and q_token in model_lower:
                    bonus += 10
                    break
            
            category = product['category'].lower()
            for q_token in query_tokens:
                if q_token in category:
                    bonus += 10
                    break
            
            final_score = min(100, base_score + bonus)
            
            # PODWYŻSZONY PRÓG - eliminuje słabe dopasowania
            if final_score >= 35:  # Zwiększone z 25
                matches.append((product, round(final_score)))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def analyze_query_intent(self, query: str) -> Dict:
        """OSTATECZNA NAPRAWA - Nonsens sprawdzany przed token_validity >= 35"""
        query_lower = query.lower().strip()
        query_tokens = query_lower.split()
        
        # Oblicz token validity
        token_validity = self.calculate_token_validity(query_tokens)
        
        # NOWA LOGIKA - Wykryj zapytania strukturalne
        is_structural = self.is_structural_query(query_tokens)
        
        # Specjalna obsługa marek luksusowych
        has_luxury_brand = any(
            brand in query_lower 
            for brand in self.AUTOMOTIVE_DICTIONARY['luxury_brands']
        )
        
        # ROZSZERZONA detekcja kodów produktów
        potential_product_codes = []
        short_codes = []  # NOWE: krótkie kody (1-3 znaki)
        
        for token in query_tokens:
            token_upper = token.upper()
            if (re.match(r'^[A-Z]\d{2,}', token_upper) or      
                re.match(r'^\d{4,}', token) or                  
                re.match(r'^[A-Z]{2,}\d{2,}', token_upper) or   
                (len(token) >= 3 and                            
                 any(c.isdigit() for c in token) and            
                 not token.lower() in ['100', '200', '300'])):  
                potential_product_codes.append(token)
            # NOWE: Wykryj krótkie kody (1-3 znaki alfanumeryczne)
            elif (len(token) >= 1 and len(token) <= 3 and 
                  (token.isdigit() or (token.isalnum() and any(c.isdigit() for c in token)))):
                short_codes.append(token)
        
        # Sprawdź czy kody istnieją w bazie
        has_nonexistent_code = False
        has_nonexistent_short_code = False
        
        # Sprawdź długie kody
        if potential_product_codes:
            for code in potential_product_codes:
                code_exists = False
                for product in self.product_database['products']:
                    if (code.upper() in product['model'].upper() or 
                        code.upper() in product['id'] or
                        code.upper() in product['name'].upper()):
                        code_exists = True
                        break
                
                if not code_exists and len(code) >= 3:
                    has_nonexistent_code = True
                    break
        
        # NOWE: Sprawdź krótkie kody (tylko jeśli są z marką/kategorią)
        if short_codes and len(query_tokens) >= 2:
            has_known_context = any(
                token.lower() in self.AUTOMOTIVE_DICTIONARY['brands'] or
                token.lower() in self.AUTOMOTIVE_DICTIONARY['categories'] or
                token.lower() in self.AUTOMOTIVE_DICTIONARY['luxury_brands']
                for token in query_tokens
            )
            
            if has_known_context:
                for code in short_codes:
                    code_exists = False
                    for product in self.product_database['products']:
                        if (code.upper() in product['model'].upper() or 
                            code.upper() in product['id'] or
                            code.upper() in product['name'].upper()):
                            code_exists = True
                            break
                    
                    if not code_exists:
                        has_nonexistent_short_code = True
                        break
        
        # Znajdź najlepsze dopasowanie
        matches = self.get_fuzzy_product_matches_internal(query_lower)
        best_match_score = matches[0][1] if matches else 0
        
        # === OSTATECZNA NAPRAWA KLASYFIKACJI ===
        
        # 1. Bardzo wysokie dopasowanie = dokładne trafienie
        if best_match_score >= 90:
            confidence_level = 'HIGH'
            suggestion_type = 'exact_match'
            ga4_event = None
        
        # 2. NOWY: Zapytanie strukturalne (kategoria + nieznana marka)
        elif is_structural:
            confidence_level = 'NO_MATCH'
            suggestion_type = 'structural_missing'
            ga4_event = 'search_lost_demand'
        
        # 3. Nieistniejący kod produktu (długi)
        elif has_nonexistent_code and token_validity >= 40:
            confidence_level = 'NO_MATCH'
            suggestion_type = 'product_code_missing'
            ga4_event = 'search_lost_demand'
        
        # 4. NOWE: Nieistniejący krótki kod (a1, 55, x1, itp.)
        elif has_nonexistent_short_code and token_validity >= 70:
            confidence_level = 'NO_MATCH'
            suggestion_type = 'short_code_missing'
            ga4_event = 'search_lost_demand'
        
        # 5. Istniejący kod ale średnie dopasowanie - uznaj za trafienie
        elif potential_product_codes and best_match_score >= 40:
            confidence_level = 'MEDIUM'
            suggestion_type = 'code_found'
            ga4_event = 'search_typo_corrected'
        
        # 6. Marka luksusowa bez produktów
        elif has_luxury_brand and best_match_score < 60:
            confidence_level = 'NO_MATCH'
            suggestion_type = 'luxury_brand_missing'
            ga4_event = 'search_lost_demand'
        
        # 7. Wysokie dopasowanie
        elif best_match_score >= 80:
            confidence_level = 'HIGH'
            suggestion_type = 'good_match'
            ga4_event = None
        
        # 8. Średnie dopasowanie + sensowne słowa = literówka
        elif best_match_score >= 70 and token_validity >= 50:
            confidence_level = 'MEDIUM'
            suggestion_type = 'typo_correction'
            ga4_event = 'search_typo_corrected'
        
        # 9. Model missing (wielosłowne + wysokie validity + słabe dopasowanie)
        elif (len(query_tokens) >= 2 and 
              token_validity >= 70 and 
              best_match_score < 70 and
              not potential_product_codes and
              not short_codes):
            confidence_level = 'NO_MATCH'
            suggestion_type = 'model_missing'
            ga4_event = 'search_lost_demand'
        
        # 10. KRYTYCZNE - Oczywisty nonsens PRZED sprawdzaniem token_validity
        elif self.is_obvious_nonsense(query_tokens, token_validity):
            confidence_level = 'LOW'
            suggestion_type = 'nonsensical'
            ga4_event = 'search_failure'
        
        # 11. Sensowne słowa ale brak dopasowania (DOPIERO PO nonsens check)
        elif token_validity >= 35:
            confidence_level = 'NO_MATCH'
            suggestion_type = 'product_missing'
            ga4_event = 'search_lost_demand'
        
        # 12. Graniczne przypadki
        elif token_validity >= 20:
            confidence_level = 'NO_MATCH'
            suggestion_type = 'unknown_brand'
            ga4_event = 'search_lost_demand'
        
        # 13. Fallback
        else:
            confidence_level = 'LOW'
            suggestion_type = 'nonsensical'
            ga4_event = 'search_failure'
        
        # Debug output
        print(f"[ANALYSIS] Query: '{query}'")
        print(f"  Token validity: {token_validity:.1f}")
        print(f"  Best match: {best_match_score:.1f}")
        print(f"  Is structural: {is_structural}")
        print(f"  Has luxury: {has_luxury_brand}")
        print(f"  Has code: {bool(potential_product_codes)}")
        print(f"  Has short code: {bool(short_codes)}")
        print(f"  Nonexistent code: {has_nonexistent_code}")
        print(f"  Nonexistent short code: {has_nonexistent_short_code}")
        print(f"  Nonsense check: {self.is_obvious_nonsense(query_tokens, token_validity)}")
        print(f"  Decision: {confidence_level} → {ga4_event}")
        
        return {
            'query': query,
            'tokens': query_tokens,
            'token_validity': round(token_validity, 2),
            'best_match_score': round(best_match_score, 2),
            'confidence_level': confidence_level,
            'suggestion_type': suggestion_type,
            'ga4_event': ga4_event,
            'has_luxury_brand': has_luxury_brand,
            'has_product_code': bool(potential_product_codes),
            'is_structural': is_structural,
            'is_nonsense': self.is_obvious_nonsense(query_tokens, token_validity),
            'matches': matches[:6] if matches else []
        }    
    
    
    def normalize_query(self, query: str) -> str:
        """Normalizacja zapytania z obsługą literówek"""
        query = query.lower().strip()
        
        # Podstawowe korekty literówek
        typo_corrections = {
            'kloki': 'klocki',
            'klocek': 'klocki',
            'filtr': 'filtr',
            'filetr': 'filtr',
            'amortyztor': 'amortyzator',
            'swica': 'świeca',
            'swieca': 'świeca',
            'gol': 'golf',
            'vw': 'volkswagen',
            'mb': 'mercedes',
            'yam': 'yamaha',
            'sprin': 'sprinter'
        }
        
        for typo, correction in typo_corrections.items():
            query = query.replace(typo, correction)
        
        return ' '.join(query.split())
    
    def get_fuzzy_product_matches(self, query: str, machine_filter: Optional[str] = None, 
                                  limit: int = 6, analyze_intent: bool = True) -> Tuple:
        """Ulepszona funkcja dopasowania z analizą intencji"""
        query = self.normalize_query(query)
        
        if analyze_intent:
            # Pełna analiza intencji
            analysis = self.analyze_query_intent(query)
            
            # Filtruj wyniki na podstawie confidence level
            if analysis['confidence_level'] == 'HIGH':
                products = [(p, s) for p, s in analysis['matches'][:limit]]
            elif analysis['confidence_level'] == 'MEDIUM':
                products = [(p, s) for p, s in analysis['matches'][:limit]]
            else:
                products = [(p, s) for p, s in analysis['matches'][:3]] if analysis['matches'] else []
            
            return (
                products,
                analysis['confidence_level'],
                analysis['suggestion_type'],
                analysis
            )
        else:
            # Stare zachowanie dla kompatybilności wstecznej
            matches = self.get_fuzzy_product_matches_internal(query, machine_filter)
            return matches[:limit]
    
    def get_fuzzy_faq_matches(self, query: str, limit: int = 5) -> List[Tuple]:
        """FAQ z predykcją znak-po-znaku + progresywny scoring"""
        query = self.normalize_query(query).lower()
        
        if len(query) < 2:
            return []
        
        matches = []
        
        for faq in self.faq_database:
            question_lower = faq['question'].lower()
            keywords_lower = [k.lower() for k in faq['keywords']]
            
            best_score = 0
            
            if query in question_lower:
                base = (len(query) / len(question_lower)) * 100
                if question_lower.startswith(query):
                    best_score = min(100, base + 30)
                else:
                    best_score = min(100, base + 15)
            
            for keyword in keywords_lower:
                if query in keyword:
                    base = (len(query) / len(keyword)) * 100
                    if keyword.startswith(query):
                        score = min(95, base + 25)
                    else:
                        score = min(90, base + 10)
                    best_score = max(best_score, score)
            
            if best_score == 0:
                if len(query) >= 4:
                    question_score = fuzz.partial_ratio(query, question_lower)
                    if question_score > 65:
                        best_score = question_score * 0.85
            
            if best_score >= 35:
                matches.append((faq, round(best_score)))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:limit]
    
    def determine_ga4_event(self, analysis: Dict) -> Optional[Dict]:
        """Określa które zdarzenie GA4 wysłać na podstawie analizy"""
        if not analysis['ga4_event']:
            return None
        
        event_data = {
            'event': analysis['ga4_event'],
            'params': {
                'query': analysis['query'],
                'token_validity': analysis['token_validity'],
                'best_match_score': analysis['best_match_score'],
                'confidence_level': analysis['confidence_level']
            }
        }
        
        # Dodaj specyficzne parametry dla różnych eventów
        if analysis['ga4_event'] == 'search_lost_demand':
            potential_product = self.extract_product_intent(analysis['query'])
            event_data['params']['potential_product'] = potential_product
            event_data['params']['priority'] = 'HIGH'
            if analysis.get('has_luxury_brand'):
                event_data['params']['luxury_brand'] = True
        
        elif analysis['ga4_event'] == 'search_failure':
            event_data['params']['reason'] = 'nonsensical_query'
        
        elif analysis['ga4_event'] == 'search_typo_corrected':
            if analysis['matches']:
                event_data['params']['suggested_product'] = analysis['matches'][0][0]['name']
        
        return event_data
    
    def extract_product_intent(self, query: str) -> str:
        """Próbuje wyekstrahować intencję produktu z zapytania"""
        tokens = query.lower().split()
        product_hints = []
        
        for token in tokens:
            if token in self.AUTOMOTIVE_DICTIONARY['categories']:
                product_hints.append(token)
            elif token in self.AUTOMOTIVE_DICTIONARY['brands']:
                product_hints.append(token)
            elif token in self.AUTOMOTIVE_DICTIONARY['luxury_brands']:
                product_hints.append(token)
        
        return ' '.join(product_hints) if product_hints else query
    
    def send_ga4_event(self, event_data: Dict) -> bool:
        """Wysyła zdarzenie do GA4"""
        try:
            GA4_MEASUREMENT_ID = "G-ECOMMERCE123"
            GA4_API_SECRET = "YOUR_API_SECRET_HERE"
            
            session_data = f"universal_soldier_{int(time.time() // 3600)}"
            client_id = hashlib.md5(session_data.encode()).hexdigest()
            
            url = "https://www.google-analytics.com/mp/collect"
            params = {
                'measurement_id': GA4_MEASUREMENT_ID,
                'api_secret': GA4_API_SECRET
            }
            
            payload = {
                "client_id": client_id,
                "events": [{
                    "name": event_data['event'],
                    "params": event_data['params']
                }]
            }
            
            response = requests.post(url, params=params, json=payload, timeout=5)
            
            if response.status_code == 204:
                print(f"[GA4] ✅ Event sent: {event_data['event']} for query: '{event_data['params']['query']}'")
                return True
            else:
                print(f"[GA4] ❌ Failed to send event. Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[GA4] 💥 Error sending event: {e}")
            return False
        
    def search_products(self, query: str, machine_filter: Optional[str] = None) -> List:
        """Wyszukiwanie produktów (kompatybilność wsteczna)"""
        result = self.get_fuzzy_product_matches(query, machine_filter, analyze_intent=False)
        if isinstance(result, tuple):
            return [product for product, score in result[0]]
        else:
            return [product for product, score in result]
    
    def search_faq(self, query: str) -> List:
        """Wyszukiwanie FAQ"""
        results = self.get_fuzzy_faq_matches(query, limit=10)
        return [faq for faq, score in results]
    
    def get_initial_greeting(self) -> Dict:
        """Powitanie"""
        return {
            'text_message': """🚗 **Witaj w Auto Parts Pro**

Jestem Twoim ekspertem od części samochodowych. 
Nasz inteligentny system rozpoznaje literówki i śledzi brakujące produkty!

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
    
    def handle_button_action(self, action: str) -> Dict:
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
                    {'text': '↩️ Powrót', 'action': 'main_menu'}
                ]
            }
        
        elif action.startswith('machine_'):
            machine_type = action.replace('machine_', '')
            session['machine_filter'] = machine_type
            
            return {
                'text_message': f"""✅ **Wybrany typ: {machine_type}**

Wpisz czego szukasz. System inteligentnie rozpozna Twoje zapytanie!""",
                'enable_input': True,
                'input_placeholder': 'np. klocki bosch, filtr mann...',
                'search_mode': True
            }
        
        elif action == 'faq_search':
            return {
                'text_message': """❓ **Centrum pomocy**

Zadaj pytanie:""",
                'enable_input': True,
                'input_placeholder': 'np. jak sprawdzić czy część pasuje...',
                'faq_mode': True
            }
        
        elif action == 'main_menu':
            return self.get_initial_greeting()
        
        elif action.startswith('faq_'):
            return self.handle_faq(action)
        
        elif action.startswith('show_full_card_'):
            product_id = action.replace('show_full_card_', '')
            return self.show_full_product_card(product_id)
        
        elif action.startswith('product_details_'):
            product_id = action.replace('product_details_', '')
            return self.show_product_details(product_id)
        
        elif action.startswith('add_to_cart_'):
            product_id = action.replace('add_to_cart_', '')
            return self.add_to_cart(product_id)
        
        elif action == 'notify_when_available':
            return {
                'text_message': """📧 **Powiadomienie o dostępności**

Zapisaliśmy Twoje zapytanie. Powiadomimy Cię gdy produkt będzie dostępny!""",
                'buttons': [
                    {'text': '🔄 Szukaj czegoś innego', 'action': 'search_product'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        return {
            'text_message': 'Wybierz opcję:',
            'buttons': [{'text': '↩️ Menu główne', 'action': 'main_menu'}]
        }
    
    def handle_faq(self, action: str) -> Dict:
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
            'buttons': [{'text': '↩️ Menu główne', 'action': 'main_menu'}]
        }
    
    def process_message(self, message: str) -> Dict:
        """Przetwarzanie wiadomości z NAPRAWIONĄ inteligentną analizą"""
        context = session.get('context', '')
        
        if session.get('machine_filter'):
            machine_filter = session.get('machine_filter')
            
            # Użyj nowej funkcji z analizą intencji
            products, confidence_level, suggestion_type, analysis = self.get_fuzzy_product_matches(
                message, machine_filter, limit=5, analyze_intent=True
            )
            
            # Wyślij odpowiednie zdarzenie GA4
            ga4_event = self.determine_ga4_event(analysis)
            if ga4_event:
                self.send_ga4_event(ga4_event)
            
            # NAPRAWIONE ODPOWIEDZI NA PODSTAWIE CONFIDENCE LEVEL
            if confidence_level == 'HIGH':
                if products:
                    products_text = "✅ **Znaleźliśmy produkty:**\n\n"
                    for product, score in products:
                        products_text += f"**{product['name']}**\n"
                        products_text += f"📊 Dopasowanie: {score}% | 💰 {product['price']:.2f} zł\n\n"
                    
                    return {
                        'text_message': products_text,
                        'confidence_level': confidence_level,
                        'buttons': self.create_product_buttons(products)
                    }
            
            elif confidence_level == 'MEDIUM':
                if products:
                    products_text = "🤔 **Czy chodziło Ci o:**\n\n"
                    for product, score in products[:3]:
                        products_text += f"**{product['name']}**\n"
                        products_text += f"📊 Dopasowanie: {score}% | 💰 {product['price']:.2f} zł\n\n"
                    products_text += "\n💡 *System automatycznie poprawił literówki*"
                    
                    return {
                        'text_message': products_text,
                        'confidence_level': confidence_level,
                        'buttons': self.create_product_buttons(products[:3])
                    }
            
            elif confidence_level == 'LOW':
                return {
                    'text_message': f"""❓ **Nie rozumiemy zapytania**

Sprawdź pisownię lub użyj innych słów.
Wpisana fraza: "{message}" """,
                    'confidence_level': confidence_level,
                    'buttons': [
                        {'text': '🔄 Spróbuj ponownie', 'action': 'search_product'},
                        {'text': '↩️ Menu główne', 'action': 'main_menu'}
                    ]
                }
            
            else:  # NO_MATCH - PRAWDZIWY UTRACONY POPYT!
                # NOWA obsługa dla różnych typów brakujących produktów
                if analysis.get('suggestion_type') == 'structural_missing':
                    message_text = f"""🔍 **Produkt spoza naszej oferty**

Szukana fraza: "{message}"
📊 System wykrył: kategoria + nieznana marka

✨ **Zapisaliśmy Twoje zapytanie!** 
Jeśli więcej osób będzie szukać tej marki, rozważymy dodanie do oferty."""
                else:
                    # Specjalna wiadomość dla marek luksusowych
                    luxury_message = ""
                    if analysis.get('has_luxury_brand'):
                        luxury_message = "\n🏎️ **Wykryto markę premium** - zwiększony priorytet!"
                    
                    message_text = f"""🔍 **Nie mamy tego produktu w ofercie**

Szukana fraza: "{message}"{luxury_message}

✨ **Dobra wiadomość:** Twoje zapytanie zostało zapisane! 
Jeśli wiele osób szuka tego produktu, dodamy go do naszej oferty."""
                
                return {
                    'text_message': message_text + "\n\n📧 Chcesz otrzymać powiadomienie gdy produkt będzie dostępny?",
                    'confidence_level': confidence_level,
                    'lost_demand': True,
                    'buttons': [
                        {'text': '📧 Tak, powiadom mnie', 'action': 'notify_when_available'},
                        {'text': '🔄 Szukaj czegoś innego', 'action': 'search_product'},
                        {'text': '↩️ Menu główne', 'action': 'main_menu'}
                    ]
                }
        
        # Obsługa FAQ
        elif context == 'faq_search':
            faq_results = self.search_faq(message)
            
            if faq_results:
                best_match = faq_results[0]
                response = f"**{best_match['question']}**\n\n{best_match['answer']}"
                
                return {
                    'text_message': response,
                    'buttons': [
                        {'text': '❓ Zadaj inne pytanie', 'action': 'faq_search'},
                        {'text': '↩️ Menu główne', 'action': 'main_menu'}
                    ]
                }
        
        return {
            'text_message': 'Wybierz opcję:',
            'buttons': [
                {'text': '🔧 Szukaj części', 'action': 'search_product'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ]
        }
    
    def create_product_buttons(self, products: List[Tuple]) -> List[Dict]:
        """Tworzy przyciski dla produktów - BEZPOŚREDNIO DO PEŁNEJ KARTY"""
        buttons = []
        for item in products[:3]:
            if isinstance(item, tuple):
                product, score = item
                # Usuń score, kieruj bezpośrednio do pełnej karty
                buttons.append({
                    'text': f"🛒 {product['name'][:45]}...",
                    'action': f"show_full_card_{product['id']}"
                })
        
        buttons.extend([
            {'text': '🔄 Szukaj ponownie', 'action': 'search_product'},
            {'text': '↩️ Menu główne', 'action': 'main_menu'}
        ])
        
        return buttons
    
    def show_product_details(self, product_id: str, match_score: Optional[int] = None) -> Dict:
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
        
        return {
            'text_message': f"""🔧 **{product['name']}**

💰 **Cena:** {product['price']:.2f} zł netto
📦 **Stan:** {product['stock']} szt.""",
            'buttons': [
                {'text': f"🛒 Dodaj do koszyka", 'action': f"add_to_cart_{product['id']}"},
                {'text': '🔍 Szukaj dalej', 'action': 'search_product'},
                {'text': '🏠 Menu główne', 'action': 'main_menu'}
            ]
        }
    
    def show_full_product_card(self, product_id: str) -> Dict:
        """Pokazuje pełną kartę produktu bez pośrednich kroków"""
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
        
        return {
            'text_message': f"""🔧 {product['name']}

💰 Cena: {product['price']:.2f} zł netto
📦 Stan: {product['stock']} szt.""",
            'buttons': [
                {'text': '🛒 Dodaj do koszyka', 'action': f"add_to_cart_{product['id']}"},
                {'text': '🔍 Szukaj dalej', 'action': 'search_product'},
                {'text': '🏠 Menu główne', 'action': 'main_menu'}
            ]
        }
    
    def add_to_cart(self, product_id: str) -> Dict:
        """Dodanie do koszyka"""
        if 'cart' not in session:
            session['cart'] = []
        
        session['cart'].append(product_id)
        session.modified = True
        
        return {
            'text_message': f"""✅ **Dodano do koszyka!**""",
            'cart_updated': True,
            'buttons': [
                {'text': '🔍 Kontynuuj zakupy', 'action': 'search_product'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ]
        }
        

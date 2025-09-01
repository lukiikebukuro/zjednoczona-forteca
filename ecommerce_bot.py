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
import requests
import uuid
import hashlib
import time
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz, process


class EcommerceBot:
    def __init__(self):
        self.product_database = {}
        self.faq_database = {}
        self.orders_database = {}
        self.current_context = None
        self.search_cache = {}  # Cache dla wydajności
        self.initialize_data()
    
    def initialize_data(self):
        """Inicjalizuje bazę danych dla branży motoryzacyjnej"""
        
        # Rozszerzona baza produktów motoryzacyjnych
        self.product_database = {
            'products': [
                # === SAMOCHODY OSOBOWE ===
                # KLOCKI HAMULCOWE - rozszerzone
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
                
                # === MOTOCYKLE - NOWE ===
                {'id': 'MKH001', 'name': 'Klocki hamulcowe EBC Yamaha R6 2003-2016 przód', 'category': 'hamulce', 'machine': 'motocykl', 'brand': 'EBC', 'model': 'FA252HH', 'price': 145.00, 'stock': 32},
                {'id': 'MKH002', 'name': 'Klocki hamulcowe Brembo Honda CBR 600RR sinter', 'category': 'hamulce', 'machine': 'motocykl', 'brand': 'Brembo', 'model': '07HO50SA', 'price': 189.00, 'stock': 28},
                {'id': 'MKH003', 'name': 'Klocki hamulcowe Ferodo Kawasaki Ninja ZX6R platinum', 'category': 'hamulce', 'machine': 'motocykl', 'brand': 'Ferodo', 'model': 'FDB2048P', 'price': 178.00, 'stock': 19},
                {'id': 'MKH004', 'name': 'Klocki hamulcowe TRW Lucas Suzuki GSX-R 750 racing', 'category': 'hamulce', 'machine': 'motocykl', 'brand': 'TRW', 'model': 'MCB721SRM', 'price': 234.00, 'stock': 15},
                
                {'id': 'MTH001', 'name': 'Tarcza hamulcowa Brembo Ducati Panigale 330mm floating', 'category': 'hamulce', 'machine': 'motocykl', 'brand': 'Brembo', 'model': '78B408C6', 'price': 890.00, 'stock': 6},
                {'id': 'MTH002', 'name': 'Tarcza hamulcowa EBC Yamaha MT-09 300mm contour', 'category': 'hamulce', 'machine': 'motocykl', 'brand': 'EBC', 'model': 'MD3006C', 'price': 456.00, 'stock': 14},
                
                {'id': 'MFO001', 'name': 'Filtr oleju HiFlo Yamaha R1 R6 FZ1 HF303', 'category': 'filtry', 'machine': 'motocykl', 'brand': 'HiFlo', 'model': 'HF303', 'price': 28.00, 'stock': 145},
                {'id': 'MFO002', 'name': 'Filtr oleju K&N Honda CBR 600 1000 KN-204', 'category': 'filtry', 'machine': 'motocykl', 'brand': 'K&N', 'model': 'KN-204', 'price': 45.00, 'stock': 98},
                
                {'id': 'MFA001', 'name': 'Filtr powietrza K&N Harley Davidson Sportster', 'category': 'filtry', 'machine': 'motocykl', 'brand': 'K&N', 'model': 'HD-1614', 'price': 234.00, 'stock': 23},
                {'id': 'MFA002', 'name': 'Filtr powietrza BMC Suzuki GSX-R 1000 race', 'category': 'filtry', 'machine': 'motocykl', 'brand': 'BMC', 'model': 'FM527/04', 'price': 189.00, 'stock': 18},
                
                {'id': 'MLN001', 'name': 'Łańcuch napędowy DID 520VX3 Yamaha R6 gold', 'category': 'napęd', 'machine': 'motocykl', 'brand': 'DID', 'model': '520VX3-114', 'price': 345.00, 'stock': 38},
                {'id': 'MLN002', 'name': 'Łańcuch RK 525GXW Honda CBR 600RR X-ring', 'category': 'napęd', 'machine': 'motocykl', 'brand': 'RK', 'model': '525GXW-116', 'price': 378.00, 'stock': 29},
                
                {'id': 'MSZ001', 'name': 'Świeca zapłonowa NGK Iridium CR9EIA-9 sport bikes', 'category': 'zapłon', 'machine': 'motocykl', 'brand': 'NGK', 'model': 'CR9EIA-9', 'price': 56.00, 'stock': 189},
                
                {'id': 'MAK001', 'name': 'Akumulator Yuasa YTZ10S sport bikes bezobsługowy', 'category': 'elektryka', 'machine': 'motocykl', 'brand': 'Yuasa', 'model': 'YTZ10S', 'price': 289.00, 'stock': 42},
                
                {'id': 'MOL001', 'name': 'Olej motocyklowy Motul 7100 10W40 4T syntetyczny 4L', 'category': 'oleje', 'machine': 'motocykl', 'brand': 'Motul', 'model': '7100 10W40', 'price': 189.00, 'stock': 67},
                {'id': 'MOL002', 'name': 'Olej Castrol Power 1 Racing 10W50 4T fully synthetic 4L', 'category': 'oleje', 'machine': 'motocykl', 'brand': 'Castrol', 'model': 'Power 1 Racing', 'price': 178.00, 'stock': 54},
                
                # === SAMOCHODY DOSTAWCZE - NOWE ===
                {'id': 'DKH001', 'name': 'Klocki hamulcowe Textar Mercedes Sprinter 906 przód', 'category': 'hamulce', 'machine': 'dostawczy', 'brand': 'Textar', 'model': '2430801', 'price': 267.00, 'stock': 34},
                {'id': 'DKH002', 'name': 'Klocki hamulcowe Ferodo VW Crafter 2.0 TDI wzmocnione', 'category': 'hamulce', 'machine': 'dostawczy', 'brand': 'Ferodo', 'model': 'FDB4191', 'price': 289.00, 'stock': 28},
                {'id': 'DKH003', 'name': 'Klocki hamulcowe ATE Ford Transit Custom przód', 'category': 'hamulce', 'machine': 'dostawczy', 'brand': 'ATE', 'model': '13.0460-2880', 'price': 234.00, 'stock': 45},
                {'id': 'DKH004', 'name': 'Klocki hamulcowe Brembo Iveco Daily 35S tył', 'category': 'hamulce', 'machine': 'dostawczy', 'brand': 'Brembo', 'model': 'P23116', 'price': 198.00, 'stock': 37},
                {'id': 'DKH005', 'name': 'Klocki hamulcowe TRW Renault Master III heavy duty', 'category': 'hamulce', 'machine': 'dostawczy', 'brand': 'TRW', 'model': 'GDB1897DTE', 'price': 312.00, 'stock': 22},
                
                {'id': 'DTH001', 'name': 'Tarcza hamulcowa Brembo Sprinter 906 330mm wentylowana', 'category': 'hamulce', 'machine': 'dostawczy', 'brand': 'Brembo', 'model': '09.A820.11', 'price': 567.00, 'stock': 15},
                {'id': 'DTH002', 'name': 'Tarcza hamulcowa ATE VW Crafter 303mm przód', 'category': 'hamulce', 'machine': 'dostawczy', 'brand': 'ATE', 'model': '24.0330-0227', 'price': 423.00, 'stock': 19},
                
                {'id': 'DFO001', 'name': 'Filtr oleju Mann W712/94 Sprinter Vito 2.2 CDI', 'category': 'filtry', 'machine': 'dostawczy', 'brand': 'Mann', 'model': 'W712/94', 'price': 78.00, 'stock': 89},
                {'id': 'DFO002', 'name': 'Filtr oleju Mahle OX404D VW Crafter 2.0 TDI', 'category': 'filtry', 'machine': 'dostawczy', 'brand': 'Mahle', 'model': 'OX404D', 'price': 67.00, 'stock': 76},
                
                {'id': 'DFP001', 'name': 'Filtr paliwa Mann WK940/33x Iveco Daily 3.0', 'category': 'filtry', 'machine': 'dostawczy', 'brand': 'Mann', 'model': 'WK940/33x', 'price': 134.00, 'stock': 54},
                {'id': 'DFP002', 'name': 'Filtr paliwa Delphi Renault Master 2.3 dCi', 'category': 'filtry', 'machine': 'dostawczy', 'brand': 'Delphi', 'model': 'HDF924E', 'price': 98.00, 'stock': 61},
                
                {'id': 'DFA001', 'name': 'Filtr powietrza Mann C2991 Mercedes Sprinter', 'category': 'filtry', 'machine': 'dostawczy', 'brand': 'Mann', 'model': 'C2991', 'price': 89.00, 'stock': 72},
                
                {'id': 'DAM001', 'name': 'Amortyzator Sachs Mercedes Sprinter 906 przód wzmocniony', 'category': 'zawieszenie', 'machine': 'dostawczy', 'brand': 'Sachs', 'model': '315901', 'price': 678.00, 'stock': 14},
                {'id': 'DAM002', 'name': 'Amortyzator KYB VW Crafter heavy duty tył', 'category': 'zawieszenie', 'machine': 'dostawczy', 'brand': 'KYB', 'model': '344459', 'price': 523.00, 'stock': 18},
                
                {'id': 'DAK001', 'name': 'Akumulator Varta Promotive Black 110Ah 680A dostawcze', 'category': 'elektryka', 'machine': 'dostawczy', 'brand': 'Varta', 'model': 'I10', 'price': 567.00, 'stock': 32},
                {'id': 'DAK002', 'name': 'Akumulator Bosch T5 100Ah 830A Sprinter Transit', 'category': 'elektryka', 'machine': 'dostawczy', 'brand': 'Bosch', 'model': 'T5077', 'price': 523.00, 'stock': 28},
                
                {'id': 'DSZ001', 'name': 'Świeca żarowa Bosch Duraterm Sprinter 2.2 CDI', 'category': 'zapłon', 'machine': 'dostawczy', 'brand': 'Bosch', 'model': '0250403009', 'price': 89.00, 'stock': 76},
                
                {'id': 'DOL001', 'name': 'Olej Mobil Delvac MX 15W40 CI-4 20L beczka', 'category': 'oleje', 'machine': 'dostawczy', 'brand': 'Mobil', 'model': 'Delvac MX', 'price': 456.00, 'stock': 23},
                {'id': 'DOL002', 'name': 'Olej Shell Rimula R6 LME 5W30 Low SAPS 20L', 'category': 'oleje', 'machine': 'dostawczy', 'brand': 'Shell', 'model': 'Rimula R6', 'price': 523.00, 'stock': 19}
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
                'answer': '↩️ **Zwroty i reklamacje:**\n\n• **14 dni** na zwrot bez montażu\n• **24 miesiące** gwarancji na wszystkie części\n• **Darmowa wymiana** przy wadzie fabrycznej\n• **Zwrot kosztów montażu** przy wadliwej części\n\n📝 Wypełnij formularz online i otrzymasz etykietę zwrotną',
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

    def send_ga4_no_results_event(self, query, search_type='products'):
        """Send 'search_no_results' event to Google Analytics 4 via Measurement Protocol"""
        try:
            GA4_MEASUREMENT_ID = "G-ECOMMERCE123"
            GA4_API_SECRET = "YOUR_API_SECRET_HERE"
            
            session_data = f"universal_soldier_{int(time.time() // 3600)}"
            client_id = hashlib.md5(session_data.encode()).hexdigest()
            
            url = f"https://www.google-analytics.com/mp/collect"
            params = {
                'measurement_id': GA4_MEASUREMENT_ID,
                'api_secret': GA4_API_SECRET
            }
            
            payload = {
                "client_id": client_id,
                "events": [{
                    "name": "search_no_results",
                    "params": {
                        "search_term": query[:100],
                        "search_type": search_type,
                        "source": "universal_soldier_bot",
                        "query_length": len(query),
                        "timestamp": int(time.time()),
                        "session_id": client_id[:16]
                    }
                }]
            }
            
            response = requests.post(url, params=params, json=payload, timeout=5)
            
            if response.status_code == 204:
                print(f"[GA4] ✅ No results event sent: '{query}' ({search_type})")
                return True
            else:
                print(f"[GA4] ❌ Failed to send event. Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[GA4] 💥 Error sending event: {e}")
            return False

    def normalize_query(self, query):
        """Rozszerzona normalizacja zapytania z obsługą skrótów motoryzacyjnych"""
        query = query.lower().strip()
        
        # Rozszerzona korekta literówek i skrótów
        typo_corrections = {
            # Literówki
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
            # Marki
            'bosch': 'bosch',
            'bosh': 'bosch',
            'mann': 'mann',
            'man': 'mann',
            'brembo': 'brembo',
            'brebo': 'brembo',
            # Skróty samochodów
            'gol': 'golf',
            'vw': 'volkswagen',
            'mb': 'mercedes',
            'merco': 'mercedes',
            'benz': 'mercedes',
            'beemer': 'bmw',
            'aud': 'audi',
            # Skróty motocyklowe
            'yam': 'yamaha',
            'kawa': 'kawasaki',
            'suzi': 'suzuki',
            'duc': 'ducati',
            # Skróty dostawcze
            'sprin': 'sprinter',
            'craft': 'crafter',
            'tran': 'transit'
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
            'olejów': 'olej',
            'łańcuchy': 'łańcuch',
            'łańcuchów': 'łańcuch'
        }
        
        for plural, singular in plural_singular.items():
            query = query.replace(plural, singular)
        
        query = ' '.join(query.split())
        return query
    
    def get_fuzzy_product_matches(self, query, machine_filter=None, limit=6):
        """NOWA ULEPSZONA FUNKCJA - Progresywny scoring dla lepszych wyników"""
        # Cache dla wydajności
        cache_key = f"{query}_{machine_filter}_{limit}"
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]
        
        query = self.normalize_query(query)
        matches = []
        
        for product in self.product_database['products']:
            # Filtrowanie po typie maszyny
            if machine_filter and product['machine'] != machine_filter and product['machine'] != 'uniwersalny':
                continue
            
            # Przygotowanie tekstu do analizy
            search_text = f"{product['name']} {product['brand']} {product['model']} {product['category']}"
            search_text_lower = search_text.lower()
            
            # NOWY WIELOPOZIOMOWY SYSTEM SCORINGU
            scores = []
            
            # 1. Token Sort Ratio - sortuje tokeny alfabetycznie
            token_sort_score = fuzz.token_sort_ratio(query, search_text_lower)
            scores.append(token_sort_score * 1.0)
            
            # 2. Token Set Ratio - ignoruje duplikaty i kolejność
            token_set_score = fuzz.token_set_ratio(query, search_text_lower)
            scores.append(token_set_score * 0.9)
            
            # 3. Partial Token Sort Ratio - dla niepełnych słów
            partial_token_sort = fuzz.partial_token_sort_ratio(query, search_text_lower)
            scores.append(partial_token_sort * 0.85)
            
            # 4. KLUCZOWA INNOWACJA: Analiza tokenów z dopasowaniem częściowym
            query_tokens = query.split()
            product_tokens = search_text_lower.split()
            token_matches = []
            
            for q_token in query_tokens:
                best_match = 0
                for p_token in product_tokens:
                    # Dokładne dopasowanie
                    if q_token == p_token:
                        best_match = 100
                        break
                    # Sprawdź prefiks (np. "gol" -> "golf", "yam" -> "yamaha")
                    elif p_token.startswith(q_token) and len(q_token) >= 2:
                        match_ratio = len(q_token) / len(p_token)
                        best_match = max(best_match, 95 * match_ratio)
                    # Sprawdź sufiks
                    elif q_token.startswith(p_token) and len(p_token) >= 2:
                        match_ratio = len(p_token) / len(q_token)
                        best_match = max(best_match, 90 * match_ratio)
                    # Podobieństwo edycyjne (np. "golf" vs "gol")
                    elif len(q_token) >= 2:
                        similarity = fuzz.ratio(q_token, p_token)
                        if similarity > 75:
                            best_match = max(best_match, similarity * 0.95)
                
                token_matches.append(best_match)
            
            # Średnia ważona z bonusami
            if token_matches:
                avg_token_match = sum(token_matches) / len(token_matches)
                
                # BONUS za kompletność dopasowania
                if all(score > 70 for score in token_matches):
                    avg_token_match *= 1.2  # 20% bonus
                elif all(score > 50 for score in token_matches):
                    avg_token_match *= 1.1  # 10% bonus
                # KARA za słabe dopasowanie
                elif any(score < 30 for score in token_matches):
                    avg_token_match *= 0.7  # 30% kara
                
                scores.append(min(100, avg_token_match))
            
            # 5. Bonusy kontekstowe
            bonus = 0
            
            # Bonus za markę
            brand_lower = product['brand'].lower()
            if brand_lower in query or query in brand_lower:
                bonus += 20
            elif any(token in brand_lower for token in query.split() if len(token) > 2):
                bonus += 15
            
            # Bonus za model
            model_lower = product['model'].lower()
            if any(token in model_lower for token in query.split() if len(token) > 2):
                bonus += 12
            
            # Bonus za kategorię
            if any(token in product['category'].lower() for token in query.split() if len(token) > 3):
                bonus += 10
            
            # Bonus za ID produktu
            if query.upper() in product['id']:
                bonus += 25
            
            # 6. Oblicz końcowy wynik
            if scores:
                base_score = max(scores)
                final_score = min(100, base_score + bonus)
                
                # Dodatkowe wzmocnienie dla bardzo dokładnych dopasowań
                if len(query_tokens) > 1 and token_matches:
                    if all(score > 85 for score in token_matches):
                        final_score = min(100, final_score * 1.15)
                
                # Próg akceptacji
                if final_score >= 35:
                    matches.append((product, round(final_score)))
        
        # Sortowanie malejąco
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # Filtrowanie słabych wyników gdy mamy dobre
        if matches and matches[0][1] > 85:
            matches = [(p, s) for p, s in matches if s > 45]
        
        # Zapisz w cache
        result = matches[:limit]
        self.search_cache[cache_key] = result
        return result
    
    def get_fuzzy_faq_matches(self, query, limit=5):
        """Dopasowanie FAQ z inteligentnym ważeniem kontekstowym"""
        query = self.normalize_query(query)
        matches = []
        
        for faq in self.faq_database:
            question = faq['question'].lower()
            keywords = [k.lower() for k in faq['keywords']]
            category = faq.get('category', '').lower()
            
            final_score = 0
            
            # Dokładne dopasowania
            if query == question:
                final_score = 100
            elif query in keywords:
                final_score = 95
            
            if not final_score:
                # Dopasowanie do pytania
                question_score = fuzz.ratio(query, question)
                if question_score > 80:
                    final_score = max(final_score, question_score)
                
                # Dopasowanie do słów kluczowych
                for keyword in keywords:
                    keyword_score = fuzz.ratio(query, keyword)
                    if keyword_score > 85:
                        final_score = max(final_score, keyword_score + 5)
                
                # Token set ratio
                search_text = f"{question} {' '.join(keywords)}"
                token_score = fuzz.token_set_ratio(query, search_text.lower())
                if token_score > 60:
                    final_score = max(final_score, token_score)
                
                # Bonusy za częściowe dopasowania
                query_words = query.split()
                for q_word in query_words:
                    if len(q_word) > 2:
                        if q_word in question:
                            final_score += 5
                        if any(q_word in k for k in keywords):
                            final_score += 8
                        if category and q_word in category:
                            final_score += 10
            
            final_score = min(100, final_score)
            
            if final_score >= 40:
                matches.append((faq, final_score))
        
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

Jestem Twoim ekspertem od części samochodowych. Pomogę Ci znaleźć idealną część dla:
• 🚗 Samochodów osobowych
• 🏍️ Motocykli 
• 🚐 Samochodów dostawczych

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
            
            # Przykłady dla każdego typu
            examples = {
                'osobowy': 'np. klocki bosch, filtr mann, golf, bmw e90...',
                'dostawczy': 'np. sprinter, transit, crafter, iveco daily...',
                'motocykl': 'np. yamaha r6, łańcuch did, ebc, cbr...',
                'uniwersalny': 'np. k&n filtr, akumulator varta...'
            }
            
            return {
                'text_message': f"""✅ **{machine_names.get(machine_type, 'Pojazd')}**

Wpisz czego szukasz. Nasz inteligentny system:
• 🤖 Automatycznie poprawia literówki
• 📈 Zwiększa dokładność przy doprecyzowywaniu
• 🎯 Rozumie skróty (np. "yam" → Yamaha, "gol" → Golf)

Spróbuj np. wpisać "klocki" a potem doprecyzuj "klocki gol" - wynik wzrośnie!""",
                'enable_input': True,
                'input_placeholder': examples.get(machine_type, 'Wpisz nazwę części...'),
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
        """Przetwarzanie wiadomości z pokazaniem mocy fuzzy matching"""
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
            results = self.get_fuzzy_product_matches(message, machine_filter, limit=5)
            
            if not results:
                # Spróbuj bez filtra
                results = self.get_fuzzy_product_matches(message, None, limit=5)
                
                if results:
                    products_text = ""
                    for product, score in results[:3]:
                        stock_icon = "✅" if product['stock'] > 10 else "⚠️" if product['stock'] > 0 else "❌"
                        products_text += f"\n**{product['name']}**\n"
                        products_text += f"🎯 Dopasowanie: **{score}%** | {stock_icon} {product['stock']} szt. | {product['price']:.2f} zł\n"
                    
                    return {
                        'text_message': f"""⚠️ Nie znaleziono dla wybranego typu, ale mamy inne:

{products_text}

💡 **Zauważ:** Im bardziej doprecyzujesz zapytanie, tym wyższy procent dopasowania!""",
                        'buttons': self.create_product_buttons([p for p, s in results[:3]])
                    }
                else:
                    return {
                        'text_message': """❌ Nie znaleziono produktów.

🤖 System automatycznie poprawia błędy. Spróbuj:
• Użyć innych słów
• Wpisać markę produktu
• Podać numer katalogowy""",
                        'buttons': [
                            {'text': '🔄 Szukaj ponownie', 'action': 'search_product'},
                            {'text': '↩️ Menu główne', 'action': 'main_menu'}
                        ]
                    }
            
            elif len(results) == 1:
                product, score = results[0]
                return self.show_product_details(product['id'], score)
            
            else:
                # Pokaż wyniki z procentami dopasowania
                products_text = f"🎯 **Moc naszego fuzzy matching:**\n\n"
                for product, score in results:
                    stock_icon = "✅" if product['stock'] > 10 else "⚠️" if product['stock'] > 0 else "❌"
                    score_emoji = "🔥" if score >= 90 else "✨" if score >= 70 else "💫"
                    products_text += f"\n{score_emoji} **{product['name']}**\n"
                    products_text += f"📊 Dopasowanie: **{score}%** | {product['id']} | {stock_icon} {product['stock']} szt. | **{product['price']:.2f} zł**\n"
                
                return {
                    'text_message': f"""✅ Znaleziono {len(results)} produktów:

{products_text}

💡 **Protip:** Doprecyzuj zapytanie (np. dodaj markę), a procent dopasowania wzrośnie!""",
                    'buttons': self.create_product_buttons(results)
                }
        
        return {
            'text_message': 'Wybierz opcję:',
            'buttons': [
                {'text': '🔧 Szukaj części', 'action': 'search_product'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ]
        }
    
    def format_product_results(self, products):
        """Formatowanie wyników z pokazaniem scoringu"""
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
        for item in products[:4]:
            if isinstance(item, tuple):
                product, score = item
                buttons.append({
                    'text': f"🛒 {product['name'][:25]}... ({score}%)",
                    'action': f"product_details_{product['id']}"
                })
            else:
                product = item
                buttons.append({
                    'text': f"🛒 {product['name'][:30]}... ({product['price']:.0f} zł)",
                    'action': f"product_details_{product['id']}"
                })
        
        buttons.extend([
            {'text': '🔄 Szukaj ponownie', 'action': 'search_product'},
            {'text': '↩️ Menu główne', 'action': 'main_menu'}
        ])
        
        return buttons
    
    def show_product_details(self, product_id, match_score=None):
        """Szczegóły produktu z opcjonalnym wynikiem dopasowania"""
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
        
        score_info = ""
        if match_score:
            score_emoji = "🔥" if match_score >= 90 else "✨" if match_score >= 70 else "💫"
            score_info = f"\n{score_emoji} **Dopasowanie:** {match_score}%"
        
        return {
            'text_message': f"""🔧 **{product['name']}**{score_info}

📋 **Dane techniczne:**
• Kod: {product['id']}
• Producent: {product['brand']}
• Model: {product['model']}
• Kategoria: {self.product_database['categories'].get(product['category'], product['category'])}
• Typ pojazdu: {self.product_database['machines'].get(product['machine'], product['machine'])}

💰 **Cena:** {product['price']:.2f} zł netto
💵 **Cena brutto:** {product['price'] * 1.23:.2f} zł

📦 **Dostępność:** {stock_status} ({product['stock']} szt.)
🚚 **Wysyłka:** 24h dla produktów na stanie""",
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
    
    def search_suggestions(self, query, context='products'):
        """Funkcja do podpowiedzi w czasie rzeczywistym"""
        suggestions = []
        if context == 'faq':
            faq_results = self.get_fuzzy_faq_matches(query, limit=6)
            for faq, score in faq_results:
                suggestions.append({
                    'title': faq['question'],
                    'subtitle': f"Kategoria: {faq.get('category', 'FAQ')}",
                    'icon': '❓',
                    'score': int(score),
                    'data': faq
                })
        else:
            product_results = self.get_fuzzy_product_matches(query, session.get('machine_filter'), limit=8)
            for product, score in product_results:
                suggestions.append({
                    'title': product['name'],
                    'subtitle': f"{product['brand']} • {product['price']:.0f} zł",
                    'icon': '🔧',
                    'score': int(score),
                    'data': product
                })
        return suggestions
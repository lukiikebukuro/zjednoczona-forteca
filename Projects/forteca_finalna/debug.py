#!/usr/bin/env python3
"""
DEBUG OPERACJI KULOODPORNY RDZEŃ - WERSJA ROZSZERZONA
100 scenariuszy testowych: 70 oryginalnych + 30 scenariuszy klientów
Strategia 50/50: Zasób A vs Zasób B vs Filtr Nonsensu
"""

from ecommerce_bot import EcommerceBot

def test_scenario(bot, query, expected_result):
    """Testuje scenariusz i zwraca szczegółowy wynik"""
    try:
        analysis = bot.analyze_query_intent(query)
        
        confidence_to_result = {
            'HIGH': 'ZNALEZIONE PRODUKTY',
            'MEDIUM': 'ZNALEZIONE PRODUKTY', 
            'LOW': 'ODFILTROWANE',
            'NO_MATCH': 'UTRACONE OKAZJE'
        }
        
        actual_result = confidence_to_result.get(analysis['confidence_level'], 'NIEZNANE')
        passed = actual_result == expected_result
        
        return {
            'passed': passed,
            'actual': actual_result,
            'expected': expected_result,
            'confidence': analysis['confidence_level'],
            'token_validity': analysis['token_validity'],
            'ga4_event': analysis.get('ga4_event', 'None'),
            'suggestion_type': analysis.get('suggestion_type', 'None'),
            'is_structural': analysis.get('is_structural', False),
            'has_luxury_brand': analysis.get('has_luxury_brand', False)
        }
        
    except Exception as e:
        return {
            'passed': False,
            'actual': f'ERROR: {e}',
            'expected': expected_result,
            'confidence': 'ERROR',
            'token_validity': 0
        }

def run_comprehensive_tests():
    """Uruchamia kompletne testy operacji Kuloodporny Rdzeń"""
    
    print("🚀 OPERACJA KULOODPORNY RDZEŃ - DEBUG ROZSZERZONY")
    print("100 SCENARIUSZY TESTOWYCH - STRATEGIA 50/50 + SCENARIUSZE KLIENTÓW")
    print("=" * 80)
    
    bot = EcommerceBot()
    
    # === SCENARIUSZE TESTOWE ===
    scenarios = [
        # === ORYGINALNE (1-20) - ze starego debug.py ===
        ("klocki bmw e90", "ZNALEZIONE PRODUKTY"),
        ("filtr oleju sony", "UTRACONE OKAZJE"),
        ("klocki bmw x1", "UTRACONE OKAZJE"),
        ("kloki bosh", "ZNALEZIONE PRODUKTY"),
        ("asdasdasd", "ODFILTROWANE"),
        ("filtr mann a1", "UTRACONE OKAZJE"),
        ("filtr mann 55", "UTRACONE OKAZJE"),
        ("klocki ferrari", "UTRACONE OKAZJE"),
        ("opony zimowe", "UTRACONE OKAZJE"),
        ("filtr mann hu719/7x", "ZNALEZIONE PRODUKTY"),
        ("bmw", "ZNALEZIONE PRODUKTY"),
        ("amortyzator", "ZNALEZIONE PRODUKTY"),
        ("bmw 1", "UTRACONE OKAZJE"),
        ("świeca", "ZNALEZIONE PRODUKTY"),
        ("amortyztor bilstein", "ZNALEZIONE PRODUKTY"),
        ("olej castrol 5w30", "ZNALEZIONE PRODUKTY"),
        ("akumulator vata", "ZNALEZIONE PRODUKTY"),
        ("części porsche", "UTRACONE OKAZJE"),
        ("xyzxyzxyz", "ODFILTROWANE"),
        ("filtr 0986494104", "ZNALEZIONE PRODUKTY"),
        
        # === ZASÓB A - FAKTYCZNE PRODUKTY (21-30) ===
        ("klocki bosch bmw e90", "ZNALEZIONE PRODUKTY"),           # KH001 dokładne
        ("filtr oleju mann hu719", "ZNALEZIONE PRODUKTY"),         # FO001 częściowe
        ("amortyzator bilstein golf", "ZNALEZIONE PRODUKTY"),      # AM001 marka+model
        ("tarcza brembo 320mm", "ZNALEZIONE PRODUKTY"),            # TH001 specyfikacja
        ("świeca ngk iridium", "ZNALEZIONE PRODUKTY"),             # SZ001 typ
        ("akumulator varta 74ah", "ZNALEZIONE PRODUKTY"),          # AK001 parametry
        ("olej castrol edge 5w30", "ZNALEZIONE PRODUKTY"),         # OL001 pełna spec
        ("klocki yamaha r6 ebc", "ZNALEZIONE PRODUKTY"),           # MKH001 motocykl
        ("łańcuch did 520", "ZNALEZIONE PRODUKTY"),                # MLN001 motocykl
        ("klocki sprinter textar", "ZNALEZIONE PRODUKTY"),         # DKH001 dostawczy
        
        # === ZASÓB B - UTRACONY POPYT LUKSUSOWY (31-40) ===
        ("klocki ferrari 458", "UTRACONE OKAZJE"),                 # Luksus + model
        ("filtr maserati ghibli", "UTRACONE OKAZJE"),              # Luksus + nowy model  
        ("amortyzatory bentley continental", "UTRACONE OKAZJE"),   # Luksus + kategoria
        ("tarcze lamborghini gallardo", "UTRACONE OKAZJE"),        # Luksus + część
        ("klocki alfa romeo giulia", "UTRACONE OKAZJE"),           # Znana marka + nowy
        ("filtr powietrza rolls royce", "UTRACONE OKAZJE"),        # Ekskluzywna + kategoria
        ("świece bugatti veyron", "UTRACONE OKAZJE"),              # Hypercar + część
        ("olej aston martin db11", "UTRACONE OKAZJE"),             # Luksus + nowy model
        ("klocki mclaren 720s", "UTRACONE OKAZJE"),                # Supercar + kategoria
        ("amortyzator pagani huayra", "UTRACONE OKAZJE"),          # Hyperscar + część
        
        # === ZASÓB B - STRUKTURALNE ZAPYTANIA (41-50) ===
        ("klocki xiaomi redmi", "UTRACONE OKAZJE"),                # Tech brand + auto część
        ("filtr dyson v11", "UTRACONE OKAZJE"),                    # Odkurzacz + auto
        ("amortyzator apple macbook", "UTRACONE OKAZJE"),          # Tech + auto część
        ("tarcze samsung galaxy", "UTRACONE OKAZJE"),              # Tech + auto część
        ("drzwi kia sportage", "UTRACONE OKAZJE"),                 # Karoseria + model
        ("klapa honda civic", "UTRACONE OKAZJE"),                  # Karoseria + model
        ("maska toyota corolla", "UTRACONE OKAZJE"),               # Karoseria + znany model
        ("zderzak ford focus", "UTRACONE OKAZJE"),                 # Karoseria + model
        ("reflektor xenon audi", "UTRACONE OKAZJE"),               # Część + tech + marka
        ("opony michelin 17", "UTRACONE OKAZJE"),                  # Marka + rozmiar brak
        
        # === EDGE CASES - LITERÓWKI I DZIWNE CZĘŚCI (51-60) ===
        ("kloki bosh e90", "ZNALEZIONE PRODUKTY"),                 # Literówka w części+marka
        ("filetr man bmw", "ZNALEZIONE PRODUKTY"),                 # Literówka w części
        ("amortyztor sachs golf", "ZNALEZIONE PRODUKTY"),          # Literówka w części
        ("swica ngk honda", "ZNALEZIONE PRODUKTY"),                # Literówka w części
        ("akumlator varta ford", "ZNALEZIONE PRODUKTY"),           # Literówka w części
        ("ślimak maglownicy audi", "UTRACONE OKAZJE"),             # Prawdziwa część dziwna
        ("pucharek amortyzatora bmw", "UTRACONE OKAZJE"),          # Prawdziwa część rzadka
        ("krakownica zawieszenia opel", "UTRACONE OKAZJE"),        # Prawdziwa część egzotyczna
        ("czop kulowy mercedes", "UTRACONE OKAZJE"),               # Prawdziwa część śmieszna
        ("kielich sprężyny vw", "UTRACONE OKAZJE"),                # Prawdziwa część nietypowa
        
        # === NONSENS - FILTR ANTYSZUMOWY (61-70) ===
        ("qwerty asdf", "ODFILTROWANE"),                           # Klawiatura czysty bełkot
        ("asdfgh jklm", "ODFILTROWANE"),                           # Kolejny rząd klawiatury
        ("nie wiem co szukam", "ODFILTROWANE"),                    # Fraza konwersacyjna
        ("pomocy gdzie jest", "ODFILTROWANE"),                     # Fraza konwersacyjna
        ("jak to działa", "ODFILTROWANE"),                         # Pytanie konwersacyjne
        ("hello klocki world", "ODFILTROWANE"),                    # Mieszane języki + bełkot
        ("pizza hamburger klocki", "ODFILTROWANE"),                # Jedzenie + części
        ("klocki do pizzy", "ODFILTROWANE"),                       # Auto części + jedzenie
        ("aaaaaa bbbbbb", "ODFILTROWANE"),                         # Powtórzenia liter
        ("123456 789", "ODFILTROWANE"),                            # Same liczby
        
        # === CZĘŚCI KAROSERYJNE - POPULARNE ZAPYTANIA (71-80) ===
        ("lusterko ford focus", "UTRACONE OKAZJE"),               # Karoseria + popularny model
        ("zderzak audi a4", "UTRACONE OKAZJE"),                   # Karoseria + popularny model  
        ("błotnik bmw e90", "UTRACONE OKAZJE"),                   # Karoseria + kod modelu
        ("klapa bagażnika golf", "UTRACONE OKAZJE"),              # Karoseria + model bez marki
        ("próg toyota corolla", "UTRACONE OKAZJE"),               # Karoseria + popularny model
        ("maska volkswagen passat", "UTRACONE OKAZJE"),           # Karoseria + marka + model
        ("reflektor mercedes w204", "UTRACONE OKAZJE"),           # Optyka + kod modelu
        ("lampa stop bmw", "UTRACONE OKAZJE"),                    # Optyka + marka
        ("kierunkowskaz audi", "UTRACONE OKAZJE"),                # Optyka + marka
        ("szyba przednia ford", "UTRACONE OKAZJE"),               # Szyby + marka

        # === POPULARNE SKRÓTY I LITERÓWKI (81-90) ===
        ("filtry vw", "UTRACONE OKAZJE"),                         # Skrót marki + liczba mnoga
        ("kloki mercedes", "ZNALEZIONE PRODUKTY"),                # Literówka + marka
        ("swica bosch", "ZNALEZIONE PRODUKTY"),                   # Literówka + marka
        ("olel 5w30", "ZNALEZIONE PRODUKTY"),                     # Literówka w kategorii
        ("opny zimowe", "UTRACONE OKAZJE"),                       # Literówka + sezonowość
        ("hamulce mb", "UTRACONE OKAZJE"),                        # Kategoria + skrót marki
        ("filtry renault", "UTRACONE OKAZJE"),                    # Liczba mnoga + marka
        ("świece do golfa", "UTRACONE OKAZJE"),                   # Kategoria + do + model
        ("akumulatory varta", "ZNALEZIONE PRODUKTY"),             # Liczba mnoga + marka
        ("oleju silnikowego", "UTRACONE OKAZJE"),                 # Dopełniacz + przymiotnik

        # === NOWE MARKI I TRENDY (91-95) ===
        ("klocki byd tang", "UTRACONE OKAZJE"),                   # Chińska marka + model
        ("filtr geely coolray", "UTRACONE OKAZJE"),               # Chińska marka + model
        ("akumulator nio es8", "UTRACONE OKAZJE"),                # Elektryczna marka
        ("opony mg zs", "UTRACONE OKAZJE"),                       # Reaktywowana marka
        ("świeca polestar 2", "UTRACONE OKAZJE"),                 # Nowa marka premium

        # === BARDZO SPECJALISTYCZNE (96-100) ===
        ("sworzen wahacza bmw", "UTRACONE OKAZJE"),               # Specjalistyczna część
        ("tuleja stabilizatora", "UTRACONE OKAZJE"),              # Część bez marki
        ("czujnik cmp audi", "UTRACONE OKAZJE"),                  # Sensor + kod + marka
        ("elektromagnes vanos", "UTRACONE OKAZJE"),               # BMW-specific część
        ("moduł abs mercedes", "UTRACONE OKAZJE")                 # Elektronika + marka
    ]
    
    passed = 0
    failed = 0
    
    print(f"\n📊 TESTOWANIE {len(scenarios)} SCENARIUSZY:\n")
    
    # Grupuj wyniki dla lepszej analizy
    groups = {
        "ORYGINALNE (1-20)": (0, 20),
        "ZASÓB A - PRODUKTY (21-30)": (20, 30), 
        "ZASÓB B - LUKSUS (31-40)": (30, 40),
        "ZASÓB B - STRUKTURALNE (41-50)": (40, 50),
        "EDGE CASES (51-60)": (50, 60),
        "NONSENS (61-70)": (60, 70),
        "KAROSERIA (71-80)": (70, 80),
        "SKRÓTY I LITERÓWKI (81-90)": (80, 90), 
        "NOWE MARKI (91-95)": (90, 95),
        "SPECJALISTYCZNE (96-100)": (95, 100)
    }
    
    group_stats = {}
    
    for group_name, (start, end) in groups.items():
        print(f"\n--- {group_name} ---")
        group_passed = 0
        group_total = end - start
        
        for i in range(start, end):
            query, expected = scenarios[i]
            result = test_scenario(bot, query, expected)
            
            if result['passed']:
                passed += 1
                group_passed += 1
                status = "✅"
            else:
                failed += 1
                status = "❌"
            
            # Drukuj wynik z dodatkowymi informacjami
            print(f"{i+1:3d}. {status} '{query:30s}' → {result['actual']:18s}")
            
            # Dodatkowe info dla błędów i interesujących przypadków
            if not result['passed'] or result.get('has_luxury_brand') or result.get('is_structural'):
                extras = []
                if result.get('token_validity', 0) > 0:
                    extras.append(f"Validity:{result['token_validity']:.1f}")
                if result.get('has_luxury_brand'):
                    extras.append("LUXURY")
                if result.get('is_structural'):
                    extras.append("STRUCTURAL")
                if result.get('ga4_event') and result['ga4_event'] != 'None':
                    extras.append(f"GA4:{result['ga4_event']}")
                
                if extras:
                    print(f"     {' | '.join(extras)}")
        
        group_stats[group_name] = (group_passed, group_total)
        print(f"Wynik grupy: {group_passed}/{group_total} ({group_passed/group_total*100:.1f}%)")
    
    # === RAPORT KOŃCOWY ===
    print("\n" + "=" * 80)
    print("🎯 RAPORT KOŃCOWY OPERACJI KULOODPORNY RDZEŃ - ROZSZERZONY")
    print("=" * 80)
    
    overall_percentage = passed / len(scenarios) * 100
    print(f"\n📈 WYNIK OGÓLNY: {passed}/{len(scenarios)} ({overall_percentage:.1f}%)")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    
    print(f"\n📊 WYNIKI PO GRUPACH:")
    for group_name, (group_passed, group_total) in group_stats.items():
        percentage = group_passed / group_total * 100
        print(f"   • {group_name:30s}: {group_passed:2d}/{group_total:2d} ({percentage:5.1f}%)")
    
    # === OCENA STRATEGII 50/50 ===
    zasob_a_score = group_stats["ZASÓB A - PRODUKTY (21-30)"][0] / group_stats["ZASÓB A - PRODUKTY (21-30)"][1] * 100
    zasob_b_luksus = group_stats["ZASÓB B - LUKSUS (31-40)"][0] / group_stats["ZASÓB B - LUKSUS (31-40)"][1] * 100  
    zasob_b_strukturalne = group_stats["ZASÓB B - STRUKTURALNE (41-50)"][0] / group_stats["ZASÓB B - STRUKTURALNE (41-50)"][1] * 100
    nonsense_score = group_stats["NONSENS (61-70)"][0] / group_stats["NONSENS (61-70)"][1] * 100
    
    print(f"\n🔍 ANALIZA STRATEGII 50/50:")
    print(f"   • ZASÓB A (faktyczne produkty):     {zasob_a_score:5.1f}%")
    print(f"   • ZASÓB B (luksusowy popyt):        {zasob_b_luksus:5.1f}%") 
    print(f"   • ZASÓB B (strukturalny popyt):     {zasob_b_strukturalne:5.1f}%")
    print(f"   • FILTR NONSENSU:                   {nonsense_score:5.1f}%")
    
    # === ANALIZA SCENARIUSZY KLIENTÓW ===
    karoseria_score = group_stats["KAROSERIA (71-80)"][0] / group_stats["KAROSERIA (71-80)"][1] * 100
    skroty_score = group_stats["SKRÓTY I LITERÓWKI (81-90)"][0] / group_stats["SKRÓTY I LITERÓWKI (81-90)"][1] * 100
    nowe_marki_score = group_stats["NOWE MARKI (91-95)"][0] / group_stats["NOWE MARKI (91-95)"][1] * 100
    specjalistyczne_score = group_stats["SPECJALISTYCZNE (96-100)"][0] / group_stats["SPECJALISTYCZNE (96-100)"][1] * 100
    
    print(f"\n🎯 ANALIZA SCENARIUSZY KLIENTÓW:")
    print(f"   • KAROSERIA (popularne zapytania):  {karoseria_score:5.1f}%")
    print(f"   • SKRÓTY I LITERÓWKI:               {skroty_score:5.1f}%")
    print(f"   • NOWE MARKI (trendy):              {nowe_marki_score:5.1f}%")
    print(f"   • SPECJALISTYCZNE:                  {specjalistyczne_score:5.1f}%")
    
    # === OCENA KOŃCOWA ===
    print(f"\n🏆 OCENA KOŃCOWA:")
    if overall_percentage >= 90:
        print("🟢 OPERACJA KULOODPORNY RDZEŃ: PEŁNY SUKCES!")
        print("   System gotowy do produkcji. Strategia 50/50 + scenariusze klientów działają perfekcyjnie.")
    elif overall_percentage >= 80:
        print("🟡 OPERACJA KULOODPORNY RDZEŃ: SUKCES Z DROBNYMI UWAGAMI")
        print("   System prawie gotowy. Wymaga drobnych dostosowań.")
    elif overall_percentage >= 70:
        print("🟠 OPERACJA KULOODPORNY RDZEŃ: CZĘŚCIOWY SUKCES")
        print("   System wymaga poprawek przed wdrożeniem.")
    else:
        print("🔴 OPERACJA KULOODPORNY RDZEŃ: WYMAGA PRZEBUDOWY")
        print("   Strategia 50/50 wymaga fundamentalnych zmian.")
    
    # === REKOMENDACJE ===
    print(f"\n💡 REKOMENDACJE:")
    if zasob_a_score < 80:
        print("   • Popraw dopasowanie ZASOBU A (faktyczne produkty)")
    if zasob_b_luksus < 70 or zasob_b_strukturalne < 70:
        print("   • Wzmocnij ZASÓB B (wykrywanie utraconego popytu)")
    if nonsense_score < 80:
        print("   • Ulepsz FILTR NONSENSU (więcej wzorców bełkotu)")
    if karoseria_score < 70:
        print("   • Dodaj wsparcie dla części karoseryjnych")
    if skroty_score < 70:
        print("   • Popraw rozpoznawanie skrótów marek i literówek")
    if nowe_marki_score < 60:
        print("   • Rozważ dodanie nowych marek azjatyckich do bazy")
    
    return passed, failed

if __name__ == "__main__":
    print("🚀 ROZPOCZĘCIE ROZSZERZONYCH TESTÓW")
    print("Strategia 50/50 vs 100 scenariuszy: oryginalnych + klientów...")
    print()
    
    passed, failed = run_comprehensive_tests()
    
    print(f"\n🏁 TESTY ZAKOŃCZONE")
    print(f"Wynik: {passed}/{passed + failed}")
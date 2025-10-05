#!/usr/bin/env python3
"""
DEBUG OPERACJI KULOODPORNY RDZEŃ - WERSJA NAPRAWIONA
120 scenariuszy testowych: 100 oryginalnych + 20 nowych brutalnych
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
    
    print("🚀 OPERACJA KULOODPORNY RDZEŃ - DEBUG NAPRAWIONY")
    print("120 SCENARIUSZY TESTOWYCH - STRATEGIA 50/50 + BRUTALNE TESTY")
    print("=" * 80)
    
    bot = EcommerceBot()
    
    # === SCENARIUSZE TESTOWE (ORYGINALNE 100 + NOWE 20) ===
    scenarios = [
        # === ORYGINALNE (1-20) ===
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
        ("klocki bosch bmw e90", "ZNALEZIONE PRODUKTY"),
        ("filtr oleju mann hu719", "ZNALEZIONE PRODUKTY"),
        ("amortyzator bilstein golf", "ZNALEZIONE PRODUKTY"),
        ("tarcza brembo 320mm", "ZNALEZIONE PRODUKTY"),
        ("świeca ngk iridium", "ZNALEZIONE PRODUKTY"),
        ("akumulator varta 74ah", "ZNALEZIONE PRODUKTY"),
        ("olej castrol edge 5w30", "ZNALEZIONE PRODUKTY"),
        ("klocki yamaha r6 ebc", "ZNALEZIONE PRODUKTY"),
        ("łańcuch did 520", "ZNALEZIONE PRODUKTY"),
        ("klocki sprinter textar", "ZNALEZIONE PRODUKTY"),
        
        # === ZASÓB B - LUKSUS (31-40) ===
        ("klocki ferrari 458", "UTRACONE OKAZJE"),
        ("filtr maserati ghibli", "UTRACONE OKAZJE"),
        ("amortyzatory bentley continental", "UTRACONE OKAZJE"),
        ("tarcze lamborghini gallardo", "UTRACONE OKAZJE"),
        ("klocki alfa romeo giulia", "UTRACONE OKAZJE"),
        ("filtr powietrza rolls royce", "UTRACONE OKAZJE"),
        ("świece bugatti veyron", "UTRACONE OKAZJE"),
        ("olej aston martin db11", "UTRACONE OKAZJE"),
        ("klocki mclaren 720s", "UTRACONE OKAZJE"),
        ("amortyzator pagani huayra", "UTRACONE OKAZJE"),
        
        # === ZASÓB B - STRUKTURALNE (41-50) ===
        ("klocki xiaomi redmi", "UTRACONE OKAZJE"),
        ("filtr dyson v11", "UTRACONE OKAZJE"),
        ("amortyzator apple macbook", "UTRACONE OKAZJE"),
        ("tarcze samsung galaxy", "UTRACONE OKAZJE"),
        ("drzwi kia sportage", "UTRACONE OKAZJE"),
        ("klapa honda civic", "UTRACONE OKAZJE"),
        ("maska toyota corolla", "UTRACONE OKAZJE"),
        ("zderzak ford focus", "UTRACONE OKAZJE"),
        ("reflektor xenon audi", "UTRACONE OKAZJE"),
        ("opony michelin 17", "UTRACONE OKAZJE"),
        
        # === EDGE CASES (51-60) ===
        ("kloki bosh e90", "ZNALEZIONE PRODUKTY"),
        ("filetr man bmw", "ZNALEZIONE PRODUKTY"),
        ("amortyztor sachs golf", "ZNALEZIONE PRODUKTY"),
        ("swica ngk honda", "ZNALEZIONE PRODUKTY"),
        ("akumlator varta ford", "ZNALEZIONE PRODUKTY"),
        ("ślimak maglownicy audi", "UTRACONE OKAZJE"),
        ("pucharek amortyzatora bmw", "UTRACONE OKAZJE"),
        ("krakownica zawieszenia opel", "UTRACONE OKAZJE"),
        ("czop kulowy mercedes", "UTRACONE OKAZJE"),
        ("kielich sprężyny vw", "UTRACONE OKAZJE"),
        
        # === NONSENS (61-70) ===
        ("qwerty asdf", "ODFILTROWANE"),
        ("asdfgh jklm", "ODFILTROWANE"),
        ("nie wiem co szukam", "ODFILTROWANE"),
        ("pomocy gdzie jest", "ODFILTROWANE"),
        ("jak to działa", "ODFILTROWANE"),
        ("hello klocki world", "ODFILTROWANE"),
        ("pizza hamburger klocki", "ODFILTROWANE"),
        ("klocki do pizzy", "ODFILTROWANE"),
        ("aaaaaa bbbbbb", "ODFILTROWANE"),
        ("123456 789", "ODFILTROWANE"),
        
        # === KAROSERIA (71-80) ===
        ("lusterko ford focus", "UTRACONE OKAZJE"),
        ("zderzak audi a4", "UTRACONE OKAZJE"),
        ("błotnik bmw e90", "UTRACONE OKAZJE"),
        ("klapa bagażnika golf", "UTRACONE OKAZJE"),
        ("próg toyota corolla", "UTRACONE OKAZJE"),
        ("maska volkswagen passat", "UTRACONE OKAZJE"),
        ("reflektor mercedes w204", "UTRACONE OKAZJE"),
        ("lampa stop bmw", "UTRACONE OKAZJE"),
        ("kierunkowskaz audi", "UTRACONE OKAZJE"),
        ("szyba przednia ford", "UTRACONE OKAZJE"),

        # === SKRÓTY I LITERÓWKI (81-90) ===
        ("filtry vw", "UTRACONE OKAZJE"),
        ("kloki mercedes", "ZNALEZIONE PRODUKTY"),
        ("swica bosch", "ZNALEZIONE PRODUKTY"),
        ("olel 5w30", "ZNALEZIONE PRODUKTY"),
        ("opny zimowe", "UTRACONE OKAZJE"),
        ("hamulce mb", "UTRACONE OKAZJE"),
        ("filtry renault", "UTRACONE OKAZJE"),
        ("świece do golfa", "UTRACONE OKAZJE"),
        ("akumulatory varta", "ZNALEZIONE PRODUKTY"),
        ("oleju silnikowego", "UTRACONE OKAZJE"),

        # === NOWE MARKI (91-95) ===
        ("klocki byd tang", "UTRACONE OKAZJE"),
        ("filtr geely coolray", "UTRACONE OKAZJE"),
        ("akumulator nio es8", "UTRACONE OKAZJE"),
        ("opony mg zs", "UTRACONE OKAZJE"),
        ("świeca polestar 2", "UTRACONE OKAZJE"),

        # === SPECJALISTYCZNE (96-100) ===
        ("sworzen wahacza bmw", "UTRACONE OKAZJE"),
        ("tuleja stabilizatora", "UTRACONE OKAZJE"),
        ("czujnik cmp audi", "UTRACONE OKAZJE"),
        ("elektromagnes vanos", "UTRACONE OKAZJE"),
        ("moduł abs mercedes", "UTRACONE OKAZJE"),
        
        # === NOWE BRUTALNE TESTY (101-120) ===
        ("maskotka", "ODFILTROWANE"),                              # NOWY: Brak kontekstu auto
        ("bilet", "ODFILTROWANE"),                                 # NOWY: Brak kontekstu auto
        ("telefon", "ODFILTROWANE"),                               # NOWY: Brak kontekstu auto
        ("jedzenie", "ODFILTROWANE"),                              # NOWY: Brak kontekstu auto
        ("klocki pizza", "ODFILTROWANE"),                          # NOWY: Auto + nonsense
        ("hello klocki", "ODFILTROWANE"),                          # NOWY: English + auto
        ("pizza klocki world", "ODFILTROWANE"),                    # NOWY: Nonsense dominuje
        ("ds", "ODFILTROWANE"),                                    # NOWY: Krótki nonsense
        ("mo", "ODFILTROWANE"),                                    # NOWY: Krótki nonsense
        ("jestem", "ODFILTROWANE"),                                # NOWY: Polski stop word
        ("x", "ODFILTROWANE"),                                     # NOWY: Jeden znak
        ("5w30", "ZNALEZIONE PRODUKTY"),                           # NOWY: Kod techniczny
        ("części xiaomi", "ODFILTROWANE"),                         # NOWY: Elektronika + auto słowo
        ("filtr samsung", "ODFILTROWANE"),                         # NOWY: Auto kategoria + elektronika
        ("klocki apple", "ODFILTROWANE"),                          # NOWY: Auto kategoria + tech
        ("amortyzator do lodówki", "ODFILTROWANE"),                # NOWY: Auto + do + AGD
        ("hamulce nintendo", "ODFILTROWANE"),                      # NOWY: Auto + gaming
        ("123456", "ODFILTROWANE"),                                # NOWY: Same liczby bez kontekstu
        ("abc123", "ODFILTROWANE"),                                # NOWY: Kod bez kontekstu auto
        ("klokihamulcowebmwmercedesaudiklocki", "ODFILTROWANE"),   # NOWY: Sklejone słowa
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
        "SPECJALISTYCZNE (96-100)": (95, 100),
        "BRUTALNE TESTY (101-120)": (100, 120)
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
    print("🎯 RAPORT KOŃCOWY OPERACJI KULOODPORNY RDZEŃ")
    print("=" * 80)
    
    overall_percentage = passed / len(scenarios) * 100
    print(f"\n📈 WYNIK OGÓLNY: {passed}/{len(scenarios)} ({overall_percentage:.1f}%)")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    
    print(f"\n📊 WYNIKI PO GRUPACH:")
    for group_name, (group_passed, group_total) in group_stats.items():
        percentage = group_passed / group_total * 100
        print(f"   • {group_name:30s}: {group_passed:2d}/{group_total:2d} ({percentage:5.1f}%)")
    
    # === OCENA KOŃCOWA ===
    print(f"\n🏆 OCENA KOŃCOWA:")
    if overall_percentage >= 95:
        print("🟢 OPERACJA KULOODPORNY RDZEŃ: PERFEKCJA!")
        print("   System gotowy do produkcji. Wszystkie funkcje działają idealnie.")
    elif overall_percentage >= 90:
        print("🟢 OPERACJA KULOODPORNY RDZEŃ: PEŁNY SUKCES!")
        print("   System gotowy do produkcji z drobnymi poprawkami.")
    elif overall_percentage >= 80:
        print("🟡 OPERACJA KULOODPORNY RDZEŃ: SUKCES Z UWAGAMI")
        print("   System prawie gotowy. Wymaga drobnych dostosowań.")
    else:
        print("🔴 OPERACJA KULOODPORNY RDZEŃ: WYMAGA POPRAWEK")
        print("   System wymaga większych zmian przed wdrożeniem.")
    
    return passed, failed

if __name__ == "__main__":
    print("🚀 ROZPOCZĘCIE NAPRAWIONYCH TESTÓW")
    print("120 scenariuszy: oryginalne + brutalne bez duplikatów...")
    print()
    
    passed, failed = run_comprehensive_tests()
    
    print(f"\n🏁 TESTY ZAKOŃCZONE")
    print(f"Wynik: {passed}/{passed + failed}")
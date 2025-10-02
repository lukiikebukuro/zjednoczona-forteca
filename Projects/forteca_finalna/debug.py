#!/usr/bin/env python3
"""
Test Debug - Uniwersalny Żołnierz (Extended Version)
Testowanie 30 scenariuszy: 20 oryginalnych + 10 zdań bez terminów produktowych
"""

from ecommerce_bot import EcommerceBot

def test_scenario_compact(bot, query, expected_result):
    """Testuje scenariusz i zwraca wynik"""
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
            'suggestion_type': analysis['suggestion_type'],
            'token_validity': analysis['token_validity'],
            'best_match': analysis['best_match_score']
        }
        
    except Exception as e:
        return {
            'passed': False,
            'actual': f'ERROR: {e}',
            'expected': expected_result,
            'confidence': 'ERROR',
            'suggestion_type': 'error',
            'token_validity': 0,
            'best_match': 0
        }

def run_extended_tests():
    """Uruchamia wszystkie testy w kompaktowym formacie - 30 scenariuszy"""
    
    print("🚀 UNIWERSALNY ŻOŁNIERZ - TEST KRYTYCZNYCH SCENARIUSZY (30 TESTÓW)")
    print("=" * 70)
    
    bot = EcommerceBot()
    
    # Wszystkie 30 scenariuszy: 20 oryginalnych + 10 nowych
    scenarios = [
        # KRYTYCZNE (5) - ORYGINALNE
        ("klocki bmw e90", "ZNALEZIONE PRODUKTY", "🔴"),
        ("filtr oleju sony", "UTRACONE OKAZJE", "🔴"),
        ("klocki bmw x1", "UTRACONE OKAZJE", "🔴"),
        ("kloki bosh", "ZNALEZIONE PRODUKTY", "🔴"),
        ("asdasdasd", "ODFILTROWANE", "🔴"),
        
        # WYSOKIE (5) - ORYGINALNE
        ("filtr mann a1", "UTRACONE OKAZJE", "🟡"),
        ("filtr mann 55", "UTRACONE OKAZJE", "🟡"),
        ("klocki ferrari", "UTRACONE OKAZJE", "🟡"),
        ("opony zimowe", "UTRACONE OKAZJE", "🟡"),
        ("filtr mann hu719/7x", "ZNALEZIONE PRODUKTY", "🟡"),
        
        # STANDARDOWE (10) - ORYGINALNE
        ("bmw", "ZNALEZIONE PRODUKTY", "🔵"),
        ("amortyzator", "ZNALEZIONE PRODUKTY", "🔵"),
        ("bmw 1", "UTRACONE OKAZJE", "🔵"),
        ("świeca", "ZNALEZIONE PRODUKTY", "🔵"),
        ("amortyztor bilstein", "ZNALEZIONE PRODUKTY", "🔵"),
        ("olej castrol 5w30", "ZNALEZIONE PRODUKTY", "🔵"),
        ("akumulator vata", "ZNALEZIONE PRODUKTY", "🔵"),
        ("części porsche", "UTRACONE OKAZJE", "🔵"),
        ("xyzxyzxyz", "ODFILTROWANE", "🔵"),
        ("filtr 0986494104", "ZNALEZIONE PRODUKTY", "🔵"),
        
        # NOWE (10) - ZDANIA BEZ TERMINÓW PRODUKTOWYCH - POWINNY BYĆ ODFILTROWANE
        ("nie wiem co pisze blabla", "ODFILTROWANE", "🟣"),
        ("dzisiaj piękna pogoda", "ODFILTROWANE", "🟣"),
        ("kocham pizzę margherita", "ODFILTROWANE", "🟣"),
        ("mam jutro egzamin z matematyki", "ODFILTROWANE", "🟣"),
        ("gdzie jest najbliższy sklep", "ODFILTROWANE", "🟣"),
        ("hello world test example", "ODFILTROWANE", "🟣"),
        ("co słychać u ciebie", "ODFILTROWANE", "🟣"),
        ("jutro idziemy na spacer", "ODFILTROWANE", "🟣"),
        ("random text here nothing", "ODFILTROWANE", "🟣"),
        ("lubię jeść kanapki", "ODFILTROWANE", "🟣")
    ]
    
    results = []
    
    print("CZĘŚĆ 1: ORYGINALNE TESTY (1-20)")
    print("-" * 50)
    
    for i, (query, expected, priority) in enumerate(scenarios[:20], 1):
        result = test_scenario_compact(bot, query, expected)
        results.append((query, priority, result))
        
        # Status kompaktowy
        status = "✅" if result['passed'] else "❌"
        print(f"{priority} {status} {query:25} → {result['actual']:18} (exp: {expected})")
        
        # Dodatkowe info dla failed testów
        if not result['passed']:
            print(f"      Confidence: {result['confidence']}, Match: {result['best_match']:.0f}, Validity: {result['token_validity']:.0f}")
    
    print("\nCZĘŚĆ 2: NOWE TESTY FILTROWANIA (21-30)")
    print("-" * 50)
    print("UWAGA: Te zdania NIE MAJĄ terminów produktowych i powinny być ODFILTROWANE")
    print()
    
    for i, (query, expected, priority) in enumerate(scenarios[20:], 21):
        result = test_scenario_compact(bot, query, expected)
        results.append((query, priority, result))
        
        # Status kompaktowy
        status = "✅" if result['passed'] else "❌"
        print(f"{priority} {status} {query:25} → {result['actual']:18} (exp: {expected})")
        
        # Dodatkowe info dla failed testów
        if not result['passed']:
            print(f"      Confidence: {result['confidence']}, Match: {result['best_match']:.0f}, Validity: {result['token_validity']:.0f}")
            print(f"      Suggestion: {result['suggestion_type']}")
    
    # Podsumowanie wyników
    print("\n" + "=" * 70)
    
    passed = sum(1 for _, _, r in results if r['passed'])
    failed = len(results) - passed
    
    # Podsumowanie po grupach
    original_passed = sum(1 for i in range(20) if results[i][2]['passed'])
    filter_passed = sum(1 for i in range(20, 30) if results[i][2]['passed'])
    
    critical_passed = sum(1 for i in range(5) if results[i][2]['passed'])
    high_passed = sum(1 for i in range(5, 10) if results[i][2]['passed'])
    standard_passed = sum(1 for i in range(10, 20) if results[i][2]['passed'])
    
    print(f"📊 WYNIKI OGÓLNE: {passed}/30 ({passed/30*100:.0f}%)")
    print(f"   • Oryginalne (1-20): {original_passed}/20 ({original_passed/20*100:.0f}%)")
    print(f"   • Filtrowanie (21-30): {filter_passed}/10 ({filter_passed/10*100:.0f}%)")
    print()
    print(f"📈 SZCZEGÓŁY ORYGINALNYCH:")
    print(f"   • Krytyczne: {critical_passed}/5")
    print(f"   • Wysokie: {high_passed}/5") 
    print(f"   • Standard: {standard_passed}/10")
    
    # Analiza błędów filtrowania
    filter_failed = [(q, p, r) for q, p, r in results[20:] if not r['passed']]
    
    if filter_failed:
        print(f"\n⚠️  PROBLEMY Z FILTROWANIEM ({len(filter_failed)}/10):")
        for query, priority, result in filter_failed:
            print(f"   • '{query}' → {result['actual']} (powinno: ODFILTROWANE)")
            print(f"     Validity: {result['token_validity']:.1f}, Confidence: {result['confidence']}")
        
        print(f"\n🔧 DIAGNOZA FILTROWANIA:")
        utracone_count = sum(1 for _, _, r in filter_failed if r['actual'] == 'UTRACONE OKAZJE')
        znalezione_count = sum(1 for _, _, r in filter_failed if r['actual'] == 'ZNALEZIONE PRODUKTY')
        
        if utracone_count > 0:
            print(f"   • {utracone_count} zdań klasyfikowanych jako UTRACONE OKAZJE")
            print("     → Funkcja is_obvious_nonsense() nie działa poprawnie")
            print("     → Sprawdź logikę has_product_term w is_obvious_nonsense()")
        
        if znalezione_count > 0:
            print(f"   • {znalezione_count} zdań klasyfikowanych jako ZNALEZIONE PRODUKTY")
            print("     → Token validity za wysoki lub false positive w matchingu")
    
    # Analiza błędów oryginalnych
    original_failed = [(q, p, r) for q, p, r in results[:20] if not r['passed']]
    
    if original_failed:
        print(f"\n❌ WYMAGAJĄ NAPRAWY - ORYGINALNE ({len(original_failed)}):")
        
        # Grupuj błędy według typu
        error_groups = {}
        for query, priority, result in original_failed:
            key = f"{result['actual']} (zamiast {result['expected']})"
            if key not in error_groups:
                error_groups[key] = []
            error_groups[key].append(f"{priority} {query}")
        
        for error_type, queries in error_groups.items():
            print(f"  • {error_type}:")
            for query in queries[:3]:  # Max 3 przykłady
                print(f"    - {query}")
            if len(queries) > 3:
                print(f"    - ... i {len(queries)-3} więcej")
    
    # Rekomendacje
    print(f"\n🎯 OCENA SYSTEMU:")
    if passed >= 28:
        print("SYSTEM DZIAŁA PERFEKCYJNIE! 🎉")
    elif passed >= 25:
        print("SYSTEM DZIAŁA BARDZO DOBRZE - drobne poprawki 🟢")
    elif original_passed >= 18 and filter_passed >= 7:
        print("PODSTAWY OK - popraw logikę filtrowania 🟡")
    elif filter_passed >= 8:
        print("FILTROWANIE OK - popraw główną logikę 🟠")
    else:
        print("SYSTEM WYMAGA DALSZYCH PRAC 🔴")
    
    # Następne kroki
    print(f"\n🛠️  NASTĘPNE KROKI:")
    if filter_passed < 8:
        print("1. PRIORYTET: Napraw funkcję is_obvious_nonsense()")
        print("   - Sprawdź czy has_product_term działa poprawnie")
        print("   - Upewnij się że brak terminów = ODFILTROWANE")
    
    if original_passed < 18:
        print("2. Popraw główną logikę analyze_query_intent()")
        print("   - Sprawdź progi confidence levels")
        print("   - Popraw detekcję structural queries")
    
    print(f"3. Docelowy wynik: 30/30 (100%)")
    
    return passed, failed

if __name__ == "__main__":
    try:
        passed, failed = run_extended_tests()
        print(f"\n🏁 Koniec testów rozszerzonych. Cel: 30/30")
        
    except ImportError as e:
        print(f"❌ BŁĄD IMPORTU: {e}")
        print("Upewnij się, że plik ecommerce_bot.py jest w tym samym katalogu.")
    except Exception as e:
        print(f"❌ NIEOCZEKIWANY BŁĄD: {e}")
#!/usr/bin/env python3
"""
Test Debug - Uniwersalny Żołnierz (Compact Version)
Szybkie testowanie 20 scenariuszy krytycznych
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

def run_compact_tests():
    """Uruchamia wszystkie testy w kompaktowym formacie"""
    
    print("🚀 UNIWERSALNY ŻOŁNIERZ - TEST KRYTYCZNYCH SCENARIUSZY")
    print("=" * 60)
    
    bot = EcommerceBot()
    
    # Wszystkie 20 scenariuszy
    scenarios = [
        # KRYTYCZNE (5)
        ("klocki bmw e90", "ZNALEZIONE PRODUKTY", "🔴"),
        ("filtr oleju sony", "UTRACONE OKAZJE", "🔴"),
        ("klocki bmw x1", "UTRACONE OKAZJE", "🔴"),
        ("kloki bosh", "ZNALEZIONE PRODUKTY", "🔴"),
        ("asdasdasd", "ODFILTROWANE", "🔴"),
        
        # WYSOKIE (5)
        ("filtr mann a1", "UTRACONE OKAZJE", "🟡"),
        ("filtr mann 55", "UTRACONE OKAZJE", "🟡"),
        ("klocki ferrari", "UTRACONE OKAZJE", "🟡"),
        ("opony zimowe", "UTRACONE OKAZJE", "🟡"),
        ("filtr mann hu719/7x", "ZNALEZIONE PRODUKTY", "🟡"),
        
        # STANDARDOWE (10)
        ("bmw", "ZNALEZIONE PRODUKTY", "🔵"),
        ("amortyzator", "ZNALEZIONE PRODUKTY", "🔵"),
        ("bmw 1", "UTRACONE OKAZJE", "🔵"),
        ("świeca", "ZNALEZIONE PRODUKTY", "🔵"),
        ("amortyztor bilstein", "ZNALEZIONE PRODUKTY", "🔵"),
        ("olej castrol 5w30", "ZNALEZIONE PRODUKTY", "🔵"),
        ("akumulator vata", "ZNALEZIONE PRODUKTY", "🔵"),
        ("części porsche", "UTRACONE OKAZJE", "🔵"),
        ("xyzxyzxyz", "ODFILTROWANE", "🔵"),
        ("filtr 0986494104", "ZNALEZIONE PRODUKTY", "🔵")
    ]
    
    results = []
    
    for i, (query, expected, priority) in enumerate(scenarios, 1):
        result = test_scenario_compact(bot, query, expected)
        results.append((query, priority, result))
        
        # Status kompaktowy
        status = "✅" if result['passed'] else "❌"
        print(f"{priority} {status} {query:20} → {result['actual']:18} (exp: {expected})")
        
        # Dodatkowe info dla failed testów
        if not result['passed']:
            print(f"      Confidence: {result['confidence']}, Match: {result['best_match']:.0f}, Validity: {result['token_validity']:.0f}")
    
    # Podsumowanie wyników
    print("\n" + "=" * 60)
    
    passed = sum(1 for _, _, r in results if r['passed'])
    failed = len(results) - passed
    
    critical_passed = sum(1 for i in range(5) if results[i][2]['passed'])
    high_passed = sum(1 for i in range(5, 10) if results[i][2]['passed'])
    standard_passed = sum(1 for i in range(10, 20) if results[i][2]['passed'])
    
    print(f"📊 WYNIKI: {passed}/20 ({passed/20*100:.0f}%) | "
          f"Krytyczne: {critical_passed}/5 | "
          f"Wysokie: {high_passed}/5 | "
          f"Standard: {standard_passed}/10")
    
    # Analiza błędów
    failed_tests = [(q, p, r) for q, p, r in results if not r['passed']]
    
    if failed_tests:
        print(f"\n❌ WYMAGAJĄ NAPRAWY ({len(failed_tests)}):")
        
        # Grupuj błędy według typu
        error_groups = {}
        for query, priority, result in failed_tests:
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
    print(f"\n🎯 OCENA:")
    if passed >= 18:
        print("GOTOWY DO PRODUKCJI! 🎉")
    elif passed >= 15:
        print("PRAWIE GOTOWY - drobne poprawki wymagane ⚠️")
    elif critical_passed == 5:
        print("PODSTAWY OK - popraw scenariusze wysokiego priorytetu 🔧")
    else:
        print("WYMAGA DALSZYCH PRAC 🛠️")
    
    # Następne kroki
    if failed_tests:
        print(f"\n🔧 NASTĘPNE KROKI:")
        if any("ZNALEZIONE PRODUKTY (zamiast UTRACONE OKAZJE)" in f"{r['actual']} (zamiast {r['expected']})" 
               for _, _, r in failed_tests):
            print("1. Popraw funkcję analyze_query_intent - zbyt niskie progi dla NO_MATCH")
        if any("UTRACONE OKAZJE (zamiast ZNALEZIONE PRODUKTY)" in f"{r['actual']} (zamiast {r['expected']})" 
               for _, _, r in failed_tests):
            print("2. Popraw detekcję literówek - zbyt agresywna klasyfikacja jako structural")
    
    return passed, failed

if __name__ == "__main__":
    try:
        passed, failed = run_compact_tests()
        print(f"\n🏁 Koniec testów. Wyniki zapisane powyżej.")
        
    except ImportError as e:
        print(f"❌ BŁĄD IMPORTU: {e}")
        print("Upewnij się, że plik ecommerce_bot.py jest w tym samym katalogu.")
    except Exception as e:
        print(f"❌ NIEOCZEKIWANY BŁĄD: {e}")
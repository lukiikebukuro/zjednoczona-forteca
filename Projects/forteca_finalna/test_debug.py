from ecommerce_bot import EcommerceBot

bot = EcommerceBot()

# Test case który nie działa
query = "klocki bmw e90"
analysis = bot.analyze_query_intent(query)

print(f"\n=== DEBUGGING '{query}' ===")
print(f"Token validity: {analysis['token_validity']}")
print(f"Best match score: {analysis['best_match_score']}")
print(f"Confidence: {analysis['confidence_level']}")
print(f"Suggestion type: {analysis['suggestion_type']}")
print(f"Is structural: {analysis['is_structural']}")

# Pokaż top 3 matches z wynikami
print(f"\nTop matches:")
for i, (product, score) in enumerate(analysis['matches'][:3]):
    print(f"  {i+1}. {product['name']} (score: {score})")

# Test wewnętrznego matchingu
print(f"\n=== RAW MATCHING ===")
raw_matches = bot.get_fuzzy_product_matches_internal(query)
for product, score in raw_matches[:5]:
    print(f"  {product['name'][:60]} -> {score}")
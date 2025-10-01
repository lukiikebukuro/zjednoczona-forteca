from ecommerce_bot import EcommerceBot
bot = EcommerceBot()

# Test 1
analysis1 = bot.analyze_query_intent("filtr mann a1")
print(f"filtr mann a1: {analysis1['confidence_level']} | {analysis1['suggestion_type']} | validity: {analysis1['token_validity']}")

# Test 2  
analysis2 = bot.analyze_query_intent("klocki bmw e90")
print(f"klocki bmw e90: {analysis2['confidence_level']} | {analysis2['suggestion_type']} | validity: {analysis2['token_validity']} | match: {analysis2['best_match_score']}")
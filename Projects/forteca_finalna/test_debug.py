from ecommerce_bot import EcommerceBot
bot = EcommerceBot()
query = "filtr mann a1"
analysis = bot.analyze_query_intent(query)
print(f"Best match score: {analysis['best_match_score']}")
for i, (product, score) in enumerate(analysis['matches'][:3]):
    print(f"{i+1}. {product['name']} -> {score}")
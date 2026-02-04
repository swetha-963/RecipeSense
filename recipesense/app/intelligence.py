# app/intelligence.py

def normalize_ingredient(name: str) -> str:
    """
    Normalize ingredient names for better matching
    """
    return name.lower().strip().replace("es", "").replace("s", "")


def analyze_recipes(recipes: list, user_ingredients: str) -> list:
    """
    Enhance recipes with intelligence data:
    - matched ingredients count
    - missing ingredients count
    - intelligence score
    """

    user_ingredients_list = [
        normalize_ingredient(i)
        for i in user_ingredients.split(",")
    ]

    enhanced_recipes = []

    for recipe in recipes:
        used = recipe.get("usedIngredients", [])
        missed = recipe.get("missedIngredients", [])

        matched_count = len(used)
        missing_count = len(missed)

        # Base intelligence score
        score = (matched_count * 10) - (missing_count * 5)

        # Bonus if recipe is healthy
        if recipe.get("likes", 0) > 50:
            score += 5

        recipe["matched_count"] = matched_count
        recipe["missing_count"] = missing_count
        recipe["intelligence_score"] = score

        enhanced_recipes.append(recipe)

    # Sort by intelligence score (highest first)
    enhanced_recipes.sort(
        key=lambda r: r.get("intelligence_score", 0),
        reverse=True
    )

    return enhanced_recipes

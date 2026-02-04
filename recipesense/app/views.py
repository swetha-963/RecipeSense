import requests
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Favorite, RecentlyViewed
from requests.exceptions import RequestException


# ==================================================
# CONSTANTS
# ==================================================

SPOONACULAR_BASE = "https://api.spoonacular.com/recipes"


# ==================================================
# HELPERS
# ==================================================




def get_recipes_by_ingredients(ingredients):
    url = f"{SPOONACULAR_BASE}/findByIngredients"
    params = {
        "apiKey": settings.SPOONACULAR_API_KEY,
        "ingredients": ingredients,
        "number": 12,
        "ranking": 1,
        "ignorePantry": True,
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 402:
            return None, "Daily API limit reached. Please try again later."

        response.raise_for_status()
        return response.json(), None

    except Exception:
        return None, "Unable to fetch recipes right now."



def get_recipe_details(recipe_id):
    url = f"{SPOONACULAR_BASE}/{recipe_id}/information"
    params = {
        "apiKey": settings.SPOONACULAR_API_KEY,
        "includeNutrition": True,
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 402:
            return None

        response.raise_for_status()
        return response.json()

    except Exception:
        return None



# ==================================================
# PUBLIC PAGES
# ==================================================

def index(request):
    return render(request, "index.html")


def recipe_detail(request):
    ingredients = request.GET.get("ingredients") or request.session.get("last_ingredients", "")
    recipes = []
    api_error = None

    if ingredients:
        # If same ingredients searched before → use cache
        if request.session.get("last_ingredients") == ingredients:
            recipes = request.session.get("cached_recipes", [])
        else:
            recipes, api_error = get_recipes_by_ingredients(ingredients)

            if recipes:
                request.session["cached_recipes"] = recipes
                request.session["last_ingredients"] = ingredients

    return render(request,"recipe_detail.html", {
        "recipes": recipes,
        "ingredients": ingredients,
        "api_error": api_error,
    })




def single_recipe(request, recipe_id):
    if not request.user.is_authenticated:
        return redirect(f"/signup/?next=/recipe/{recipe_id}/")

    recipe = get_recipe_details(recipe_id)

    if not recipe:
        return redirect("app:recipe_detail")

    RecentlyViewed.objects.get_or_create(
        user=request.user,
        recipe_id=recipe_id,
        defaults={
            "title": recipe.get("title"),
            "image": recipe.get("image"),
        }
    )

    return render(request, "single_recipe.html", {"recipe": recipe})





# ==================================================
# AUTH
# ==================================================

def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            
            # ✅ If no explicit 'next' url, try to restore previous search
            if not next_url:
                last_ingredients = request.session.get("last_ingredients")
                if last_ingredients:
                    return redirect(f"/recipes/?ingredients={last_ingredients}")
            
            return redirect(next_url or "app:recipe_detail")

        return render(request, "login.html", {
            "error": "Invalid email or password",
            "next": next_url
        })

    return render(request, "login.html", {"next": next_url})


def signup(request):
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not name or not email or not password:
            return render(request, "signup.html", {
                "error": "All fields are required",
                "next": next_url
            })

        if User.objects.filter(username=email).exists():
            return render(request, "signup.html", {
                "error": "User already exists",
                "next": next_url
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        login(request, user)
        
        # ✅ Prioritize explicit 'next' destination (e.g. recipe page)
        if next_url:
             return redirect(next_url)

        # ✅ Restore previous search if no specific destination
        last_ingredients = request.session.get("last_ingredients")

        if last_ingredients:
            return redirect(f"/recipes/?ingredients={last_ingredients}")

        return redirect("app:recipe_detail")

    return render(request, "signup.html", {"next": next_url})








def logout_view(request):
    logout(request)
    return redirect("app:index")


# ==================================================
# FAVORITES
# ==================================================

@login_required
def favorites(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, "favorites.html", {"favorites": favorites})


@require_POST
@login_required
def toggle_favorite(request, recipe_id):
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        recipe_id=recipe_id,
        defaults={
            "title": request.POST.get("title"),
            "image": request.POST.get("image"),
            "ready_in_minutes": request.POST.get("time", 0),
        }
    )

    if not created:
        favorite.delete()
        return JsonResponse({"status": "removed"})

    return JsonResponse({"status": "added"})


@require_POST
@login_required
def remove_favorite(request, recipe_id):
    Favorite.objects.filter(
        user=request.user,
        recipe_id=recipe_id
    ).delete()
    return JsonResponse({"success": True})


# ==================================================
# HISTORY
# ==================================================

@login_required
def recently_viewed(request):
    recipes = RecentlyViewed.objects.filter(user=request.user)
    return render(request, "history.html", {"recipes": recipes})


# ==================================================
# CATEGORIES
# ==================================================

def category_recipes(request, category):
    recipes = []
    error = None

    CATEGORY_MAP = {
        "family favourites": "popular",
        "healthy meals": "healthy",
        "quick meals": "quick",
        "budget meals": "cheap",
        "chicken": "chicken",
        "baking": "baking",
        "breakfast": "breakfast",
        "brunch": "brunch",
        "lunch": "lunch",
        "dinner": "dinner",
        "dessert": "dessert",
    }

    query = CATEGORY_MAP.get(category.lower(), category)

    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        "query": query,
        "number": 20,
        "addRecipeInformation": True,
        "apiKey": settings.SPOONACULAR_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        recipes = data.get("results", [])

    except Exception:
        error = "⚠️ Recipe service unavailable. Please try again later."

    return render(request, "category_recipes.html", {
        "recipes": recipes,
        "category": category,
        "error": error
    })



# ==================================================
# OFFLINE
# ==================================================

def offline(request):
    return render(request, "offline.html")

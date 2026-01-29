from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
import requests
from django.http import JsonResponse
from .models import Favorite
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import RecentlyViewed



# ---------------- HOME ----------------
@login_required(login_url='/login/')
def index(request):
    return render(request, 'index.html')


# ---------------- SIGNUP ----------------
def signup_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=email).exists():
            return render(request, 'signup.html', {'error': 'User already exists'})

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        user.first_name = name
        user.save()

        login(request, user)
        return redirect('app:index')

    return render(request, 'signup.html')


# ---------------- LOGIN ----------------
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            return redirect('app:index')

        return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    return redirect('app:login')


# ---------------- RECIPE SEARCH / LIST ----------------
@login_required(login_url="/login/")
def recipe_detail(request):
    ingredients = request.GET.get("ingredients", "").strip()
    recipes = []

    if ingredients:
        url = "https://api.spoonacular.com/recipes/findByIngredients"
        params = {
            "apiKey": settings.SPOONACULAR_API_KEY,
            "ingredients": ingredients,
            "number": 12,
            "ranking": 1,
            "ignorePantry": "true",
        }

        response = requests.get(url, params=params)

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        if response.status_code == 200:
            recipes = response.json()

    return render(request, "recipe_detail.html", {
        "recipes": recipes,
        "ingredients": ingredients,
    })





# ---------------- SINGLE RECIPE ----------------
@login_required
def single_recipe(request, recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {
        "apiKey": settings.SPOONACULAR_API_KEY,
        "includeNutrition": True
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return render(request, "single_recipe.html", {
            "error": "Unable to load recipe"
        })

    recipe = response.json()

    # 🔥 SAVE TO RECENTLY VIEWED
    RecentlyViewed.objects.filter(
        user=request.user,
        recipe_id=recipe["id"],
        # title=recipe["title"],
        # image=recipe["image"]
    )   .delete()

    RecentlyViewed.objects.create(
        user=request.user,
        recipe_id=recipe["id"],
        title=recipe["title"],
        image=recipe["image"]
    )

    return render(request, "single_recipe.html", {"recipe": recipe})




@login_required
@require_POST
def toggle_favorite(request):
    recipe_id = request.POST.get("recipe_id")
    title = request.POST.get("title")
    image = request.POST.get("image")
    time = request.POST.get("time")

    fav, created = Favorite.objects.get_or_create(
        user=request.user,
        recipe_id=recipe_id,
        defaults={
            "title": title,
            "image": image,
            "ready_in_minutes": time
        }
    )

    if not created:
        fav.delete()
        return JsonResponse({"status": "removed"})

    return JsonResponse({"status": "added"})




@login_required
def favorites(request):
    items = Favorite.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "favorites.html", {"favorites": items})



@login_required
def recently_viewed(request):
    recipes = RecentlyViewed.objects.filter(
        user=request.user
    ).order_by("-viewed_at")[:10]

    return render(request, "history.html", {
        "recipes": recipes
    })

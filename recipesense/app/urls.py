from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path("", views.index, name="index"),
    path("recipes/", views.recipe_detail, name="recipe_detail"),
    path("recipe/<int:recipe_id>/", views.single_recipe, name="single_recipe"),

    # CATEGORY ROUTE
    path("category/<str:category>/", views.category_recipes, name="category_recipes"),

    path("favorites/", views.favorites, name="favorites"),
    path("favorites/toggle/<int:recipe_id>/", views.toggle_favorite, name="toggle_favorite"),

    path("recent/", views.recently_viewed, name="recently_viewed"),

    # ✅ NEW CATEGORY PAGE
    path("category/<str:category>/", views.category_recipes, name="category_recipes"),

    path("login/", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),

]

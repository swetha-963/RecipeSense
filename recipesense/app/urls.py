from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path("", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("index/", views.index, name="index"),

    path("recipes/", views.recipe_detail, name="recipe_detail"),
    path("recipe/<int:recipe_id>/", views.single_recipe, name="single_recipe"),
    path("favorites/", views.favorites, name="favorites"),
    path("toggle-favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("recent/", views.recently_viewed, name="recently_viewed"),

]

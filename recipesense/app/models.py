from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Recipe(models.Model):
    title = models.CharField(max_length=200)
    ingredients = models.TextField()  # comma-separated
    instructions = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    diet = models.CharField(max_length=50, blank=True, null=True)
    gluten_free = models.BooleanField(default=False)
    vegan = models.BooleanField(default=False)
    vegetarian = models.BooleanField(default=False)
    ready_in_minutes = models.IntegerField(default=0)
    servings = models.IntegerField(default=1)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.title
    




class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe_id = models.IntegerField()
    title = models.CharField(max_length=255)
    image = models.URLField()
    ready_in_minutes = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "recipe_id")

    def __str__(self):
        return f"{self.user.username} - {self.title}"
    


class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe_id = models.IntegerField()
    title = models.CharField(max_length=255)
    image = models.URLField()
    viewed_at = models.DateTimeField(auto_now_add=True)


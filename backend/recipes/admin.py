from django.contrib import admin

from .models import Ingredient, IngredientInRecipe, Tag

admin.site.register(Ingredient)
admin.site.register(IngredientInRecipe)
admin.site.register(Tag)

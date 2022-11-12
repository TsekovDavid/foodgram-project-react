from django.contrib import admin

from .models import Ingredient, IngredientInRecipe, Recipe, ShoppingList, Tag

# from django.contrib.auth.models import Group
# from rest_framework.authtoken.models import TokenProxy

# admin.site.unregister(Group)
# admin.site.unregister(TokenProxy)

admin.site.register(Ingredient)
admin.site.register(IngredientInRecipe)
admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(ShoppingList)

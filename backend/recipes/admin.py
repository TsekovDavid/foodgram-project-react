from django.contrib import admin
from django.db import models

from .models import (Favourites, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingList, Tag)


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'ingredient')
    inlines = [
        IngredientInline,
    ]

    def ingredient(self, obj):
        return (', '.join([str(ingredient).split(',')[0]
                for ingredient in obj.ingredients.all()]))


@admin.register(ShoppingList)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


@admin.register(IngredientInRecipe)
class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')


@admin.register(Favourites)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')

from django.contrib import admin
from django.db import models

from .models import (Favourites, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingList, Tag)


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe


# class TagInline(admin.StackedInline):
#     model = Tag


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
        # TagInline,
    ]

    def ingredient(self, obj):
        ingredients = obj.ingredients.all()
        ing = []
        ing.append(
            [str(ingredient).split(',')[0] for ingredient in ingredients]
        )
        return ing[0]

@admin.register(ShoppingList)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


@admin.register(IngredientInRecipe)
class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')


@admin.register(Favourites)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')

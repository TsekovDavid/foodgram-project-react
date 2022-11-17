from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favourites, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingList, Tag)
from users.models import Follow, User


class UsersSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj: User):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')

    def to_representation(self, instance):
        data = IngredientSerializer(instance.ingredient).data
        data['amount'] = instance.amount
        return data


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    author = UsersSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favourites.objects.filter(
            user=user, recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=user, recipe__id=obj.id).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True, max_length=None)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UsersSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredients_in_recipe',
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favourites.objects.filter(
            user=user, recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=user, recipe__id=obj.id).exists()

    def create_ingredients(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])

    def validate(self, data):
        ingredients = data.get('ingredients_in_recipe')
        if not ingredients:
            raise serializers.ValidationError('Добавьте ингредиенты в рецепт')
        ingredients_list = []
        for ingredient in ingredients:
            amount = ingredient['amount']
            if amount <= 0:
                raise serializers.ValidationError(
                    'Количество должно быть больше 0'
                )
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться'
                )
            ingredients_list.append(ingredient)
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError('Добавьте тег')
        if data['cooking_time'] <= 0:
            raise serializers.ValidationError(
                'Минимальное время приготовления 1 мин'
            )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients_in_recipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients_in_recipe')
        instance.tags.set(tags)
        self.create_ingredients(
            ingredients=ingredients,
            recipe=instance
        )
        return super().update(instance=instance, validated_data=validated_data)


class RecipeSubscribesSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UserSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeSubscribesSerializer(queryset, many=True).data


class FavouriteSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Tag, Ingredient, IngredientInRecipe, Recipe, Favourites, ShoppingList
from users.models import User, Follow
from users.validators import validate_username


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
    ingredients = IngredientInRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredientinrecipe_set'
    )
    author = UsersSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

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


# class CreateIngredientRecipeSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(
#         source='ingredient',
#         queryset=Ingredient.objects.all()
#     )

#     class Meta:
#         model = IngredientInRecipe
#         fields = ('id', 'amount')

#     def validate_amount(self, data):
#         if int(data) < 1:
#             raise serializers.ValidationError({
#                 'ingredients': ('Минимальное количество: 1'),
#                 'msg': data
#             })
#         return data

#     def create(self, validated_data):
#         return IngredientInRecipe.objects.create(
#             ingredient=validated_data.get('id'),
#             amount=validated_data.get('amount')
#         )


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True, max_length=None)
    author = UsersSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set',
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    cooking_time = serializers.IntegerField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags', 'image', 'author',
            'name', 'text', 'cooking_time', 'is_favorited',
            'is_in_shopping_cart'
        )

    # def create_ingredients(self, recipe, ingredients):
    #     IngredientInRecipe.objects.bulk_create([
    #         IngredientInRecipe(
    #             recipe=recipe,
    #             amount=ingredient['amount'],
    #             ingredient=ingredient['ingredient'],
    #         ) for ingredient in ingredients
    #     ])

    # def validate(self, data):
    #     ingredients = self.initial_data.get('ingredients')
    #     ingredients_list = []
    #     for ingredient in ingredients:
    #         ingredient_id = ingredient['id']
    #         if ingredient_id in ingredients_list:
    #             raise serializers.ValidationError(
    #                 'Ингредиенты не должны повторяться'
    #             )
    #         ingredients_list.append(ingredient_id)
    #     if data['cooking_time'] <= 0:
    #         raise serializers.ValidationError(
    #             'Минимальное время приготовления 1 мин'
    #         )
    #     return data

    # def create(self, validated_data):
    #     request = self.context.get('request')
    #     ingredients = validated_data.pop('ingredients')
    #     tags = validated_data.pop('tags')
    #     recipe = Recipe.objects.create(
    #         author=request.user,
    #         **validated_data
    #     )
    #     self.create_ingredients(recipe, ingredients)
    #     recipe.tags.set(tags)
    #     return recipe

    # def update(self, instance, validated_data):
    #     ingredients = validated_data.pop('ingredients')
    #     recipe = instance
    #     IngredientInRecipe.objects.filter(recipe=recipe).delete()
    #     self.create_ingredients(recipe, ingredients)
    #     return super().update(recipe, validated_data)

    # def to_representation(self, instance):
    #     return RecipeSerializer(
    #         instance,
    #         context={'request': self.context.get('request')}
    #     ).data




# class CreateRecipeSerializer(serializers.ModelSerializer):
#     '''Сериализатор создания рецепта'''
#     author = UsersSerializer(read_only=True)
#     ingredients = serializers.SerializerMethodField()
#     tags = serializers.PrimaryKeyRelatedField(
#         query_set=Tag.objects.all(),
#         many=True
#     )
#     image = Base64ImageField(use_url=True, max_length=None)

#     class Meta:
#         model = Recipe
#         fields = ('id', 'tags', 'author', 'ingredients', 'name', 'text',
#                   'cooking_time', 'image')

    # def create(self, validated_data):
    #     request = self.context.get('request')
    #     tags = validated_data.pop('tags')
    #     recipe = Recipe.objects.create(author=request.user, **validated_data)
    #     recipe.tags.set('tags')
    #     ingredients_set = request.data['ingredients']
    #     for ingredient in ingredients_set:
    #         try:
    #             ingredient_model = Ingredient.objects.get(id=ingredient['id'])
    #             amount = ingredient['amount']
    #         except KeyError:
    #             raise serializers.ValidationError(
    #                 'Добавьте ингредиенты в рецепт'
    #             )
    #         except Ingredient.DoesNotExist:
    #             raise serializers.ValidationError(
    #                 'Рецепта с таким id нет'
    #             )
    #         if amount and int(amount) > 0:
    #             IngredientInRecipe.objects.create(
    #                 recipe=recipe,
    #                 ingredients=ingredient_model,
    #                 amount=amount
    #             )
    #         else:
    #             raise serializers.ValidationError(
    #                 'Не указано количество ингредиента'
    #             )
    #     recipe.save()
    #     return recipe
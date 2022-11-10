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
        source='ingredients'
    )
    author = UsersSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)


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
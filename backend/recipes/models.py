from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        db_index=True
    )
    color = ColorField(
        format='hex',
        verbose_name='Цвет в HEX'
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Уникальный слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug[:20]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Ингредиент',
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты для рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги'
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipes/media/',
        blank=True
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1, 'Минимальное время приготовления 1 минута')
        ],
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    is_favorited = models.BooleanField('В избранном', default=False)
    is_in_shopping_cart = models.BooleanField(
        'В списке покупок',
        default=False
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:50]


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиенты для рецепта',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Название рецепта',
        related_name='recipe_ingredients',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1, 'Количество не может быть меньше 1')],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.recipe}: {self.ingredient}-{self.amount}'[:100]


class Favourites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites'
    )

    class Meta:
        verbose_name = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourites'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shopping_list'
            )
        ]

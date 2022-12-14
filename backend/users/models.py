from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    """Модель пользователя"""
    username = models.CharField(
        max_length=settings.MAX_LEN_USERS_CHARFIELD,
        unique=True,
        validators=[validate_username],
        verbose_name='Уникальный юзернейм'
    )
    first_name = models.CharField(
        max_length=settings.MAX_LEN_USERS_CHARFIELD,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=settings.MAX_LEN_USERS_CHARFIELD,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        verbose_name='Почта',
        unique=True,
        max_length=settings.MAX_LEN_EMAIL_FIELD
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'], name='unique_together'
            )
        ]

    def __str__(self):
        return self.username[:20]


class Follow(models.Model):
    """Модель подписок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецепта',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='Нельзя подписаться на самого себя'
            )
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}.'

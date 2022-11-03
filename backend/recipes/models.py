from colorfield.fields import ColorField
from django.db import models


class Tag(models.Model):
    COLOR_PALETTE = [
        ("#FFFFFF", "white", ),
        ("#000000", "black", ),
    ]
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

# slug	
# string or null <= 200 characters ^[-a-zA-Z0-9_]+$
# Уникальный слаг
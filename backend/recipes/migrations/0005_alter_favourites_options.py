# Generated by Django 3.2.14 on 2022-11-15 22:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20221115_1837'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favourites',
            options={'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранное'},
        ),
    ]

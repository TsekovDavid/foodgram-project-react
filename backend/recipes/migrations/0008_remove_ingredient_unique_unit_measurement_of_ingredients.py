# Generated by Django 3.2.14 on 2022-11-17 18:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20221117_2114'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ingredient',
            name='unique_unit_measurement_of_ingredients',
        ),
    ]
# Generated by Django 4.1.3 on 2022-11-05 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_followers_alter_follow_author_alter_follow_user_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='user!=author',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(('user', models.F('author')), _negated=True), name='Нельзя подписаться на самого себя'),
        ),
    ]
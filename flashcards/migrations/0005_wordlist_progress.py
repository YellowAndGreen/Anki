# Generated by Django 3.0.4 on 2022-01-25 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flashcards', '0004_wordlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='wordlist',
            name='progress',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
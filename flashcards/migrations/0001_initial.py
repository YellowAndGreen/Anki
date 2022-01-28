# Generated by Django 3.0.4 on 2022-01-07 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cid', models.PositiveIntegerField(db_index=True, unique=True)),
                ('group', models.CharField(max_length=20)),
                ('question', models.CharField(default='none', max_length=200)),
                ('answer', models.CharField(default='none', max_length=200)),
                ('example', models.CharField(max_length=200)),
                ('translation', models.CharField(max_length=200)),
                ('extra', models.CharField(max_length=200)),
            ],
        ),
    ]

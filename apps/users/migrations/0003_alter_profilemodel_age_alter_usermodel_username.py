# Generated by Django 5.1 on 2025-03-18 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_usermodel_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilemodel',
            name='age',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='usermodel',
            name='username',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]

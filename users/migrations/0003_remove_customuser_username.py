# Generated by Django 5.0.6 on 2024-06-20 11:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_customuser_username"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customuser",
            name="username",
        ),
    ]
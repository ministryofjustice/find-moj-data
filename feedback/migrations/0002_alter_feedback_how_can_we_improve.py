# Generated by Django 5.1 on 2024-08-21 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("feedback", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feedback",
            name="how_can_we_improve",
            field=models.TextField(
                blank=True, verbose_name="How can we improve this service?"
            ),
        ),
    ]

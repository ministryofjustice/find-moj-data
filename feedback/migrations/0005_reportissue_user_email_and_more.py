# Generated by Django 5.1.2 on 2024-10-16 13:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("feedback", "0004_reportissue_additional_info_alter_reportissue_reason"),
    ]

    operations = [
        migrations.AddField(
            model_name="reportissue",
            name="user_email",
            field=models.CharField(
                blank=True,
                max_length=250,
                null=True,
                validators=[django.core.validators.EmailValidator()],
            ),
        ),
        migrations.AlterField(
            model_name="reportissue",
            name="additional_info",
            field=models.TextField(
                blank=True, null=True, verbose_name="Can you provide more detail?"
            ),
        ),
    ]

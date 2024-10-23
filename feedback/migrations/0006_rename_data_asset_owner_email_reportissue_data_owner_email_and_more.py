# Generated by Django 5.1.2 on 2024-10-16 13:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("feedback", "0005_reportissue_user_email_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="reportissue",
            old_name="data_asset_owner_email",
            new_name="data_owner_email",
        ),
        migrations.RenameField(
            model_name="reportissue",
            old_name="data_asset_name",
            new_name="entity_name",
        ),
        migrations.RenameField(
            model_name="reportissue",
            old_name="data_asset_url",
            new_name="entity_url",
        ),
    ]

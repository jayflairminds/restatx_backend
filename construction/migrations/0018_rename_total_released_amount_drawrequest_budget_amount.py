# Generated by Django 5.0.6 on 2024-09-05 03:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("construction", "0017_drawrequest_total_released_amount"),
    ]

    operations = [
        migrations.RenameField(
            model_name="drawrequest",
            old_name="total_released_amount",
            new_name="budget_amount",
        ),
    ]
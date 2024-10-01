# Generated by Django 5.0.6 on 2024-10-01 10:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alerts", "0002_remove_notification_user_notification_notify_to_and_more"),
        ("construction", "0027_alter_budgetmaster_acquisition_loan_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="loan",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="construction.loan",
            ),
        ),
    ]
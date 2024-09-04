# Generated by Django 5.0.6 on 2024-09-03 11:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("construction", "0015_alter_loan_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="DrawRequest",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("draw_request", models.IntegerField()),
                (
                    "released_amount",
                    models.DecimalField(decimal_places=3, max_digits=30, null=True),
                ),
                (
                    "funded_amount",
                    models.DecimalField(decimal_places=3, max_digits=30, null=True),
                ),
                (
                    "balance_amount",
                    models.DecimalField(decimal_places=3, max_digits=30, null=True),
                ),
                (
                    "draw_amount",
                    models.DecimalField(decimal_places=3, max_digits=30, null=True),
                ),
                ("description", models.CharField(max_length=200, null=True)),
                ("invoice", models.CharField(max_length=100, null=True)),
                ("requested_date", models.DateTimeField(blank=True, null=True)),
                ("disbursement_date", models.DateTimeField(blank=True, null=True)),
                ("disbursement_status", models.CharField(max_length=200)),
                (
                    "budget_master",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="construction.budgetmaster",
                    ),
                ),
            ],
        ),
    ]

# Generated by Django 5.0.6 on 2024-08-08 11:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("construction", "0013_alter_budgetmaster_uses"),
    ]

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("document_name", models.CharField(max_length=255)),
                ("document_type", models.CharField(max_length=150)),
                ("file_id", models.CharField(max_length=255)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "loan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="construction.loan",
                    ),
                ),
            ],
        ),
    ]
# Generated by Django 5.0.6 on 2024-08-21 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("document_management", "0003_document_document_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="status",
            field=models.CharField(default="Not Started", max_length=100, null=True),
        ),
    ]
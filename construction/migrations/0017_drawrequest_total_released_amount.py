# Generated by Django 5.0.6 on 2024-09-04 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("construction", "0016_drawrequest"),
    ]

    operations = [
        migrations.AddField(
            model_name="drawrequest",
            name="total_released_amount",
            field=models.DecimalField(decimal_places=3, max_digits=30, null=True),
        ),
    ]

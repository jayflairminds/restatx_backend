# Generated by Django 5.0.6 on 2024-09-12 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "construction",
            "0019_rename_date_approved_drawtracking_disbursement_date_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="budgetmaster",
            name="adjustments",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="budgetmaster",
            name="equity_budget",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="budgetmaster",
            name="revised_budget",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
# Generated by Django 5.0.6 on 2024-08-01 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("construction", "0010_alter_budgetmaster_acquisition_loan_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="budgetmaster",
            name="project_total",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

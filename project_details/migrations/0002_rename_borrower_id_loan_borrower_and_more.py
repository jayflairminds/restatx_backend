# Generated by Django 5.0.6 on 2024-07-11 13:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_details', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='loan',
            old_name='borrower_id',
            new_name='borrower',
        ),
        migrations.RenameField(
            model_name='loan',
            old_name='inspector_id',
            new_name='inspector',
        ),
        migrations.RenameField(
            model_name='loan',
            old_name='lender_id',
            new_name='lender',
        ),
        migrations.RenameField(
            model_name='loan',
            old_name='project_id',
            new_name='project',
        ),
    ]

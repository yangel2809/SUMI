# Generated by Django 4.2.13 on 2024-08-27 14:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_alter_historicalclient_rif_num'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='rif_num',
            field=models.CharField(max_length=10, null=True, validators=[django.core.validators.RegexValidator('^[0-9]{8}+-[0-9]+$')]),
        ),
    ]

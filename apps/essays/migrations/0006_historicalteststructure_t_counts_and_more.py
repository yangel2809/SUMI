# Generated by Django 4.2.13 on 2024-07-24 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('essays', '0005_remove_historicallaminatorboot_check_crown_treatment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalteststructure',
            name='t_counts',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='historicalteststructure',
            name='w_counts',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='teststructure',
            name='t_counts',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='teststructure',
            name='w_counts',
            field=models.BooleanField(default=True),
        ),
    ]

# Generated by Django 4.2.13 on 2024-09-16 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('essays', '0009_alter_testrequest_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalprinterboot',
            name='photocell_side',
            field=models.CharField(blank=True, choices=[('l', 'Fotocelda lado izquierdo'), ('r', 'Fotocelda lado derecho')], max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='printerboot',
            name='photocell_side',
            field=models.CharField(blank=True, choices=[('l', 'Fotocelda lado izquierdo'), ('r', 'Fotocelda lado derecho')], max_length=1, null=True),
        ),
    ]

# Generated by Django 3.2.25 on 2024-10-21 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('depaul_market', '0009_alter_products_made_available'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='introduction',
            field=models.TextField(blank=True, null=True),
        ),
    ]
# Generated by Django 3.2.25 on 2024-11-10 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('depaul_market', '0012_products_associated_classes'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='is_senior_firesale',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 4.1.1 on 2022-09-15 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_service', '0002_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='amount',
            field=models.IntegerField(default=0),
        ),
    ]

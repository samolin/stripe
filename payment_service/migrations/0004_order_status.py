# Generated by Django 4.1.1 on 2022-09-15 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_service', '0003_alter_order_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(default='in_process', max_length=30),
        ),
    ]

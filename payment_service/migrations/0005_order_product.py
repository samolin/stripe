# Generated by Django 4.1.1 on 2022-09-15 14:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment_service', '0004_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order_Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payment_service.order')),
                ('item_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payment_service.item')),
            ],
        ),
    ]
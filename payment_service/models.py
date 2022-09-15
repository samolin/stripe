from pydoc import describe
from pyexpat import model
from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=255)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_price(self):
        return "{0:.2f}".format(self.price / 100)

class Order(models.Model):
    id = models.BigAutoField(primary_key=True)
    status = models.CharField(max_length=30, default='in_process')

    def __str__(self):
        return str(self.id)

class Order_Product(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='item')
    cart_id = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='order')

    def __str__(self):
        return str(self.item_id)
    
    

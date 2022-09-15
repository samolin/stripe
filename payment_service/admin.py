from django.contrib import admin
from .models import Item, Order, Order_Product


#admin.site.register(Order_Product)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id']

@admin.register(Order_Product)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'item_id']



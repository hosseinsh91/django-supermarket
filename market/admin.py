from django.contrib import admin

from market.models import Product, Order, OrderRow

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderRow)



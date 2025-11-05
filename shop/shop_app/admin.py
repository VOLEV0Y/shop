from django.contrib import admin
from .models import *

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'price', 'category', 'gender']
    list_filter = ['category', 'gender']
    search_fields = ['name']

@admin.register(SizeProduct)
class SizeProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'quantity']
    list_filter = ['size']

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Size)
admin.site.register(Address)
admin.site.register(PaymentMethod)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
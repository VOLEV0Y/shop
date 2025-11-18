from django.contrib import admin
from .models import *

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Size)
admin.site.register(Address)
admin.site.register(PaymentMethod)
admin.site.register(Product)
admin.site.register(SizeProduct)
admin.site.register(Cart)
admin.site.register(CartItem)